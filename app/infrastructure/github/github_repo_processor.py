import logging
import os
import asyncio
import json
from pydriller import Repository, ModificationType
from app.utils.helpers import (
    find_and_convert_in_dir,
    extract_repo_name,
    extract_repo_name_and_owner
)
import aiohttp
from gidgethub.aiohttp import GitHubAPI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GitHubRepoProcessor:
    def __init__(self, github_token, local_path="data"):
        self.github_token = github_token
        self.local_path = local_path
        self.session = aiohttp.ClientSession()
        self.gh = GitHubAPI(self.session, "my-app", oauth_token=github_token)

    async def clone_repo(self, repo_url):
        repo_name = extract_repo_name(repo_url)
        repo_dir = os.path.join(self.local_path, repo_name)

        if not os.path.isdir(repo_dir):
            try:
                logger.debug(f"Cloning repository: {repo_url}")
                process = await asyncio.create_subprocess_exec(
                    "git", "clone", repo_url,
                    cwd=self.local_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    if os.path.isdir(repo_dir):
                        meta_data = await self.form_metadata(repo_url)
                        self._save_metadata(repo_dir, meta_data)
                        find_and_convert_in_dir(repo_dir)
                        return {"status": "success", "message": f"Cloned repo {repo_url}"}
                    else:
                        logger.error(f"Repository directory {repo_dir} was not created.")
                        return {"status": "error", "message": f"Repository directory {repo_dir} was not created."}
                else:
                    logger.error(f"Failed to clone repo {repo_url}: {stderr.decode()}")
                    return {"status": "error", "message": f"Failed to clone repo {repo_url}", "detail": stderr.decode()}
            except Exception as e:
                logger.exception(f"Exception occurred while cloning repo {repo_url}: {str(e)}")
                return {"status": "error", "message": f"Exception occurred: {str(e)}"}
        else:
            logger.info(f"Repo {repo_name} already exists locally")
            return {"status": "info", "message": f"Repo {repo_name} already exists locally"}

    async def form_metadata(self, repo_url: str) -> dict:
        repo_name = extract_repo_name_and_owner(repo_url)
        owner, repo = repo_name.split('/')
        logger.debug(f"Processing repository: {repo_name}")

        repo_data = await self.gh.getitem(f"/repos/{owner}/{repo}")
        logger.debug(f"Repository data: {repo_data}")

        repository_data = {
            "id": repo_data["id"],
            "name": repo_data["name"],
            "owner": repo_data["owner"]["login"],
            "url": repo_data["html_url"],
            "updated_at": repo_data["updated_at"],
            "archived": repo_data["archived"],
            "default_branch": repo_data["default_branch"],
            "open_issues_count": repo_data["open_issues_count"],
            "commits_on_date": {},
            "issues_on_date": {}
        }

        commits = []
        for commit in Repository(repo_url).traverse_commits():
            commit_info = {
                "hash": commit.hash,
                "author": commit.author.name,
                "date": commit.author_date.isoformat(),
                "message": commit.msg,
                "files": []
            }

            for modified_file in commit.modified_files:
                mod_info = {
                    "filename": modified_file.filename,
                    "changes": modified_file.change_type,
                    "additions": modified_file.added_lines,
                    "deletions": modified_file.deleted_lines,
                    "diff": modified_file.diff
                }
                commit_info["files"].append(mod_info)

            commits.append(commit_info)

            date = commit.author_date.date().isoformat()
            if date not in repository_data["commits_on_date"]:
                repository_data["commits_on_date"][date] = {"total_commits_on_day": 0, "commits": []}

            repository_data["commits_on_date"][date]["commits"].append(commit_info)
            repository_data["commits_on_date"][date]["total_commits_on_day"] += 1

        repository_data["total_commits"] = len(commits)

        issues = await self.gh.getitem(f"/repos/{owner}/{repo}/issues")
        logger.debug(f"Issues fetched: {issues}")

        for issue in issues:
            issue_info = {
                "id": issue["id"],
                "title": issue["title"],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "author": issue["user"]["login"]
            }

            date = issue["created_at"].split("T")[0]
            if date not in repository_data["issues_on_date"]:
                repository_data["issues_on_date"][date] = {"total_issues_on_day": 0, "issues": []}

            repository_data["issues_on_date"][date]["issues"].append(issue_info)
            repository_data["issues_on_date"][date]["total_issues_on_day"] += 1

        repository_data["total_issues"] = len(issues)

        return repository_data

    async def close(self):
        await self.session.close()

    async def initialize_session(self):
        if self.session is None or self.session.closed:
            logger.debug("Initializing new aiohttp session")
            self.session = aiohttp.ClientSession(base_url="https://api.github.com")

    async def fetch_all_issues(self, owner: str, repo: str) -> list | None:
        await self.initialize_session()
        url = f"/repos/{owner}/{repo}/issues"
        try:
            logger.debug(f"Fetching issues from {url}")
            async with self.session.get(url) as response:
                response.raise_for_status()
                issues = await response.json()
                logger.debug(f"Issues fetched successfully: {issues}")
                return issues
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error {e.status} while fetching issues from {owner}/{repo}: {e.message}")
        except Exception as e:
            logger.exception(f"Unexpected error while fetching issues from {owner}/{repo}: {e}")
        return None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    import os

    def _save_metadata(self, repo_dir: str, metadata: dict) -> None:
        metadata_file = os.path.join(repo_dir, "repository_data.txt")
        with open(metadata_file, "w", encoding='utf-8') as outfile:
            json.dump(metadata, outfile, indent=1, default=self._handle_commit)

    def _handle_commit(self, obj):
        if isinstance(obj, ModificationType):
            return obj.name

        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')