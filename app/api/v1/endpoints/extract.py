import os

from fastapi import HTTPException, Header, APIRouter

from app.domain.schema.query import RepoRequest
from app.infrastructure.github.github_repo_processor import GitHubRepoProcessor

app = APIRouter()

@app.post("/extract")
async def extract_repo(repo_request: RepoRequest):
    processor = GitHubRepoProcessor(github_token=repo_request.github_token, local_path="/home/logan/TEES/repo-insight-bot/data")

    try:
        response = await processor.clone_repo(repo_request.url)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))