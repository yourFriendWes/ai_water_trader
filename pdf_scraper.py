import requests, re
from bs4 import BeautifulSoup
import pdfplumber
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIG ===
BASE_URL = "https://veleswater.com/veles-weekly-report-archive/"
GOOGLE_SHEET_NAME = "Water Market Data"   # Existing Google Sheet name
WORKSHEET_NAME = "Veles Weekly Reports"   # Tab name for the data

# === STEP 1: SCRAPE LATEST VELES WEEKLY REPORT ===
html = requests.get(BASE_URL).text
soup = BeautifulSoup(html, "html.parser")
pdf_link = soup.find("a", href=True, text=re.compile(r"Weekly Report", re.I))['href']

# Download PDF
pdf_file = "veles_weekly.pdf"
with open(pdf_file, "wb") as f:
    f.write(requests.get(pdf_link).content)

# Extract price and report date from PDF
with pdfplumber.open(pdf_file) as pdf:
    text = "\n".join(page.extract_text() for page in pdf.pages)

# Find price
price_match = re.search(r"NQH2O.*?\$?(\d+\.?\d*)", text)
price = float(price_match.group(1)) if price_match else None

# Find report date (if listed)
date_match = re.search(r"Week Ending[: ]+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
report_date = date_match.group(1) if date_match else "Unknown"

print(f"Report Date: {report_date}")
print(f"NQH₂O Price: ${price}/AF")

# === STEP 2: CONNECT TO GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the existing sheet
spreadsheet = client.open(GOOGLE_SHEET_NAME)

# Create or open the 'Veles Weekly Reports' tab
try:
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
except gspread.exceptions.WorksheetNotFound:
    worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows="100", cols="5")
    worksheet.append_row(["Report Date", "NQH₂O Price ($/AF)", "PDF Link", "Extracted Text Preview"])

# === STEP 3: APPEND DATA TO SHEET ===
preview_text = text[:200] + "..."  # short preview of extracted text
worksheet.append_row([report_date, price, pdf_link, preview_text])

print(f"✅ Uploaded Veles Weekly Report ({report_date}) to Google Sheet tab '{WORKSHEET_NAME}'")
