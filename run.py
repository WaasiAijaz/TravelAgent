
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, APIConnectionError, APIStatusError

# Load settings from the .env file in the project folder
env_file = Path(__file__).resolve().parent / ".env"
load_dotenv(env_file)

base_url = os.getenv("METERLESS_BASE_URL", "http://127.0.0.1:8088/v1")
token = os.getenv("METERLESS_RUNTIME_TOKEN", "").strip()
model = os.getenv("METERLESS_MODEL", "meterless/auto")
app_name = os.getenv("METERLESS_APP", "travelagent").lower()

if not token or token == "REPLACE_WITH_YOUR_TOKEN":
    print("Error: Check METERLESS_RUNTIME_TOKEN in your .env file.")
    sys.exit(1)

# Connect TravelAgent to Meterless Runtime
client = OpenAI(
    api_key=token,
    base_url=base_url,
    default_headers={
        "meterless-app": app_name,
        "meterless-scope": "user",
    },
    timeout=180.0,
)


def plan_vacation():
    print("\n=== Welcome to TravelAgent ===")
    print("Let's plan your next vacation!\n")

    destination = input("Where would you like to travel to? ").strip()
    days = input("How many days is your trip? ").strip()
    travelers = input("How many people are traveling? ").strip()
    budget = input("What is your total budget? (e.g. $2,500) ").strip()
    itinerary = input("What are your interested in doing? (food, adventures, sightseeing, etc.) ").strip()
    departure_city = input("What city are you departing from? ").strip()

    # Check that required details were provided
    if not all([destination, days, travelers, budget, itinerary]):
        print("Please fill in all required trip details.")
        return

    try:
        days_number = int(days)
        travelers_number = int(travelers)

    except ValueError:
        print("Please enter a whole number for days and travelers.")
        return

    if days_number < 1:
        print("Must be at least one day.")
        return

    if travelers_number < 1:
        print("Must be at least one traveler.")
        return

    departure = departure_city \
        if departure_city else "not specified"

    prompt = f"""
Create a practical vacation plan using these details:

Destination: {destination}
Trip duration: {days_number} days
Number of travelers: {travelers_number} people
Total budget: {budget}
Itinerary: {itinerary}
Departure city: {departure}

Organize the response with these sections:

1. TRIP OVERVIEW
Summarize the recommended trip and explain your main assumptions.

2. DAY-BY-DAY ITINERARY
Create a plan for each day. Suggest activities, sights, and food
experiences relevant to the traveler's interests. Group activities
geographically when practical.

3. ESTIMATED BUDGET
Give a breakdown for transportation, lodging, food, activities,
and a contingency buffer. State the currency and whether costs are
for all travelers combined or per person. Make the totals consistent
with the traveler's stated budget as closely as possible.

4. MONEY-SAVING TIPS
Give practical ways to stay within budget.

5. THINGS TO CHECK BEFORE BOOKING
Identify important details the traveler should verify.

Important rules:
- Do not claim to have checked live prices, availability, or bookings.
- Label prices as estimates unless they have been independently verified.
- Explain major assumptions, including whether international airfare
  is included in the budget.
- If the budget is unrealistic for the requested trip, say so honestly
  and suggest adjustments.
- Never claim that reservations or purchases have been made.
"""

    try:
        print("\nTravelAgent is planning your vacation. Please wait...\n")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are TravelAgent, a helpful vacation-planning "
                        "assistant. Follow the traveler's requirements, "
                        "organize your answer clearly, and be honest about "
                        "uncertain prices and information."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
        )

        answer = response.choices[0].message.content

        print("=" * 60)
        print("YOUR TRAVELAGENT VACATION PLAN")
        print("=" * 60)
        print(answer or "The AI returned an empty response.")

    except AuthenticationError:
        print("Authentication failed. Check your Meterless runtime token.")

    except APIConnectionError:
        print("Connection failed. Check that Meterless Runtime is running.")

    except APIStatusError as error:
        print(f"Meterless returned HTTP status {error.status_code}.")
        print(error.message)

    except Exception as error:
        print(f"Unexpected error: {type(error).__name__}")


if __name__ == "__main__":
    plan_vacation()
