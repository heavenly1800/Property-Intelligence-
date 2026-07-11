import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url:
    raise RuntimeError(
        "SUPABASE_URL is missing from your .env file."
    )

if not key:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY is missing from your .env file."
    )

supabase = create_client(url, key)