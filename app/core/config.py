
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str  = ""
    CHROMA_DB_PATH: str = "./data/chroma_db"
    CHUNK_SIZE: int = 350
    CHUNK_OVERLAP: int = 20
    TOP_K_DOCUMENTS: int = 4

settings = Settings()
