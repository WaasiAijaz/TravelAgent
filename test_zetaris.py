
import json
import os
import uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv

# Load the TravelAgent configuration
load_dotenv(Path(__file__).resolve().parent / ".env")

base_url = os.getenv(
    "ZETARIS_REST_URL",
    "http://127.0.0.1:8888/api/v1.0"
).rstrip("/")

api_key = os.getenv("ZETARIS_API_KEY", "").strip()
org_id = os.getenv("ZETARIS_ORG_ID", "").strip()

if not api_key or not org_id:
    print("Missing Zetaris API key or Organization ID in .env.")
    raise SystemExit(1)

# Run a harmless test query
payload = {"sql": "SELECT * FROM NY_TAXI.taxi_zones LIMIT 5"}

request = Request(
    f"{base_url}/sql-editor/sqls/run-query",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "X-Org-ID": org_id,
        "X-Request-ID": str(uuid.uuid4()),
        "Content-Type": "application/json",
    },
    method="POST",
)

try:
    print("Connecting TravelAgent to Zetaris...")

    with urlopen(request, timeout=30) as response:
        print("HTTP status:", response.status)
        print("Zetaris response:")
        print(response.read().decode("utf-8"))
        print("Zetaris request completed.")

except HTTPError as error:
    print("Zetaris returned HTTP status:", error.code)
    print(error.read().decode("utf-8"))

except URLError as error:
    print("Could not connect to Zetaris.")
    print("Details:", error.reason)
