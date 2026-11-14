import requests

# Find a destination anywhere in the world
def find_destination(destination):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": destination,
        "format": "jsonv2",
        "limit": 1
    }

    headers = {
        "User-Agent": "TravelAgent/1.0 (personal travel planning project)",
        "Accept-Language": "en"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    return results[0]


# Find attractions near the destination
def find_attractions(latitude, longitude):
    url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json][timeout:25];
    node(around:1000,{latitude},{longitude})
      ["tourism"~"^(attraction|museum)$"];
    out tags;
    """

    response = requests.post(
        url,
        data={"data": query},
        headers={
            "User-Agent": "TravelAgent/1.0 (personal travel planning project)"
        },
        timeout=60
    )

    response.raise_for_status()

    attractions = response.json().get("elements", [])

    # Keep only places that have a name
    named_attractions = []

    for place in attractions:
        tags = place.get("tags", {})

        name = tags.get("name:en") or tags.get("name")

        if name:
            named_attractions.append({
                "name": name,
                "category": tags.get("tourism", "unknown")
            })

    return named_attractions


# Combine destination lookup and attraction search
def get_destination_attractions(destination):
    location = find_destination(destination)

    if location is None:
        return None

    latitude = float(location["lat"])
    longitude = float(location["lon"])

    attractions = find_attractions(latitude, longitude)

    return {
        "destination": location.get("display_name", destination),
        "latitude": latitude,
        "longitude": longitude,
        "attractions": attractions
    }
