#!/usr/bin/env python3
"""Main entry point for the prompt-to-bot service."""

import logging
import sys
from typing import Optional

import structlog
from sanic import HTTPResponse, Sanic
from sanic.request import Request
from sanic_openapi import openapi3_blueprint

import rasa.core.utils
from rasa.builder import config
from rasa.builder.logging_utils import collecting_logs_processor
from rasa.builder.service import bp, setup_project_generator
from rasa.core.channels.studio_chat import StudioChatInput
from rasa.server import configure_cors
from rasa.utils.common import configure_logging_and_warnings
from rasa.utils.log_utils import configure_structlog
from rasa.utils.sanic_error_handler import register_custom_sanic_error_handler

structlogger = structlog.get_logger()


def setup_logging() -> None:
    """Setup logging configuration."""
    log_level = logging.DEBUG

    configure_logging_and_warnings(
        log_level=log_level,
        logging_config_file=None,
        warn_only_once=True,
        filter_repeated_logs=True,
    )

    configure_structlog(
        log_level,
        include_time=True,
        additional_processors=[collecting_logs_processor],
    )


def setup_input_channel() -> StudioChatInput:
    """Setup the input channel for chat interactions."""
    studio_chat_credentials = config.get_default_credentials().get(
        StudioChatInput.name()
    )
    return StudioChatInput.from_credentials(credentials=studio_chat_credentials)


def setup_middleware(app: Sanic) -> None:
    """Setup middleware for request/response processing."""

    @app.middleware("request")
    async def log_request(request: Request) -> None:
        structlogger.info(
            "request.received",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr or "unknown",
        )

    @app.middleware("response")
    async def log_response(request: Request, response: HTTPResponse) -> None:
        structlogger.info(
            "request.completed",
            method=request.method,
            path=request.path,
            status=response.status,
        )


def create_app(project_folder: Optional[str] = None) -> Sanic:
    """Create and configure the Sanic app."""
    app = Sanic("BotBuilderService")

    # Basic app configuration
    app.config.REQUEST_TIMEOUT = 60  # 1 minute timeout
    app.ctx.agent = None

    # Set up project generator and store in app context
    app.ctx.project_generator = setup_project_generator(project_folder)

    # Set up input channel and store in app context
    app.ctx.input_channel = setup_input_channel()

    # Register the blueprint
    app.blueprint(bp)

    # OpenAPI docs
    app.blueprint(openapi3_blueprint)
    app.config.API_TITLE = "Bot Builder API"
    app.config.API_VERSION = rasa.__version__
    app.config.API_DESCRIPTION = (
        "API for building conversational AI bots from prompts and templates. "
        "The API allows to change the assistant and retrain it with new data."
    )

    # Setup middleware
    setup_middleware(app)

    configure_cors(app, cors_origins=config.CORS_ORIGINS)

    # Register input channel webhooks
    from rasa.core import channels

    channels.channel.register([app.ctx.input_channel], app, route="/webhooks/")

    return app


def main(project_folder: Optional[str] = None) -> None:
    """Main entry point."""
    try:
        # Setup logging
        setup_logging()

        # Create and configure app
        app = create_app(project_folder)
        register_custom_sanic_error_handler(app)

        # Run the service
        structlogger.info(
            "service.starting",
            host=config.BUILDER_SERVER_HOST,
            port=config.BUILDER_SERVER_PORT,
        )

        app.run(
            host=config.BUILDER_SERVER_HOST,
            port=config.BUILDER_SERVER_PORT,
            legacy=True,
            motd=False,
        )

    except KeyboardInterrupt:
        print("\nService stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    project_folder = sys.argv[1] if len(sys.argv) > 1 else None
    main(project_folder)
