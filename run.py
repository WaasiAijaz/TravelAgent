import os
import sys
import re
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


# Convert trip durations into days
def parse_trip_duration(user_input):
    user_input = user_input.lower().strip()

    if user_input.isdigit():
        days = int(user_input)
        return days if days > 0 else None

    # Accept days, weeks, or both
    pattern = (
        r"(?:(\d+)\s*(?:weeks?|wks?))?"
        r"(?:\s*(?:and\s+)?(\d+)\s*(?:days?|d))?"
    )

    match = re.fullmatch(pattern, user_input)

    if not match or not any(match.groups()):
        return None

    weeks = int(match.group(1) or 0)
    days = int(match.group(2) or 0)

    total_days = weeks * 7 + days

    return total_days if total_days > 0 else None


def plan_vacation():
    print("\n=== Welcome to TravelAgent ===")
    print("Let's plan your next vacation!\n")

    destination = input("Where would you like to travel to? ").strip()

    # Accept flexible trip durations
    while True:
        duration_input = input(
            "How long is your trip? (e.g., 5 days, 2 weeks): "
        ).strip()

        days_number = parse_trip_duration(duration_input)

        if days_number is not None:
            break

        print("Please enter a valid duration, such as 5 days or 2 weeks.")

    travelers = input("How many people are traveling? ").strip()

    budget = input("What is your total budget? (e.g. $2,500) ").strip()

    itinerary = input(
        "What are you interested in doing? "
        "(shopping, adventures, sightseeing, etc.) "
    ).strip()

    food = input(
        "Any dietary restrictions or food preferences? "
        "(e.g., halal meat only, vegetarian, vegan, allergies, or none): "
    ).strip()

    if not food:
        food = "No specific dietary restrictions or food preferences provided."

    departure_city = input("What city are you departing from? ").strip()

    # Check that required details were provided
    if not all([destination, travelers, budget, itinerary]):
        print("Please fill in all required trip details.")
        return

    try:
        travelers_number = int(travelers)

    except ValueError:
        print("Please enter a whole number for travelers.")
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
Dietary restrictions: {food}
Departure city: {departure}

Organize the response with these sections:

1. TRIP OVERVIEW
Summarize the recommended trip and explain your main assumptions.

2. DAY-BY-DAY ITINERARY
Create a plan for EVERY day of the trip, from Day 1 through
Day {days_number}.

Do not skip any days.

Suggest activities, sights, and food experiences relevant to
the traveler's interests.

Group activities geographically when practical.

For longer trips, keep each day's description concise enough
to include all requested days.

3. ESTIMATED BUDGET
Give a breakdown for transportation, lodging, food, activities,
and a contingency buffer.

State the currency and whether costs are for all travelers
combined or per person.

Make the totals consistent with the traveler's stated budget
as closely as possible.

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
- Treat dietary restrictions as requirements, not optional preferences.
- If the traveler requests halal meat only, recommend halal food options
  and do not suggest non-halal meat dishes.
- If the traveler is vegetarian, do not recommend meat or fish dishes.
- Respect vegan and other explicitly stated dietary restrictions.
- Do not assume a restaurant is halal or meets another dietary standard
  without reliable verification.
- If dietary compliance cannot be verified, clearly tell the traveler
  to confirm directly with the restaurant before visiting.
"""

    try:
        print("\nTravelAgent is planning your vacation. Please wait...\n")

        # Allow longer responses for longer trips
        max_output_tokens = min(
            8000,
            max(2000, days_number * 350)
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are TravelAgent, a helpful vacation-planning "
                        "assistant. Follow the traveler's requirements, "
                        "organize your answer clearly, and be honest about "
                        "uncertain prices and information. "
                        "Provide a separate itinerary for every requested day."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_output_tokens,
        )

        answer = response.choices[0].message.content

        print("=" * 60)
        print("YOUR TRAVELAGENT VACATION PLAN")
        print("=" * 60)
        print(answer or "The AI returned an empty response.")

        if response.choices[0].finish_reason == "length":
            print(
                "\nNote: The response reached the output limit. "
                "Some itinerary details may be missing."
            )

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
