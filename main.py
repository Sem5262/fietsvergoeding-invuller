from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])

def process():

    
    # Get the uploaded PDF file from the form
    maandag = request.form.get('maandag')
    dinsdag = request.form.get('dinsdag')
    woensdag = request.form.get('woensdag')
    donderdag = request.form.get('donderdag')
    vrijdag = request.form.get('vrijdag')
    zaterdag = request.form.get('zaterdag')
    zondag = request.form.get('zondag')
    aantal_km = request.form.get('km')
    week = request.form.get('week')
    firstday = get_first_day_of_week(week)

    daylist = [maandag,dinsdag,woensdag,donderdag,vrijdag,zaterdag,zondag]

    uploaded_file = request.files['pdf']

    # Read the uploaded PDF file with PyPDF2
    input_pdf = PdfReader(uploaded_file)

    # Create a BytesIO buffer for the watermark PDF
    watermark_buffer = io.BytesIO()
    
    # Create a new PDF with ReportLab
    can = canvas.Canvas(watermark_buffer, pagesize=letter)
    can.drawString(135, 717, "Begijntjesbad Overijse")
    can.drawString(230, 499, str(aantal_km))
    
    for x in range(7):

        can.drawString(230, 630 - (x*17), add_days_to_date(firstday, x))

        if daylist[x] == 'true':
            can.drawString(510, 637 - (x*17), "___")
        else:
            can.drawString(410, 637 - (x*17), "__")
        
    
    can.save()
    
    # Move to the beginning of the BytesIO buffer
    watermark_buffer.seek(0)
    
    # Read the watermark PDF with PyPDF2
    watermark_pdf = PdfReader(watermark_buffer)
    
    # Create a new PDF writer
    output_pdf = PdfWriter()
    
    # Merge the pages of the input PDF with the watermark PDF
    page = input_pdf.pages[0]
    page.merge_page(watermark_pdf.pages[0])
    output_pdf.add_page(page)
    
    # Save the resulting PDF to a BytesIO buffer
    output_buffer = io.BytesIO()
    output_pdf.write(output_buffer)
    output_buffer.seek(0)
    

    
    # Return the modified PDF file as a downloadable attachment
    return send_file(output_buffer,  as_attachment = True, download_name='fietsvergoeding_'+ week +'.pdf')

def add_days_to_date(date_string, num_days):
    # Parse the input date string into a datetime object
    date_format = "%d/%m/%Y"
    date = datetime.strptime(date_string, date_format)

    # Add the specified number of days to the date
    updated_date = date + timedelta(days=num_days)

    # Convert the updated date back to a string in the same format
    updated_date_string = updated_date.strftime(date_format)

    return updated_date_string



def get_first_day_of_week(year_week):
    year, week = map(int, year_week.split('-W'))
    first_day = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w')
    return first_day.strftime('%d/%m/%Y')


if __name__ == '__main__':
    app.run(debug=True)