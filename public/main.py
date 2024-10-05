import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from mangum import Mangum

from config.app import get_settings
from routes import health, users

sys.path.append(".")
settings = get_settings()


description = """
The Spartan Framework, known as "The Swiss Army Knife for Serverless Development,"
is an essential tool for developers working with serverless architectures.
It significantly simplifies the creation of serverless applications across major
cloud providers by automatically generating Python code for classes and other
necessary components. This powerful framework accelerates your development process,
reduces manual coding, and ensures consistent, high-quality code
in your serverless projects. 🚀

Spartan Framework is versatile and can be used to efficiently develop:
- API
- Workflows or State Machines
- ETL Pipelines
- Containerized Microservices

Fully tested in AWS, Spartan Framework is also compatible with other cloud providers
like Azure and GCP, making it a flexible choice for a wide range of serverless applications.
"""


tags_metadata = [
    {
        "name": "Users",
        "description": "Operations related to users, providing functionality through a RESTful API.",
    },
    {
        "name": "Health Check",
        "description": "A health check endpoint to verify the API's functional condition.",
    },
]


settings = get_settings()


if settings.APP_ENVIRONMENT == "dev":
    root_path = "/dev/"
elif settings.APP_ENVIRONMENT == "uat":
    root_path = "/uat/"
elif settings.APP_ENVIRONMENT == "prod":
    root_path = "/prod/"
else:
    root_path = "/"


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


allowed_origins = settings.ALLOWED_ORIGINS


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.route)
app.include_router(users.route)


templates = Jinja2Templates(directory="public")


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


handle = Mangum(app)
