from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.helpers.environment import env
from routes import health, inference

description = """
Spartan Framework—"The swiss army knife for serverless development"—is a powerful scaffold that simplifies
the creation of serverless applications on AWS. It streamlines your development process and ensures code
consistency, allowing you to build scalable and efficient applications on AWS with ease. 🚀

Spartan Framework is versatile and can be used to efficiently develop:
- REST API
- Workflows or State Machines
- ETL Pipelines (Extract, Transform, Load)
- Data Processing Applications
- Event-Driven Applications
- Microservices

Fully tested in AWS, Spartan Framework is also compatible with other cloud providers
like Azure and GCP, making it a flexible choice for a wide range of serverless applications.
"""


tags_metadata = [
    {
        "name": "Inference",
        "description": "Operations related to inference or prediction, providing functionality through a RESTful API.",
    },
    {
        "name": "Health",
        "description": "A health check endpoint to verify the API's functional condition.",
    },
]


root_path = ""

if env("APP_ENVIRONMENT") == "prod":
    root_path = "/prod/"
elif env("APP_ENVIRONMENT") == "stage":
    root_path = "/stage/"
elif env("APP_ENVIRONMENT") == "dev":
    root_path = "/dev/"
else:
    root_path = ""


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
    root_path=root_path,  # Updated root_path
    debug=env().APP_DEBUG,
)


allowed_origins = env().ALLOWED_ORIGINS


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def read_welcome(request: Request):
    return {
        "message": "Welcome to Spartan Framework!",
        "environment": env("APP_ENVIRONMENT"),
        "docs": f"{request.url._url}/{root_path}docs",
    }


app.include_router(inference.route)
app.include_router(health.route)


handle = Mangum(app, lifespan="auto")
