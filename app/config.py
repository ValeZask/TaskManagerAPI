from dotenv import load_dotenv
import os

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "supersecret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
