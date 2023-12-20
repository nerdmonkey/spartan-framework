import sys

sys.path.append(".")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from mangum import Mangum

from config.app import get_settings
from routes import health, users

settings = get_settings()

# Description of the FastAPI application
description = """
Spartan, often referred to as "The swiss army knife for serverless development," is a tool that simplifies the creation of serverless applications on popular cloud providers by generating Python code for classes and more. It streamlines your development process, saving you time and ensuring code consistency in your serverless projects. 🚀
"""

# Metadata for API tags
tags_metadata = [
    {
        "name": "Users",
        "description": "This endpoint allows performing operations related to users. It provides functionality to users through a RESTful API.",
    },
    {
        "name": "Health Check",
        "description": "This is a health check endpoint for an API serves as a method to verify the API's functional condition.",
    },
]

# Get application settings
settings = get_settings()

# Define the root path based on the environment
root_path = "/dev/"
if settings.APP_ENVIRONMENT == "local" or settings.APP_ENVIRONMENT == "test":
    root_path = "/"

# Create a FastAPI app instance
app = FastAPI(
    title="Spartan",
    description=description,
    version="0.2.5",
    terms_of_service="N/A",
    contact={
        "name": "Sydel Palinlin",
        "url": "https://github.com/nerdmonkey",
        "email": "sydel.palinlin@gmail.com",
    },
    openapi_tags=tags_metadata,
    root_path=root_path,
    debug=settings.APP_DEBUG,
)

# Define allowed origins for CORS
allowed_origins = settings.ALLOWED_ORIGINS

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router for health check and users
app.include_router(health.route)
app.include_router(users.route)

# Define Jinja2 templates directory
templates = Jinja2Templates(directory="public")


# Define a route for the welcome page
@app.get("/", include_in_schema=False)
async def read_welcome(request: Request):
    """
    Endpoint for the welcome page.

    Args:
        request (Request): The incoming request.

    Returns:
        TemplateResponse: A Jinja2 template response for the welcome page.
    """
    return templates.TemplateResponse(
        "static/welcome.html", {"request": request, "root_path": app.root_path}
    )


# Create a Mangum handler for AWS Lambda
handle = Mangum(app)
