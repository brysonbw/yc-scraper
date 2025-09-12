import os
import json
import requests
from dotenv import dotenv_values
from pathlib import Path

config = dotenv_values(".env")
scrape_output_json_file_path = os.path.join(config["SCRAPE_OUTPUT_DIR"], config["SCRAPE_OUTPUT_JSON_FILE"])

# Setup images output
OUTPUT_DIR_COMPANY_LOGOS = f"{config["SCRAPE_OUTPUT_DIR"]}/images/logos"
OUTPUT_DIR_COMPANY_FOUNDER_AVATARS = f"{config["SCRAPE_OUTPUT_DIR"]}/images/avatars"
OUTPUT_DIR_COMPANY_PHOTOS = f"{config["SCRAPE_OUTPUT_DIR"]}/images/company_photos"

Path(OUTPUT_DIR_COMPANY_LOGOS).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR_COMPANY_FOUNDER_AVATARS).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_DIR_COMPANY_PHOTOS).mkdir(parents=True, exist_ok=True)

def safe_filename(name: str) -> str:
    """Turn filename into a safe filename"""
    return "".join(c if c.isalnum() else "_" for c in name).lower()

if os.path.exists(scrape_output_json_file_path):
  # Load json
    with open(scrape_output_json_file_path, "r", encoding="utf-8") as f:
        yc_companies = json.load(f)

    for company in yc_companies:
        id = company.get("id")
        name = company.get("name", f"unknown_{id}")
        print(f"=== Images for ({id}) {name.upper()} ===")
        logo_url = company.get("logo")
        founders = company.get("founders", [])
        company_photos = company.get("company_photos", [])

        # Download company logo
        if logo_url:
            fileExt = "png"
            filename = f"{safe_filename(name)}_{id}"
            filepath = os.path.join(OUTPUT_DIR_COMPANY_LOGOS, f"{filename}.{fileExt}")

            if not os.path.exists(filepath):
                try:
                    print(f"Downloading company logo for ({id}) {name.upper()}...")
                    response = requests.get(logo_url, timeout=10)
                    response.raise_for_status()
                    with open(filepath, "wb") as out:
                        out.write(response.content)
                    company["logo"] = f"{filename}"  # Update prop value
                except Exception as e:
                    print(f"! Error: Failed to download logo for {name.upper()}: {e}")
                    company["logo"] = None
            else:
                print(f"Info: Logo already exists for {name.upper()}, skipping...")

        # Download founder avatars
        for founder in founders:
            id = founder.get("id")
            founder_name = founder.get("name", f"unknown_founder_{id}")
            avatar_url = founder.get("avatar")
            if avatar_url:
                fileExt = "png"
                filename = f"{safe_filename(name)}_{safe_filename(founder_name)}_{id}"
                filepath = os.path.join(OUTPUT_DIR_COMPANY_FOUNDER_AVATARS, f"{filename}.{fileExt}")

                if not os.path.exists(filepath):
                    try:
                        print(f"Downloading avatar for ({id}) founder [{founder_name}] ({name.upper()})...")
                        response = requests.get(avatar_url, timeout=10)
                        response.raise_for_status()
                        with open(filepath, "wb") as out:
                            out.write(response.content)
                        founder["avatar"] = f"{filename}" # Update prop value
                    except Exception as e:
                        print(f"! Error: Failed to download avatar for {founder_name}: {e}")
                        founder["avatar"] = None
                else:
                    print(f"Info: Avatar already exists for {founder_name}, skipping...")

        # Download company photos
        for idx, photo_url in enumerate(company_photos):
            if photo_url:
                fileExt = "png"
                filename = f"{safe_filename(name)}_company_photo_{idx + 1}"
                filepath = os.path.join(OUTPUT_DIR_COMPANY_PHOTOS, f"{filename}.{fileExt}")

                if not os.path.exists(filepath):
                    try:
                        print(f"Downloading company photo for ({idx + 1}) {name.upper()}...")
                        response = requests.get(photo_url, timeout=10)
                        response.raise_for_status()
                        with open(filepath, "wb") as out:
                            out.write(response.content)
                        company_photos[idx] = f"{filename}"  # Update prop value
                    except Exception as e:
                        print(f"! Error: Failed to download company photo for {name.upper()}: {e}\n")
                        company_photos[idx] = None
                else:
                    print(f"Info: Company photo already exists for {name.upper()}, skipping...")
    
        print("Done!\n\n")

    # Save updated json object data/prop value with filename value
    with open(f"{config["SCRAPE_OUTPUT_DIR"]}/{config["SCRAPE_OUTPUT_JSON_FILE"].replace(".json", "")}_local.json", "w", encoding="utf-8") as f:
        json.dump(yc_companies, f, ensure_ascii=False, indent=4)

    print(f"Exit: Saved updated results to {config["SCRAPE_OUTPUT_DIR"]}/{config["SCRAPE_OUTPUT_JSON_FILE"].replace(".json", "")}_local.json")
else:
    print(f"! Error: File {scrape_output_json_file_path} does not exist. Please check the path")