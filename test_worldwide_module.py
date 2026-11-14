from worldwide_places import get_destination_attractions
import requests

destination = input("Enter a destination: ")

try:
    result = get_destination_attractions(destination)

    if result is None:
        print("Destination not found.")

    else:
        print("\nDestination:", result["destination"])
        print("Latitude:", result["latitude"])
        print("Longitude:", result["longitude"])

        attractions = result["attractions"]

        print(f"\nFound {len(attractions)} attractions:\n")

        for attraction in attractions[:15]:
            print("Name:", attraction["name"])
            print("Category:", attraction["category"])
            print("-" * 40)

except requests.exceptions.RequestException as error:
    print("Could not retrieve destination information.")
    print("Error:", error)
