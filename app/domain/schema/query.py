from typing import Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    repo_url: Optional[str]
    question: Optional[str]
    user_id: Optional[str]

    class Config:
        populate_by_name = True
        from_attributes = True

class QueryResponse(BaseModel):
    text: str

class RepoRequest(BaseModel):
    repo_url: str
    github_token: str