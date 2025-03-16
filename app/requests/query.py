from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    """
    Data model for creating a new user.

    Attributes:
        username (str): The username of the new user.
        email (EmailStr): The email address of the new user.
        password (str): The password for the new user.
    """

    query: str = Field(..., example="What is Generative AI?")

    model_config = ConfigDict(from_attributes=True, extra="forbid")
