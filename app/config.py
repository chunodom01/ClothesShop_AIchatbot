"""
app/config.py
Central configuration for the whole bot. Every setting comes from the `.env`
file via pydantic-settings, so there are NO hardcoded secrets in the code.
Anywhere you need an API key or option, do: `from app.config import settings`.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# ✅ Load .env from the project root (one level up from app/)
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # --- LLM provider ---
    llm_provider: str = "gemini"
    openai_api_key: str = ""
    google_api_key: str = ""  
    pinecone_environment: str
        # used by Gemini

    # --- Vector DB (Pinecone) ---
    pinecone_api_key: str = ""
    pinecone_index_name: str = "fanpage-faqs"

    # --- Facebook ---
    fb_verify_token: str = ""         # any random string; must match Meta webhook config
    fb_page_access_token: str = ""    # long-lived token, expires every 60 days

    # --- Google Sheets ---
    google_sheets_credentials_path: str = "./credentials/service-account.json"
    google_sheets_id: str = ""

    # --- Misc ---
    log_level: str = "INFO"

    # ✅ Explicitly point to the .env file in the project root
    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8"
    )

# ✅ Shared settings instance
settings = Settings()
print("Loaded Google API key:", settings.google_api_key)
