
import os
import json
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load environment variables
env_file = Path(__file__).resolve().parent / ".env"
load_dotenv(env_file)

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "").strip()

# Cache settings
CACHE_DIR = Path(__file__).resolve().parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

CACHE_FILE = CACHE_DIR / "worldwide_attractions.json"
CACHE_DURATION = 7 * 24 * 60 * 60

HEADERS = {
    "User-Agent": "TravelAgent/1.0 (personal travel planning project)",
    "Accept-Language": "en"
}


# Find a destination anywhere in the world
def find_destination(destination):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": destination,
        "format": "jsonv2",
        "limit": 1
    }

    response = requests.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    return results[0]


# Find attractions using Geoapify
def find_attractions(latitude, longitude):
    if not GEOAPIFY_API_KEY or GEOAPIFY_API_KEY == "YOUR_ACTUAL_API_KEY":
        raise ValueError(
            "GEOAPIFY_API_KEY is missing or invalid in your .env file."
        )

    url = "https://api.geoapify.com/v2/places"

    params = {
        "categories": (
            "tourism.attraction,"
            "tourism.sights,"
            "entertainment.museum"
        ),
        "filter": f"circle:{longitude},{latitude},5000",
        "bias": f"proximity:{longitude},{latitude}",
        "limit": 100,
        "lang": "en",
        "apiKey": GEOAPIFY_API_KEY
    }

    print("Searching Geoapify for attractions...")

    response = requests.get(
        url,
        params=params,
        timeout=(5, 20)
    )

    response.raise_for_status()

    features = response.json().get("features", [])

    named_attractions = []
    seen = set()

    for feature in features:
        properties = feature.get("properties", {})

        name = properties.get("name")

        if not name:
            continue

        name_key = name.strip().lower()

        if name_key in seen:
            continue

        seen.add(name_key)

        categories = properties.get("categories", [])

        if categories:
            category = categories[0]
        else:
            category = "unknown"

        named_attractions.append({
            "name": name,
            "category": category
        })

    return named_attractions


# Load cached destination information
def load_cache(destination):
    if not CACHE_FILE.exists():
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            cache_data = json.load(file)

        key = destination.strip().lower()
        entry = cache_data.get(key)

        if entry is None:
            return None

        if time.time() - entry["timestamp"] > CACHE_DURATION:
            return None

        print("Using cached destination information.")

        return entry["result"]

    except (OSError, ValueError, KeyError, TypeError):
        return None


# Save destination information to cache
def save_cache(destination, result):
    cache_data = {}

    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as file:
                cache_data = json.load(file)
        except (OSError, ValueError):
            cache_data = {}

    key = destination.strip().lower()

    cache_data[key] = {
        "timestamp": time.time(),
        "result": result
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache_data, file, indent=4, ensure_ascii=False)


# Combine destination lookup and attraction search
def get_destination_attractions(destination):
    # Check cache first
    cached_result = load_cache(destination)

    if cached_result is not None:
        return cached_result

    # Find destination coordinates
    location = find_destination(destination)

    if location is None:
        return None

    latitude = float(location["lat"])
    longitude = float(location["lon"])

    # Retrieve real attractions
    attractions = find_attractions(latitude, longitude)

    result = {
        "destination": location.get("display_name", destination),
        "latitude": latitude,
        "longitude": longitude,
        "attractions": attractions
    }

    # Save successful results
    save_cache(destination, result)

    return result
