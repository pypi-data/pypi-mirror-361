"""Main service for the prompt-to-bot functionality."""

import os
from typing import Any, Optional

import structlog
from sanic import Blueprint, HTTPResponse, response
from sanic.request import Request
from sanic_openapi import openapi

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
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.studio.upload import CALMUserData, extract_calm_import_parts_from_importer
from rasa.utils.openapi import model_to_schema

structlogger = structlog.get_logger()

# Create the blueprint
bp = Blueprint("bot_builder", url_prefix="/api")


def setup_project_generator(project_folder: Optional[str] = None) -> ProjectGenerator:
    """Initialize and return a ProjectGenerator instance."""
    if project_folder is None:
        import tempfile

        project_folder = tempfile.mkdtemp(prefix="rasa_builder_")

    # working directory needs to be the project folder, e.g.
    # for relative paths (./docs) in a projects config to work
    os.chdir(project_folder)

    structlogger.info(
        "bot_builder_service.service_initialized", project_folder=project_folder
    )

    return ProjectGenerator(project_folder)


def get_project_generator(request: Request) -> ProjectGenerator:
    """Get the project generator from app context."""
    return request.app.ctx.project_generator


def get_input_channel(request: Request) -> StudioChatInput:
    """Get the input channel from app context."""
    return request.app.ctx.input_channel


def extract_calm_import_parts_from_project_generator(
    project_generator: ProjectGenerator,
) -> CALMUserData:
    """Extract CALMUserData from a ProjectGenerator.

    Args:
        project_generator: The project generator to extract data from

    Returns:
        CALMUserData containing flows, domain, config, endpoints, and nlu data
    """
    # Get the training data importer
    importer = project_generator._create_importer()

    # Extract endpoints (if exists)
    endpoints_path = project_generator.project_folder / "endpoints.yml"
    if endpoints_path.exists():
        from rasa.shared.utils.yaml import read_yaml_file

        endpoints = read_yaml_file(endpoints_path, expand_env_vars=False)
    else:
        endpoints = {}

    # Use the shared function with the importer and project data paths
    return extract_calm_import_parts_from_importer(
        importer=importer,
        config=None,  # Let the shared function get config from importer
        endpoints=endpoints,
    )


# Health check endpoint
@bp.route("/", methods=["GET"])
@openapi.summary("Health check endpoint")
@openapi.description("Returns the health status of the Bot Builder service")
@openapi.tag("health")
@openapi.response(200, {"application/json": {"status": str, "service": str}})
async def health(request: Request) -> HTTPResponse:
    """Health check endpoint."""
    return response.json({"status": "ok", "service": "bot-builder"})


@bp.route("/prompt-to-bot", methods=["POST"])
@openapi.summary("Generate bot from natural language prompt")
@openapi.description(
    "Creates a complete conversational AI bot from a natural language prompt "
    "using LLM generation. Returns server-sent events (SSE) for real-time "
    "progress tracking through the entire bot creation process.\n\n"
    "**SSE Event Flow:**\n"
    "1. `received` - Request received by server\n"
    "2. `generating` - Generating bot project files\n"
    "3. `generation_success` - Bot generation completed successfully\n"
    "4. `training` - Training the bot model\n"
    "5. `train_success` - Model training completed\n"
    "6. `done` - Bot creation completed\n\n"
    "**Error Events (can occur at any time):**\n"
    "- `generation_error` - Failed to generate bot from prompt\n"
    "- `train_error` - Bot generated but training failed\n"
    "- `validation_error` - Generated bot configuration is invalid\n"
    "- `error` - Unexpected error occurred\n\n"
    "**Usage:** Send POST request with Content-Type: application/json and "
    "Accept: text/event-stream"
)
@openapi.tag("bot-generation")
@openapi.body(
    {"application/json": model_to_schema(PromptRequest)},
    description="Prompt request with natural language description and client ID "
    "for tracking",
    required=True,
)
@openapi.response(
    200,
    {"text/event-stream": str},
    description="Server-sent events stream with real-time progress updates",
)
@openapi.response(
    400,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Validation error in request payload",
)
@openapi.response(
    500,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Internal server error",
)
async def handle_prompt_to_bot(request: Request) -> None:
    """Handle prompt-to-bot generation requests."""
    sse_response = await request.respond(content_type="text/event-stream")
    project_generator = get_project_generator(request)
    input_channel = get_input_channel(request)

    try:
        # 1. Received
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="received", data={"status": "received"}),
        )

        # Validate request
        prompt_data = PromptRequest(**request.json)

        # 2. Generating
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="generating", data={"status": "generating"}),
        )

        try:
            # Generate project with retries
            bot_files = await project_generator.generate_project_with_retries(
                prompt_data.prompt,
                template=ProjectTemplateName.PLAIN,
            )

            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="generation_success",
                    data={"status": "generation_success"},
                ),
            )

        except (ProjectGenerationError, LLMGenerationError) as e:
            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="generation_error",
                    data={"status": "generation_error", "error": str(e)},
                ),
            )
            await sse_response.eof()
            return

        # 3. Training
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="training", data={"status": "training"}),
        )

        try:
            # Train and load agent
            importer = project_generator._create_importer()
            request.app.ctx.agent = await train_and_load_agent(importer)

            # Update input channel with new agent
            input_channel.agent = request.app.ctx.agent

            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="train_success", data={"status": "train_success"}
                ),
            )

        except TrainingError as e:
            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="train_error",
                    data={"status": "train_error", "error": str(e)},
                ),
            )
            await sse_response.eof()
            return

        # 4. Done
        await _send_sse_event(
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
        await _send_sse_event(
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
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="error", data={"status": "error", "error": str(e)}),
        )
    finally:
        await sse_response.eof()


@bp.route("/template-to-bot", methods=["POST"])
@openapi.summary("Generate bot from predefined template")
@openapi.description(
    "Creates a complete conversational AI bot from a predefined template with "
    "immediate setup. Returns server-sent events (SSE) for real-time progress "
    "tracking through the entire bot creation process.\n\n"
    "**SSE Event Flow:**\n"
    "1. `received` - Request received by server\n"
    "2. `generating` - Initializing bot from template\n"
    "3. `generation_success` - Template initialization completed successfully\n"
    "4. `training` - Training the bot model\n"
    "5. `train_success` - Model training completed\n"
    "6. `done` - Bot creation completed\n\n"
    "**Error Events (can occur at any time):**\n"
    "- `generation_error` - Failed to initialize bot from template\n"
    "- `train_error` - Template loaded but training failed\n"
    "- `validation_error` - Template configuration is invalid\n"
    "- `error` - Unexpected error occurred\n\n"
    "**Usage:** Send POST request with Content-Type: application/json and "
    "Accept: text/event-stream\n"
    "**Templates Available:** Check available templates through the API or "
    "documentation"
)
@openapi.tag("bot-generation")
@openapi.body(
    {"application/json": model_to_schema(TemplateRequest)},
    description="Template request with template name and client ID for " "tracking",
    required=True,
)
@openapi.response(
    200,
    {"text/event-stream": model_to_schema(ServerSentEvent)},
    description="Server-sent events stream with real-time progress updates",
    example=ServerSentEvent(
        event="generation_success",
        data={"status": "generation_success"},
    ).model_dump(),
)
@openapi.response(
    400,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Validation error in request payload or invalid template name",
)
@openapi.response(
    500,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Internal server error",
)
async def handle_template_to_bot(request: Request) -> None:
    """Handle template-to-bot generation requests."""
    sse_response = await request.respond(content_type="text/event-stream")
    project_generator = get_project_generator(request)
    input_channel = get_input_channel(request)

    try:
        # 1. Received
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="received", data={"status": "received"}),
        )

        # Validate request
        template_data = TemplateRequest(**request.json)

        # 2. Generating
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="generating", data={"status": "generating"}),
        )

        try:
            # Generate project with retries
            project_generator.init_from_template(
                template_data.template_name,
            )
            bot_files = project_generator.get_bot_files()

            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="generation_success",
                    data={"status": "generation_success"},
                ),
            )

        except ProjectGenerationError as e:
            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="generation_error",
                    data={"status": "generation_error", "error": str(e)},
                ),
            )
            await sse_response.eof()
            return

        # 3. Training
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="training", data={"status": "training"}),
        )

        try:
            # Train and load agent
            importer = project_generator._create_importer()
            request.app.ctx.agent = await train_and_load_agent(importer)

            # Update input channel with new agent
            input_channel.agent = request.app.ctx.agent

            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="train_success", data={"status": "train_success"}
                ),
            )

        except TrainingError as e:
            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="train_error",
                    data={"status": "train_error", "error": str(e)},
                ),
            )
            await sse_response.eof()
            return

        # 4. Done
        await _send_sse_event(
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
        await _send_sse_event(
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
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="error", data={"status": "error", "error": str(e)}),
        )
    finally:
        await sse_response.eof()


@bp.route("/files", methods=["GET"])
@openapi.summary("Get bot files")
@openapi.description("Retrieves the current bot configuration files and data")
@openapi.tag("bot-files")
@openapi.response(
    200,
    {"application/json": model_to_schema(ApiResponse)},
    description="Bot files retrieved successfully",
)
@openapi.response(
    500,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Internal server error",
)
async def get_bot_files(request: Request) -> HTTPResponse:
    """Get current bot files."""
    project_generator = get_project_generator(request)
    bot_files = project_generator.get_bot_files()
    return response.json(
        ApiResponse(
            status="success",
            message="Bot files fetched successfully",
            data={"files": bot_files},
        ).model_dump()
    )


@bp.route("/files", methods=["PUT"])
@openapi.summary("Update bot files")
@openapi.description(
    "Updates the bot configuration files and retrains the model. "
    "Returns server-sent events for real-time progress tracking."
)
@openapi.tag("bot-files")
@openapi.body(
    {"application/json": dict},
    description="Bot files containing updated configuration files",
    required=True,
)
@openapi.response(
    200,
    {"text/event-stream": str},
    description="Server-sent events stream with update progress",
)
@openapi.response(
    400,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Validation error in bot files",
)
@openapi.response(
    500,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Internal server error",
)
async def update_bot_files(request: Request) -> None:
    """Update bot files with server-sent events for progress tracking."""
    sse_response = await request.respond(content_type="text/event-stream")
    project_generator = get_project_generator(request)
    input_channel = get_input_channel(request)

    try:
        # 1. Received
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="received", data={"status": "received"}),
        )

        # Update bot files
        bot_files = request.json
        project_generator.update_bot_files(bot_files)

        # 2. Validating
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="validating", data={"status": "validating"}),
        )

        try:
            importer = project_generator._create_importer()
            validation_error = await validate_project(importer)

            if validation_error:
                raise ValidationError(validation_error)

            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="validation_success",
                    data={"status": "validation_success"},
                ),
            )

        except ValidationError as e:
            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="validation_error",
                    data={"status": "validation_error", "error": str(e)},
                ),
            )
            await sse_response.eof()
            return

        # 3. Training
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="training", data={"status": "training"}),
        )

        try:
            request.app.ctx.agent = await train_and_load_agent(importer)
            input_channel.agent = request.app.ctx.agent

            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="train_success", data={"status": "train_success"}
                ),
            )

        except TrainingError as e:
            await _send_sse_event(
                sse_response,
                ServerSentEvent(
                    event="train_error",
                    data={"status": "train_error", "error": str(e)},
                ),
            )
            await sse_response.eof()
            return

        # 4. Done
        await _send_sse_event(
            sse_response,
            ServerSentEvent(
                event="done",
                data={
                    "status": "done",
                },
            ),
        )

    except Exception as e:
        await _send_sse_event(
            sse_response,
            ServerSentEvent(event="error", data={"status": "error", "error": str(e)}),
        )
    finally:
        await sse_response.eof()


@bp.route("/data", methods=["GET"])
@openapi.summary("Get bot data")
@openapi.description(
    "Retrieves the current bot data in CALM import format with flows, domain, "
    "config, endpoints, and NLU data"
)
@openapi.tag("bot-data")
@openapi.response(
    200,
    {"application/json": model_to_schema(ApiResponse)},
    description="Bot data retrieved successfully",
)
@openapi.response(
    500,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Internal server error",
)
async def get_bot_data(request: Request) -> HTTPResponse:
    """Get current bot data in CALM import format."""
    try:
        project_generator = get_project_generator(request)
        calm_parts = extract_calm_import_parts_from_project_generator(project_generator)

        return response.json(
            ApiResponse(
                status="success",
                message="Bot data fetched successfully",
                data=calm_parts.model_dump(),
            ).model_dump()
        )
    except Exception as e:
        structlogger.error("bot_builder_service.get_bot_data.error", error=str(e))
        return response.json(
            ApiErrorResponse(
                error="Failed to retrieve bot data",
                details={"error": str(e)},
            ).model_dump(),
            status=500,
        )


@bp.route("/llm-builder", methods=["POST"])
@openapi.summary("LLM assistant for bot building")
@openapi.description(
    "Provides LLM-powered assistance for bot building tasks, including "
    "debugging, suggestions, and explanations"
)
@openapi.tag("llm-assistant")
@openapi.body(
    {"application/json": model_to_schema(LLMBuilderRequest)},
    description="LLM builder request containing chat messages and context",
    required=True,
)
@openapi.response(
    200,
    {"application/json": dict},
    description="LLM response with assistance and suggestions",
)
@openapi.response(
    400,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Validation error in request",
)
@openapi.response(
    502,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="LLM generation failed",
)
@openapi.response(
    500,
    {"application/json": model_to_schema(ApiErrorResponse)},
    description="Internal server error",
)
async def llm_builder(request: Request) -> HTTPResponse:
    """Handle LLM builder requests."""
    project_generator = get_project_generator(request)
    input_channel = get_input_channel(request)

    try:
        # Validate request
        builder_request = LLMBuilderRequest(**request.json)

        # Get current conversation context
        current_tracker = await current_tracker_from_input_channel(
            request.app, input_channel
        )
        bot_logs = get_recent_logs()
        chat_bot_files = project_generator.get_bot_files()

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
    app: Any, input_channel: StudioChatInput
) -> Optional[DialogueStateTracker]:
    """Generate chat bot context from current conversation."""
    if app.ctx.agent and input_channel.latest_tracker_session_id:
        return await app.ctx.agent.tracker_store.retrieve(
            input_channel.latest_tracker_session_id
        )
    else:
        return None


async def _send_sse_event(sse_response: HTTPResponse, event: ServerSentEvent) -> None:
    """Send a server-sent event."""
    await sse_response.send(event.format())
