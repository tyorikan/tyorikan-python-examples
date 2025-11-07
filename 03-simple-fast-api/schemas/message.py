from pydantic import BaseModel, Field, ConfigDict

class Message(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    hello: str = Field(alias="Hello")
