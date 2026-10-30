import requests

def search_attractions(latitude, longitude):
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
            "User-Agent": "TravelAgent/1.0 (travel planning project)"
        },
        timeout=60
    )
    response.raise_for_status()
    return response.json()


# Tokyo coordinates from our previous test
latitude = 35.6768601
longitude = 139.7638947

results = search_attractions(latitude, longitude)

places = results.get("elements", [])

print(f"\nFound {len(places)} places near Tokyo:\n")

for place in places[:15]:
    tags = place.get("tags", {})
    name = tags.get("name", "Unnamed place")
    category = tags.get("tourism", "Unknown category")
    print("Name:", name)
    print("Category:", category)
    print("-" * 40)
