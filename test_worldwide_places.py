import requests

def search_destination(destination):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": destination,
        "format": "jsonv2",
        "limit": 5
    }
    headers = {
        "User-Agent": "TravelAgent/1.0 (travel planning project)"
    }
    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=20
    )
    response.raise_for_status()

    return response.json()

destination = input("Enter a destination: ")

results = search_destination(destination)

if results:
    print(f"\nResults for {destination}:\n")
    for place in results:
        print("Location Name:", place.get("name", "Unknown"))
        print("Location:", place.get("display_name", "Unknown"))
        print("Latitude:", place.get("lat"))
        print("Longitude:", place.get("lon"))
        print("-" * 50)
else:
    print("No destinations found.")
