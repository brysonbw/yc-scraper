from dotenv import dotenv_values
import requests
import json
import time
import os

config = dotenv_values(".env")
scrape_output_json_file_path = os.path.join(config["SCRAPE_OUTPUT_DIR"], config["SCRAPE_OUTPUT_JSON_FILE"])

API_KEY = config["API_KEY"]
PLACES_URL = config["PLACES_API_URL"]
FIELD_MASK = "places.location,places.shortFormattedAddress,places.formattedAddress,places.shortFormattedAddress"

def get_company_place_info(company_name, company_region):
    """Call Places API to get place info for a yc company."""
    result = {
        "latitude": None,
        "longitude": None,
        "long_address": None,
        "short_address": None
    }

    if not company_name or not company_region:
        print(f"Info: Company name or region not found - returning default location prop/data")
        return result
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": FIELD_MASK
    }

    payload = {"textQuery": f"{company_name} {company_region}"}

    response = requests.post(PLACES_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        if "places" in data and data["places"]:
            place = data["places"][0]
            if "location" in place and place["location"] is not None:
                if "latitude" in place["location"] and place["location"]["latitude"] is not None:
                    result["latitude"] = place["location"]["latitude"]
                if "longitude" in place["location"] and place["location"]["longitude"] is not None:
                    result["longitude"] = place["location"]["longitude"]
            if "formattedAddress" in place and place["formattedAddress"] is not None:
                result["long_address"] = place["formattedAddress"]
            if "shortFormattedAddress" in place and place["shortFormattedAddress"] is not None:
                result["short_address"] = place["shortFormattedAddress"]
                
    return result

if os.path.exists(scrape_output_json_file_path):
    # Load json file
    with open(scrape_output_json_file_path, "r", encoding="utf-8") as f:
        yc_companies = json.load(f)

    # Fetch place info for each company
    for company in yc_companies:
        id = company.get("id")
        name = company.get("name")
        region = company.get("region")
        print(f"=== Attempting to get place info for ({id}) {name.upper()} ===")
        result = get_company_place_info(name, region)
        company["location"] = result
        print(f"Done -> {result}\n\n")
        time.sleep(0.1)  # Small delay to avoid possibly hitting rate limits

    # Write the updated data back to the json file
    with open(scrape_output_json_file_path, "w", encoding="utf-8") as f:
        json.dump(yc_companies, f, ensure_ascii=False, indent=4)

    print(f"Exit: Saved updated results to {scrape_output_json_file_path}")
else:
    print(f"! Error: File {scrape_output_json_file_path} does not exist. Please check the path")