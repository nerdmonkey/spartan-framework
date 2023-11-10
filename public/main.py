import sys
sys.path.append(".")

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from mangum import Mangum

from config.app import get_settings
from routes import users, health

description = """
Spartan, often referred to as "The swiss army knife for serverless development," is a tool that simplifies the creation of serverless applications on popular cloud providers by generating Python code for classes and more. It streamlines your development process, saving you time and ensuring code consistency in your serverless projects. 🚀
"""

tags_metadata = [
    {
        "name": "Users",
        "description": "This endpoint allows performing operations related to users. It provides functionality to users through a RESTful API.",
    },
     {
        "name": "Health Check",
        "description": "This is a health check endpoint for an API serves as a method to verify the API's functional condition."
    },
]

settings = get_settings()
root_path = "/dev/"
if settings.APP_ENVIRONMENT == "local" or settings.APP_ENVIRONMENT == "test":
    root_path = "/"

app = FastAPI(
    title="Spartan",
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

app.include_router(health.route)
app.include_router(users.route)

templates = Jinja2Templates(directory="public")

@app.get("/", include_in_schema=False)
async def read_welcome(request: Request):
    return templates.TemplateResponse("static/welcome.html", {"request": request, "root_path": app.root_path})

handle = Mangum(app)
