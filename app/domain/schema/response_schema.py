from pydantic import BaseModel

class ResponseSchema(BaseModel):
    response: str

    class Config:
        populate_by_name = True
        from_attributes = True