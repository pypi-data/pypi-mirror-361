from pydantic import Field
from pydantic_settings import BaseSettings

class VectorXSettings(BaseSettings):
    api_key: str|None = Field(default=None, validation_alias="VectorX_API_KEY")
