# Brain.com.ua Product Parser

A Django-based scraping project for extracting product specifications, prices, and images from **brain.com.ua** using three different approaches (`Requests + BeautifulSoup`, `Selenium`, and `Playwright`) and storing the collected data in PostgreSQL.

## Project Structure

```text
braincomua_project/
├── braincomua_project/   # Django project settings & configuration
├── parser_app/           # Django app with Product/Phone model & migrations
├── modules/              # Standalone scraping scripts
│   ├── load_django.py           # Django ORM environment initializer
│   ├── 1_get_info_bs.py         # Parser using Requests + BeautifulSoup4
│   ├── 2_get_info_selenium.py   # Parser using SeleniumBase (Undetected Chrome)
│   └── 3_get_info_playwright.py # Parser using Playwright
├── results/              # Exported PostgreSQL dump (.sql) and CSV data (.csv)
├── .env.example          # Environment variables template
├── manage.py
└── requirements.txt
```

## Setup & Installation

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone https://github.com/VladimirDolhyi/braincomua_project.git
   cd braincomua_project
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies and Playwright browsers:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env` and set your PostgreSQL credentials:
   ```bash
   cp .env.example .env
   ```

5. **Apply database migrations:**
   Make sure PostgreSQL is running and the target database (`DB_NAME`) is created, then run:
   ```bash
   python manage.py migrate
   ```

## Running the Parsers

Run any of the scraping scripts from the project root:

```bash
python modules/1_get_info_bs.py
python modules/2_get_info_selenium.py
python modules/3_get_info_playwright.py
```

## Results

Pre-exported database dump and parsed records are available in the `results/` directory:
- `results/braincomua_db.sql`
- `results/braincomua_phones.csv`
