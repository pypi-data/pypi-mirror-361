import importlib.resources as pkg_resources
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

import ingenious.config.config as ingen_config
from ingenious.api.routes import chat as chat_route
from ingenious.api.routes import diagnostic as diagnostic_route
from ingenious.api.routes import message_feedback as message_feedback_route
from ingenious.api.routes import prompts as prompts_route

# Import your routers
from ingenious.models.api_routes import IApiRoutes
from ingenious.utils.namespace_utils import (
    import_class_with_fallback,
    import_module_with_fallback,
)


# Delay config loading until needed
def get_config():
    return ingen_config.get_config(os.getenv("INGENIOUS_PROJECT_PATH", ""))


# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class FastAgentAPI:
    def __init__(self, config: ingen_config.Config):
        # Set the working directory
        os.chdir(os.environ["INGENIOUS_WORKING_DIR"])

        # Initialize FastAPI app
        self.app = FastAPI(title="FastAgent API", version="1.0.0")

        # Mount Flask Prompt Tuner App if enabled
        if config.prompt_tuner.enable:
            import ingenious_prompt_tuner as prompt_tuner

            self.flask_app = prompt_tuner.create_app_for_fastapi()
            # Mount Flask App
            self.app.mount("/prompt-tuner", WSGIMiddleware(self.flask_app))

        # TODO: Add CORS option to config.
        origins = [
            "http://localhost",
            "http://localhost:5173",
            "http://localhost:4173",
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add in-built routes
        self.app.include_router(chat_route.router, prefix="/api/v1", tags=["Chat"])
        self.app.include_router(
            diagnostic_route.router, prefix="/api/v1", tags=["Diagnostic"]
        )
        self.app.include_router(
            prompts_route.router, prefix="/api/v1", tags=["Prompts"]
        )
        self.app.include_router(
            message_feedback_route.router, prefix="/api/v1", tags=["Message Feedback"]
        )

        # Add custom routes from ingenious extensions
        custom_api_routes_module = import_module_with_fallback("api.routes.custom")
        if custom_api_routes_module.__name__ != "ingenious.api.routes.custom":
            custom_api_routes_class = import_class_with_fallback(
                "api.routes.custom", "Api_Routes"
            )
            custom_api_routes_class_instance: IApiRoutes = custom_api_routes_class(
                config, self.app
            )
            custom_api_routes_class_instance.add_custom_routes()

        # Add exception handler
        self.app.add_exception_handler(Exception, self.generic_exception_handler)

        # Mount ChainLit
        if config.chainlit_configuration.enable:
            from chainlit.utils import mount_chainlit

            chainlit_path = pkg_resources.files("ingenious.chainlit") / "app.py"
            mount_chainlit(app=self.app, target=str(chainlit_path), path="/chainlit")

        # Redirect `/` to `/docs`
        self.app.get("/", tags=["Root"])(self.redirect_to_docs)

    async def redirect_to_docs(self):
        """Redirect the root endpoint to /docs."""
        return RedirectResponse(url="/docs")

    async def generic_exception_handler(self, request: Request, exc: Exception):
        if os.environ.get("LOADENV") == "True":
            load_dotenv()

        # Log the exception
        logger.exception(exc)

        return JSONResponse(
            status_code=500, content={"detail": f"An error occurred: {str(exc)}"}
        )

    async def root(self):
        # Locate the HTML file in ingenious.api
        html_path = pkg_resources.files("ingenious.chainlit") / "index.html"
        with html_path.open("r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
