"""Main service for the prompt-to-bot functionality."""

import os
from typing import Optional

import structlog
from sanic import HTTPResponse, Sanic, response
from sanic.request import Request

from rasa.builder import config
from rasa.builder.exceptions import (
    LLMGenerationError,
    ProjectGenerationError,
    TrainingError,
    ValidationError,
)
from rasa.builder.llm_service import llm_service
from rasa.builder.logging_utils import get_recent_logs
from rasa.builder.models import (
    ApiErrorResponse,
    ApiResponse,
    LLMBuilderContext,
    LLMBuilderRequest,
    PromptRequest,
    ServerSentEvent,
    TemplateRequest,
)
from rasa.builder.project_generator import ProjectGenerator
from rasa.builder.training_service import train_and_load_agent
from rasa.builder.validation_service import validate_project
from rasa.cli.scaffold import ProjectTemplateName
from rasa.core.channels.studio_chat import StudioChatInput
from rasa.server import configure_cors
from rasa.shared.core.trackers import DialogueStateTracker

structlogger = structlog.get_logger()


class BotBuilderService:
    """Main service for bot building functionality."""

    def __init__(self, project_folder: Optional[str] = None):
        """Initialize the service with a project folder for file persistence.

        Args:
            project_folder: Path to the folder where project files will be stored.
                           If None, defaults to a temporary directory.
        """
        if project_folder is None:
            import tempfile

            project_folder = tempfile.mkdtemp(prefix="rasa_builder_")

        # working directory needs to be the project folder, e.g.
        # for relative paths (./docs) in a projects config to work
        os.chdir(project_folder)

        structlogger.info(
            "bot_builder_service.service_initialized", project_folder=project_folder
        )

        self.project_generator = ProjectGenerator(project_folder)
        self.app = Sanic("BotBuilderService")
        self.app.config.REQUEST_TIMEOUT = 60  # 1 minute timeout
        self.app.ctx.agent = None
        self.input_channel = self.setup_input_channel()
        self.setup_routes()
        self.setup_middleware()

        configure_cors(self.app, cors_origins=config.CORS_ORIGINS)

    def setup_input_channel(self) -> StudioChatInput:
        """Setup the input channel for chat interactions."""
        studio_chat_credentials = config.get_default_credentials().get(
            StudioChatInput.name()
        )
        return StudioChatInput.from_credentials(credentials=studio_chat_credentials)

    def setup_routes(self) -> None:
        """Setup all API routes."""
        # Core endpoints
        self.app.add_route(
            self.handle_prompt_to_bot, "/api/prompt-to-bot", methods=["POST"]
        )
        self.app.add_route(
            self.handle_template_to_bot, "/api/template-to-bot", methods=["POST"]
        )
        self.app.add_route(self.get_bot_data, "/api/bot-data", methods=["GET"])
        self.app.add_route(self.update_bot_data, "/api/bot-data", methods=["PUT"])
        self.app.add_route(self.llm_builder, "/api/llm-builder", methods=["POST"])

        # Health check
        self.app.add_route(self.health, "/", methods=["GET"])

        # Register input channel webhooks
        from rasa.core import channels

        channels.channel.register([self.input_channel], self.app, route="/webhooks/")

    def setup_middleware(self) -> None:
        """Setup middleware for request/response processing."""

        @self.app.middleware("request")  # type: ignore[no-untyped-call]
        async def log_request(request: Request) -> None:
            structlogger.info(
                "request.received",
                method=request.method,
                path=request.path,
                remote_addr=request.remote_addr or "unknown",
            )

        @self.app.middleware("response")  # type: ignore[no-untyped-call]
        async def log_response(request: Request, response: HTTPResponse) -> None:
            structlogger.info(
                "request.completed",
                method=request.method,
                path=request.path,
                status=response.status,
            )

    async def health(self, request: Request) -> HTTPResponse:
        """Health check endpoint."""
        return response.json({"status": "ok", "service": "bot-builder"})

    async def handle_prompt_to_bot(self, request: Request) -> None:
        """Handle prompt-to-bot generation requests."""
        sse_response = await request.respond(content_type="text/event-stream")

        try:
            # 1. Received
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="received", data={"status": "received"}),
            )

            # Validate request
            prompt_data = PromptRequest(**request.json)

            # 2. Generating
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="generating", data={"status": "generating"}),
            )

            try:
                # Generate project with retries
                bot_files = await self.project_generator.generate_project_with_retries(
                    prompt_data.prompt,
                    template=ProjectTemplateName.PLAIN,
                )

                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="generation_success",
                        data={"status": "generation_success"},
                    ),
                )

            except (ProjectGenerationError, LLMGenerationError) as e:
                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="generation_error",
                        data={"status": "generation_error", "error": str(e)},
                    ),
                )
                await sse_response.eof()
                return

            # 3. Training
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="training", data={"status": "training"}),
            )

            try:
                # Train and load agent
                importer = self.project_generator._create_importer()
                self.app.ctx.agent = await train_and_load_agent(importer)

                # Update input channel with new agent
                self.input_channel.agent = self.app.ctx.agent

                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="train_success", data={"status": "train_success"}
                    ),
                )

            except TrainingError as e:
                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="train_error",
                        data={"status": "train_error", "error": str(e)},
                    ),
                )
                await sse_response.eof()
                return

            # 4. Done
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="done",
                    data={
                        "status": "done",
                    },
                ),
            )

            structlogger.info(
                "bot_builder_service.prompt_to_bot.success",
                client_id=prompt_data.client_id,
                files_generated=list(bot_files.keys()),
            )

        except ValidationError as e:
            structlogger.error(
                "bot_builder_service.prompt_to_bot.validation_error", error=str(e)
            )
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="validation_error",
                    data={"status": "validation_error", "error": str(e)},
                ),
            )

        except Exception as e:
            structlogger.error(
                "bot_builder_service.prompt_to_bot.unexpected_error", error=str(e)
            )
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="error", data={"status": "error", "error": str(e)}
                ),
            )
        finally:
            await sse_response.eof()

    async def handle_template_to_bot(self, request: Request) -> None:
        """Handle template-to-bot generation requests."""
        sse_response = await request.respond(content_type="text/event-stream")

        try:
            # 1. Received
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="received", data={"status": "received"}),
            )

            # Validate request
            template_data = TemplateRequest(**request.json)

            # 2. Generating
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="generating", data={"status": "generating"}),
            )

            try:
                # Generate project with retries
                self.project_generator.init_from_template(
                    template_data.template_name,
                )
                bot_files = self.project_generator.get_bot_files()

                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="generation_success",
                        data={"status": "generation_success"},
                    ),
                )

            except ProjectGenerationError as e:
                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="generation_error",
                        data={"status": "generation_error", "error": str(e)},
                    ),
                )
                await sse_response.eof()
                return

            # 3. Training
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="training", data={"status": "training"}),
            )

            try:
                # Train and load agent
                importer = self.project_generator._create_importer()
                self.app.ctx.agent = await train_and_load_agent(importer)

                # Update input channel with new agent
                self.input_channel.agent = self.app.ctx.agent

                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="train_success", data={"status": "train_success"}
                    ),
                )

            except TrainingError as e:
                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="train_error",
                        data={"status": "train_error", "error": str(e)},
                    ),
                )
                await sse_response.eof()
                return

            # 4. Done
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="done",
                    data={
                        "status": "done",
                    },
                ),
            )

            structlogger.info(
                "bot_builder_service.template_to_bot.success",
                client_id=template_data.client_id,
                files_generated=list(bot_files.keys()),
            )

        except ValidationError as e:
            structlogger.error(
                "bot_builder_service.template_to_bot.validation_error", error=str(e)
            )
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="validation_error",
                    data={"status": "validation_error", "error": str(e)},
                ),
            )

        except Exception as e:
            structlogger.error(
                "bot_builder_service.template_to_bot.unexpected_error", error=str(e)
            )
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="error", data={"status": "error", "error": str(e)}
                ),
            )
        finally:
            await sse_response.eof()

    async def get_bot_data(self, request: Request) -> HTTPResponse:
        """Get current bot data."""
        bot_files = self.project_generator.get_bot_files()
        return response.json(
            ApiResponse(
                status="success",
                message="Bot data fetched successfully",
                data={"bot_data": bot_files},
            ).model_dump()
        )

    async def update_bot_data(self, request: Request) -> None:
        """Update bot data with server-sent events for progress tracking."""
        sse_response = await request.respond(content_type="text/event-stream")

        try:
            # 1. Received
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="received", data={"status": "received"}),
            )

            # Update bot files
            bot_data = request.json
            self.project_generator.update_bot_files(bot_data)

            # 2. Validating
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="validating", data={"status": "validating"}),
            )

            try:
                importer = self.project_generator._create_importer()
                validation_error = await validate_project(importer)

                if validation_error:
                    raise ValidationError(validation_error)

                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="validation_success",
                        data={"status": "validation_success"},
                    ),
                )

            except ValidationError as e:
                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="validation_error",
                        data={"status": "validation_error", "error": str(e)},
                    ),
                )
                await sse_response.eof()
                return

            # 3. Training
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(event="training", data={"status": "training"}),
            )

            try:
                self.app.ctx.agent = await train_and_load_agent(importer)
                self.input_channel.agent = self.app.ctx.agent

                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="train_success", data={"status": "train_success"}
                    ),
                )

            except TrainingError as e:
                await self._send_sse_event(
                    sse_response,
                    ServerSentEvent(
                        event="train_error",
                        data={"status": "train_error", "error": str(e)},
                    ),
                )
                await sse_response.eof()
                return

            # 4. Done
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="done",
                    data={
                        "status": "done",
                        "bot_data": self.project_generator.get_bot_files(),
                    },
                ),
            )

        except Exception as e:
            await self._send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="error", data={"status": "error", "error": str(e)}
                ),
            )
        finally:
            await sse_response.eof()

    async def llm_builder(self, request: Request) -> HTTPResponse:
        """Handle LLM builder requests."""
        try:
            # Validate request
            builder_request = LLMBuilderRequest(**request.json)

            # Get current conversation context
            current_tracker = await self.current_tracker_from_input_channel()
            bot_logs = get_recent_logs()
            chat_bot_files = self.project_generator.get_bot_files()

            # create LLM builder context
            llm_builder_context = LLMBuilderContext(
                tracker=current_tracker,
                bot_logs=bot_logs,
                chat_bot_files=chat_bot_files,
                chat_history=builder_request.messages,
            )

            # Generate response
            messages = await llm_service.create_helper_messages(llm_builder_context)
            llm_response = await llm_service.generate_helper_response(messages)

            return response.json(llm_response)

        except LLMGenerationError as e:
            structlogger.error(
                "bot_builder_service.llm_builder.generation_error", error=str(e)
            )
            return response.json(
                ApiErrorResponse(
                    error="LLM helper generation failed", details={"llm_error": str(e)}
                ).model_dump(),
                status=502,
            )

        except Exception as e:
            structlogger.error(
                "bot_builder_service.llm_builder.unexpected_error", error=str(e)
            )
            return response.json(
                ApiErrorResponse(
                    error="Unexpected error in LLM builder",
                    details=None,
                ).model_dump(),
                status=500,
            )

    async def current_tracker_from_input_channel(
        self,
    ) -> Optional[DialogueStateTracker]:
        """Generate chat bot context from current conversation."""
        if self.app.ctx.agent and self.input_channel.latest_tracker_session_id:
            return await self.app.ctx.agent.tracker_store.retrieve(
                self.input_channel.latest_tracker_session_id
            )
        else:
            return None

    @staticmethod
    async def _send_sse_event(
        sse_response: HTTPResponse, event: ServerSentEvent
    ) -> None:
        """Send a server-sent event."""
        await sse_response.send(event.format())

    def run(self) -> None:
        """Run the service."""
        structlogger.info(
            "service.starting",
            host=config.BUILDER_SERVER_HOST,
            port=config.BUILDER_SERVER_PORT,
        )

        self.app.run(
            host=config.BUILDER_SERVER_HOST,
            port=config.BUILDER_SERVER_PORT,
            legacy=True,
            motd=False,
        )
