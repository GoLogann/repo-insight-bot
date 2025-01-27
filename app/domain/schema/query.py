from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    repo_url: Optional[str]
    question: Optional[str]

    class Config:
        populate_by_name = True
        from_attributes = True