# YC Scraper

A collection of python scripts to scrape [Y Combinator Startup Directory](https://www.ycombinator.com/companies).

![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-orange)
---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage) 
  - [Run scraper](#run-scraper)
  - [Get location data for yc companies](#get-location-data-for-yc-companies)
  - [Download yc company images *(optional)*](#download-yc-company-images-optional)
  - [Generate scrape report](#generate-scrape-report)
- [Contributing](#contributing)
- [License](#license)
  
---

## Installation

1. **Clone repository**

    ```bash
    git clone https://github.com/brysonbw/yc-scraper yc_scraper
    ```

    ```bash
    cd yc_scraper
    ```

2. **Create virtual environment**

    ```bash
    python3 -m venv .venv
    ```

3. **Activate environment**

    ```bash
    source .venv/bin/activate
    ```

4. **Verify**
    > Path should include where you've cloned the repository.

    ```bash
    which python
    ```

5. **Prepare pip**

    ```bash
    python3 -m pip install --upgrade pip
    ```

6. **Install required packages**

    ```bash
    python3 -m pip install -r requirements.txt
    ```

    **Check outdated packges**

    ```bash
    pip list --outdated
    ```

    **Upgrade package**

    ```bash
    python3 -m pip install --upgrade <package_name>
    ```

7. **Create enviornment variables**

    1. Create `.env` from `.env.example`

        ```bash
        cp .env.example .env && rm .env.example
        ```

    2. Update and replace placeholder value for each variable

        ```bash
        SCRAPE_OUTPUT_DIR="<OUTPUT_FOLDER_NAME_VALUE>" # The folder where `scrape_yc.py` and `scrape_report.py` will output results
        SCRAPE_OUTPUT_JSON_FILE="<OUTPUT_JSON_FILE_NAME_VALUE>" # The json file where `scrape_yc.py` and `scrape_report.py` will output results
        API_KEY="<API_KEY_VALUE>" # API key for the places api to fetch yc company location (coordinates) data
        PLACES_API_URL="<PLACES_API_URL_VALUE>" # Places api url (e.g Google Places API, Foursquare Places API, ect) - endpoint to fetch company location (coordinates) data
        ```

## Usage

### Run scraper

> **Note**: Before running the script, install a [WebDriver](https://developer.mozilla.org/en-US/docs/Web/WebDriver) (if you haven't done so already). Script import's Firefox's [geckodriver](https://github.com/mozilla/geckodriver). If you decide to use a different WebDriver (e.g [ChromeDriver](https://developer.chrome.com/docs/chromedriver/downloads)) - modify [scrape_yc.py](scrape_yc.py).

```bash
python scrape_yc.py
```

### Get location data for yc companies

> **Note**: The script calls [Google Places (new) API](https://developers.google.com/maps/documentation/places/web-service/op-overview) to fetch company location data. If you decide to use a different API (e.g [Foursquare Places API](https://docs.foursquare.com/data-products/docs/places-api)) - modify [get_company_place_info.py](get_company_place_info.py).

```bash
python get_company_place_info.py
```

### Download yc company images *(optional)* 

> **Note**: The script downloads images from the provided scraped URL(s), specifically for these properties: `logo`, `founder["avatar"]`, and `company_photos`.

```bash
python dl_company_images.py
```

The script will save images in `SCRAPE_OUTPUT_DIR/images` with the following sub folders (which you can change if you like): `/avatars`, `/company_photos`, and `/logos`

### Generate scrape report

```bash
python scrape_report.py
```

## Contributing

If you have suggestions for how this project could be improved, or want to report a bug, feel free to open an issue! We welcome all contributions.

Also, feel free to contribute to the [YC Startup Map repository](https://github.com/brysonbw/yc-startup-map), which visualizes the collected and scraped data.

## License

[Apache 2.0](LICENSE)
