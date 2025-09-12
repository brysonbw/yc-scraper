from dotenv import dotenv_values
import json
import os

config = dotenv_values(".env")
scrape_report_json_file = "scrape_report.json"
scrape_output_json_file_path = os.path.join(config["SCRAPE_OUTPUT_DIR"], config["SCRAPE_OUTPUT_JSON_FILE"])
scrape_report_json_file_path = os.path.join(config["SCRAPE_OUTPUT_DIR"], scrape_report_json_file)

if os.path.exists(scrape_output_json_file_path):
    # Load json file
    with open(scrape_output_json_file_path, "r") as file:
        objects = json.load(file)

    # Total objects
    total_count = len(objects)

    # Collect IDs
    ids = [obj["id"] for obj in objects]
    id_set = set(ids)

    # Find missing IDs
    full_range = range(min(ids), max(ids) + 1)
    missing_ids = [i for i in full_range if i not in id_set]

    # Find objects with null region and null location lat/long
    region_null_ids = []
    location_null_ids = []

    for obj in objects:
        if obj.get("region") is None:
            region_null_ids.append(obj["id"])

        location = obj.get("location")
        if location is None or location.get("latitude") is None or location.get("longitude") is None:
            location_null_ids.append(obj["id"])

    # Calculate percentages
    percentage_missing = (len(missing_ids) / (max(ids) - min(ids) + 1)) * 100
    region_null_percent = (len(region_null_ids) / total_count) * 100
    location_null_percent = (len(location_null_ids) / total_count) * 100
    percentage_success = 100 - percentage_missing  # Success based on IDs present

    # Prepare result
    result = {
        "missing_company_ids": missing_ids,
        "percentage_missing": round(percentage_missing, 2),
        "region_null_ids": region_null_ids,
        "region_null_ids_count": len(region_null_ids),
        "region_null_percent": round(region_null_percent, 2),
        "location_null_ids": location_null_ids,
        "location_null_ids_count": len(location_null_ids),
        "location_null_percent": round(location_null_percent, 2),
        "scrape_success_percentage": round(percentage_success, 2)
    }

    # Write data to json file
    with open(scrape_report_json_file_path, "w") as f:
        json.dump(result, f)

    print(f"Exit: Saved results to {scrape_report_json_file_path}")
else:
    print(f"! Error: File {scrape_output_json_file_path} does not exist. Please check the path")
