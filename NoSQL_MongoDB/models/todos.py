from pydantic import BaseModel


class ToDo(BaseModel):
    name: str
    description: str
    complete: bool

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "ToDo task title",
                    "description": "Test description here",
                    "complete": False,
                }
            ]
        }
