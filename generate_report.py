from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
import pdfkit
import os
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_PDF = os.path.join(BASE_DIR, "report.pdf")
TEMP_HTML = os.path.join(BASE_DIR, "temp_combined.html")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# wkhtmltopdf path (change if needed)
pdf_config = pdfkit.configuration(wkhtmltopdf='C:/Users/Neil Advani/Downloads/wkhtmltox-0.12.6-1.mxe-cross-win64/wkhtmltox/bin/wkhtmltopdf.exe')

def extract_weather_data(html):
    # Extract values using regex (assuming JS has already populated static values)
    temp = re.search(r'id="temp">([\d.]+)', html)
    humidity = re.search(r'id="humidity">([\d.]+)', html)
    wind = re.search(r'id="wind">([\d.]+)', html)
    alert = re.search(r'id="alertMessage">(.*?)<', html)

    return {
        "temperature": temp.group(1) + " °C" if temp else "N/A",
        "humidity": humidity.group(1) + " %" if humidity else "N/A",
        "wind_speed": wind.group(1) + " km/h" if wind else "N/A",
        "alert": alert.group(1) if alert else "N/A"
    }

@app.get("/generate-pdf")
def generate_pdf():
    try:
        with open("weather monitoring.html", "r", encoding="utf-8") as f:
            weather_html = f.read()

        with open("sensor page (1).html", "r", encoding="utf-8") as f:
            sensor_html = f.read()

        # Extract weather data
        weather_data = extract_weather_data(weather_html)

        # Render template with real values
        template = env.get_template("report_template.html")
        html_out = template.render(weather=weather_data, sensor=sensor_html)

        # Save rendered HTML
        with open(TEMP_HTML, "w", encoding="utf-8") as f:
            f.write(html_out)

        # Generate PDF
        pdfkit.from_file(TEMP_HTML, OUTPUT_PDF, configuration=pdf_config)

        return FileResponse(OUTPUT_PDF, media_type='application/pdf', filename="SmartFarming_Report.pdf")

    except Exception as e:
        return {"error": f"Failed to generate PDF: {str(e)}"}
