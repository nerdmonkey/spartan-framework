from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from config.app import get_settings
from routes import router


description = """
Artisan is a tool that simplifies the creation of serverless applications on popular cloud providers by generating Python code for classes and more. It streamlines your development process, saving you time and ensuring code consistency in your serverless projects. 🚀
"""

tags_metadata = [
    {
        "name": "Default",
        "description": "This endpoint allows performing operations related to users. It provides functionality to save and download users through a RESTful API.",
    }
]

settings = get_settings()
root_path = "/dev/"
if settings.APP_ENVIRONMENT == "local" or settings.APP_ENVIRONMENT == "test":
    root_path = "/"

app = FastAPI(
    title="Artisan",
    description=description,
    version="0.1.0",
    terms_of_service="N/A",
    contact={
        "name": "Sydel Palinlin",
        "url": "https://github.com/nerdmonkey",
        "email": "sydel.palinlin@gmail.com",
    },
    openapi_tags=tags_metadata,
    root_path=root_path,
)

allowed_origins = settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

handle = Mangum(app)
