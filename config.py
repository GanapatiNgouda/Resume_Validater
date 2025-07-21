import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_SERVER: str = os.getenv("DB_SERVER", "localhost")
    DB_DATABASE: str = os.getenv("DB_DATABASE", "YourDatabaseName")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "YourUsername")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "YourPassword")
    DB_PORT: int = int(os.getenv("DB_PORT", "1433"))
    DB_DRIVER: str = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}") # Adjust driver as needed

settings = Settings()

