from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from dotenv import dotenv_values
from urllib.parse import urlparse, urlunparse
import time
import os
import json


config = dotenv_values(".env")

# Setup headless Firefox
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# Setup scraped data output folder/files
output_folder = config["SCRAPE_OUTPUT_DIR"]
os.makedirs(output_folder, exist_ok=True)
scrape_output_json_file_path = os.path.join(output_folder, config["SCRAPE_OUTPUT_JSON_FILE"])

# Setup data map to populate while scraping
yc_companies_map = {}

# Prep before scraping
# Go to yc companies page
driver.get("https://www.ycombinator.com/companies")

# Wait for page to load
time.sleep(5)

# Scroll to fetch yc cards - stop when end reached
SCROLL_PAUSE_TIME = 2
MAX_SCROLLS = None
scroll_count = 0
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    # Increment scroll counter
    scroll_count += 1
    
    # Get new scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    # Check if more content loaded
    if new_height == last_height or (MAX_SCROLLS is not None and scroll_count >= MAX_SCROLLS):
        break  # No new items loaded, exit loop
    last_height = new_height

print(f"Scrolled page {scroll_count} times\n\n")


# Get all yc cards (a tags)
links = driver.find_elements(By.CSS_SELECTOR, "._rightCol_i9oky_592 a._company_i9oky_355")

# Start scraping
for idx, link in enumerate(links, start=1):
    try:
        # Get basic company info within card
        name = link.find_element(By.CSS_SELECTOR, "._coName_i9oky_470").text.strip()
        print(f"=== Scraping ({idx}) {name.upper() or "None"} ===")
        try:
            logo_url = link.find_element(By.TAG_NAME, "img").get_attribute("src")
        except:
            logo_url = None
        description = link.find_element(By.CSS_SELECTOR, ".text-sm").text.strip()
        pill_links = link.find_element(By.CSS_SELECTOR, "._pillWrapper_i9oky_33").find_elements(By.CSS_SELECTOR, "a")

        # Create record along with other prop/fields for current company
        yc_companies_map[idx] = {
            "id": idx,
            "name": name,
            "yc_page_url": link.get_attribute("href"),
            "logo": logo_url,
            "description": description,
            "about": None,
            "founded": None,
            "batch": None,
            "team_size": None,
            "status": None,
            "region": None,
            "primary_partner": None,
            "company_pages": [],
            "company_photos": [],
            "industry": [],
            "founders": [],
        }

        # Populate 'industry'
        if pill_links and len(pill_links) > 0:
            for a in pill_links[1:]:
                industry_text = a.text.strip()
                yc_companies_map[idx]["industry"] += [f"{industry_text}"]

        # Go to yc company detail page
        driver.get(link.get_attribute("href"))
        time.sleep(2)  # Wait for page to load, increase if needed

        # Populate `about`
        whitespace_pre_line_divs = driver.find_elements(By.CSS_SELECTOR, "div.whitespace-pre-line")
        if whitespace_pre_line_divs and len(whitespace_pre_line_divs) > 0:
            first_div = whitespace_pre_line_divs[0] 
            parent = first_div.find_element(By.XPATH, "..")
            parent_classes = parent.get_attribute("class").split()

            # Check if divs valid
            if first_div and parent and "prose" in parent_classes:
                about_text = first_div.text.replace("\t", " ").strip()
                yc_companies_map[idx]["about"] = about_text

        # Populate `company_photos`
        company_photo_imgs = driver.find_elements(By.XPATH, '//img[@alt="Company photo"]')
        if company_photo_imgs and len(company_photo_imgs) > 0:
            for img in company_photo_imgs:
                company_photo_url = img.get_attribute("src")
                if company_photo_url:
                    parsed_url = urlparse(company_photo_url)
                    clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
                    yc_companies_map[idx]["company_photos"] += [clean_url]

        # Company card
        company_card = driver.find_element(By.XPATH,f"//div[contains(@class, 'ycdc-card-new') and contains(., '{name}')]")
        # Company information divs
        company_info_div = company_card.find_element(By.XPATH,"//div[contains(@class, 'space-y-2')]")
        company_info_child_divs = company_info_div.find_elements(By.CSS_SELECTOR, "div.justify-between")
        # Company links
        company_info_links_div = company_info_div.find_element(By.CSS_SELECTOR, "div.items-center")
        company_info_links = company_info_links_div.find_elements(By.TAG_NAME, "a")
        # Company industry pill/links
        company_industry_links = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/companies/industry"]')

        # Populate `company_pages`
        if company_info_links is not None and len(company_info_links) > 0:
            for link in company_info_links:
                aria_label = link.get_attribute("aria-label").replace("account", "").replace("profile", "").replace("(Twitter)", "").strip()
                href = link.get_attribute("href")
                if aria_label and href:
                    yc_companies_map[idx]["company_pages"] += [{ "platform": aria_label, "url": href }]
    
        # Populate additional industry pills for company on detail page for `industry`
        if company_industry_links is not None and len(company_industry_links) > 0:
            for link in company_industry_links:
                industryToUpper = link.text.strip().upper()
                if industryToUpper and industryToUpper not in yc_companies_map[idx]["industry"]:
                    yc_companies_map[idx]["industry"]+= [industryToUpper]

        # Populate company info key/value pairs in div: `founded`, `batch`, `team_size`, `status`, `region`, and `primary_partner`
        if company_info_child_divs is not None and len(company_info_child_divs) > 0:
            for div in company_info_child_divs:
                pairs = div.find_elements(By.XPATH, "./*")
                if len(pairs) >= 2:
                    key = pairs[0].text.strip()
                    value = pairs[1].text.strip()
                    if key.lower().replace(":", "") == "location": #? Saving as 'region' because will populate 'location' prop from script to call places api that get's exact location data after scraping -> see get_company_place_info.py
                        yc_companies_map[idx]["region"] = value
                    else:
                        yc_companies_map[idx][key.lower().replace(":", "").replace(" ", "_")] = value
                else:
                    print(f"! Error: Company info (key/pairs) [{key} {value}] not accounted for\n")
        
        # Check if founder(s) card present - look for 'Founders' or 'Active Founders' text in DOM
        company_founder_cards = None
        if "Founders" or "Active Founders" in driver.page_source:
            company_founder_cards = driver.find_elements(By.XPATH,f"//div[contains(@class, 'ycdc-card-new') and contains(@class, 'w-full') and contains(@class, 'space-y-1.5')]")
        
        # Gather yc founder information/data - populating company `founders[{id, name, ect...}]` prop/data
        if company_founder_cards is not None and len(company_founder_cards) > 0:
            for fc_idx, founder_card in enumerate(company_founder_cards):
                # Create default prop/fields for current company `founders` prop/data
                yc_companies_map[idx]["founders"] += [
                    {
                        "id": fc_idx + 1, 
                        "name": None,
                        "bio": None,
                        "avatar": None,
                        "job_title": None,
                        "social_media_profiles": []
                    }
                ]
                # Loop through `founder_card_divs` for each founder card
                founder_card_divs = founder_card.find_elements(By.CSS_SELECTOR, "div")
                for div_idx, div in enumerate(founder_card_divs):
                    # Populate 'avatar'
                    if "aspect-square" in div.get_attribute("class").split() and div.find_element(By.TAG_NAME, "img").get_attribute("src"):
                        avatar_url = div.find_element(By.TAG_NAME, "img").get_attribute("src")
                        parsed_url = urlparse(avatar_url)
                        clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
                        yc_companies_map[idx]["founders"][fc_idx]["avatar"] = clean_url
                    # Loop through `founder_additional_info_divs` within founder card divs
                    if "flex-1" in div.get_attribute("class").split():
                        founder_additional_info_divs = div.find_elements(By.CSS_SELECTOR, "div")
                        if len(founder_additional_info_divs) > 0:
                            for div in founder_additional_info_divs:
                                # Populate `name`
                                if "font-bold" in div.get_attribute("class").split():
                                    yc_companies_map[idx]["founders"][fc_idx]["name"] = div.text.strip()
                                # Populate `job_title`
                                if "pt-1" in div.get_attribute("class").split():
                                    yc_companies_map[idx]["founders"][fc_idx]["job_title"] = div.text.strip()
                                # Populate `bio`
                                if "whitespace-pre-line" in div.get_attribute("class").split():
                                    yc_companies_map[idx]["founders"][fc_idx]["bio"] = div.text.replace("\t", " ").strip()
                                # Populate `social_media_profiles`
                                if "gap-2" in div.get_attribute("class").split():
                                    founder_social_links = div.find_elements(By.TAG_NAME, "a")
                                    if founder_social_links is not None and len(founder_social_links) > 0:
                                        for link in founder_social_links:
                                            aria_label = link.get_attribute("aria-label").replace("account", "").replace("profile", "").replace("Twitter", "X").strip()
                                            href = link.get_attribute("href")
                                            if aria_label and href:
                                                yc_companies_map[idx]["founders"][fc_idx]["social_media_profiles"] += [{ "platform": aria_label, "url": href }]
        
        driver.back() # Go back to yc companies page
        time.sleep(2)  # Wait for page to load, increase if needed

        print(f"Done!\n")

    except Exception as e:
        #! If failure - log and continue to next company in iteration
        print(f"! Error: Exit scraping - unable to populate data for ({idx}) {name.upper() or "None"} \n")
        continue


driver.quit()

print(f"\n\nScraping done - writing data to json file...\n\n")
with open(scrape_output_json_file_path, "w", encoding="utf-8") as f:
    json.dump(list(yc_companies_map.values()), f, indent=4, ensure_ascii=False)

print(f"Exit: Saved results to {scrape_output_json_file_path}")