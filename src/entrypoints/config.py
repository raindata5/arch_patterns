from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pg_oltp_api_db: str
    pg_oltp_api_port: str
    pg_oltp_api_host: str
    pg_oltp_api_password: str
    pg_oltp_api_user: str
    api_url: str
    class Config:
        env_file = ".env"


settings = Settings()