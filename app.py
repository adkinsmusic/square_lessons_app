import os
from dotenv import load_dotenv
from square.client import Client
from flask import Flask, request, render_template_string, session, redirect, url_for
from datetime import time

# Load environment variables from the .env file
load_dotenv()

# Retrieve the access token from the environment variable
SQUARE_ACCESS_TOKEN = os.getenv('SQUARE_ACCESS_TOKEN')

# Initialize the Square client with the access token
client = Client(access_token=SQUARE_ACCESS_TOKEN)

app = Flask(__name__)
app.secret_key = 'your_real_secret_key_here'  # Replace with a real secret key for session security

@app.route('/lesson-form', methods=['GET', 'POST'])
def lesson_form():
    instruments = [
        "Piano", "Guitar", "Vocals", "Drums",
        "Banjo", "Bass Guitar", "Brass Horns/WoodWind", "Cello",
        "Clarinet", "Flute", "Oboe", "Percussion Bells",
        "Saxophone", "Trombone", "Trumpet", "Ukulele", "Viola", "Violin"
    ]

    teachers = [
        "Adam Wilson", "Bailey Kuehl", "Chase Jensen", "Eamon Jones", 
        "Jonny Clausing", "Joshua Miller", "Kait Widger", "Raymond Worden", 
        "Reyli Gonzalez", "Sam Howdle"
    ]

    pricing_options = {
        "Appointment Block": 0.00,
        "Regular Price": 40.00,
        "Multi-Student/Military Discount": 35.00,
        "4 or More Sessions Per Week": 32.50
    }

    service_types = {
        "Appointment Block (no charge – for lesson tracking only)": "Appointment Block"
    }

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday", "Sunday"]

    # Generate 30-min time slots from 10:00 AM to 9:00 PM
    times = []
    for hour in range(10, 21):  # 10am to 8pm
        for minute in (0, 30):
            t = time(hour, minute)
            times.append(t.strftime("%I:%M %p"))
    times.append("09:00 PM")  # Add 9:00 PM manually

    # Initialize students in session if it's the first time
    if 'students' not in session:
        session['students'] = []

    # HTML for the form
    form_html = '''
        <h2>New Student Lesson Setup</h2>
        <form method="post">
            <h3>Student Info</h3>
            
            <strong>Student Info</strong><br>
            First Name: <input type="text" name="first_name" required><br><br>
            Last Name: <input type="text" name="last_name" required><br><br>
            Email: <input type="email" name="email" required><br><br>
            Phone Number: <input type="text" name="phone" required><br><br>

            Instrument:
            <select name="instrument" required>
                {% for instrument in instruments %}
                <option value="{{ instrument }}">{{ instrument }}</option>
                {% endfor %}
            </select><br><br>

            Lesson Day:
            <select name="lesson_day" required>
                {% for day in days %}
                <option value="{{ day }}">{{ day }}</option>
                {% endfor %}
            </select><br><br>

            Lesson Time:
            <select name="lesson_time" required>
                {% for time in times %}
                <option value="{{ time }}">{{ time }}</option>
                {% endfor %}
            </select><br><br>

            Teacher:
            <select name="teacher" required>
                {% for teacher in teachers %}
                <option value="{{ teacher }}">{{ teacher }}</option>
                {% endfor %}
            </select><br><br>

            Start Date: <input type="date" name="start_date" required><br><br>

            Pricing Option:
            <select name="price_option" required>
                {% for option, value in pricing_options.items() %}
                <option value="{{ option }}">{{ option }} - ${{ '{:.2f}'.format(value) }}</option>
                {% endfor %}
            </select><br><br>

            Number of Lessons:
            <select name="weeks" required>
                {% for w in range(1, 9) %}
                <option value="{{ w }}">{{ w }}</option>
                {% endfor %}
            </select><br><br>

            <strong>Appointment Service Type</strong><br>
            <select name="appointment_service_type" required>
                {% for label, value in service_types.items() %}
                <option value="{{ value }}">{{ label }}</option>
                {% endfor %}
            </select><br><br>

            <strong>Parent Info (Optional)</strong><br>
            Parent Name: <input type="text" name="parent_name"><br><br>
            Parent Contact: <input type="text" name="parent_contact"><br><br>

            <strong>Address (Optional)</strong><br>
            Street Address: <input type="text" name="address_line1"><br><br>
            City: <input type="text" name="city"><br><br>
            State: <input type="text" name="state"><br><br>
            ZIP Code: <input type="text" name="zip"><br><br>

            <input type="submit" value="Add Student {{ students|length + 1 }}">
        </form>
        <form method="POST" action="/generate-invoice">
            <input type="submit" value="Generate Invoice">
        </form>
    '''

    # Handle POST request (form submission)
    if request.method == 'POST':
        student_data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'instrument': request.form['instrument'],
            'lesson_day': request.form['lesson_day'],
            'lesson_time': request.form['lesson_time'],
            'teacher': request.form['teacher'],
            'start_date': request.form['start_date'],
            'price_option': request.form['price_option'],
            'price': pricing_options[request.form['price_option']],
            'weeks': request.form['weeks']
        }

        # Add student to the session (this stores them for later use)
        session['students'].append(student_data)

        # Create the customer in Square (You could store customer data here or send it to Square)
        create_square_customer(student_data['first_name'], student_data['last_name'], student_data['email'], student_data['phone'])

        return render_template_string(form_html, students=session['students'], instruments=instruments, pricing_options=pricing_options, days=days, times=times, teachers=teachers, service_types=service_types)

    return render_template_string(form_html, students=session['students'], instruments=instruments, pricing_options=pricing_options, days=days, times=times, teachers=teachers, service_types=service_types)


@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    """This is where you would handle invoice generation."""
    students = session.get('students', [])
    if students:
        student = students[-1]  # Get the most recent student
        # Create the invoice in Square
        create_square_invoice(student)

        # Redirect to a success page or display a confirmation
        return render_template_string("<h2>Invoice Created Successfully for {{ student['first_name'] }} {{ student['last_name'] }}!</h2>", student=student)

    return "No student data found.", 400


def create_square_customer(first_name, last_name, email, phone):
    """Create a customer in Square using the data from the form."""
    try:
        response = client.customers.create_customer(
            given_name=first_name,
            family_name=last_name,
            email_address=email,
            phone_number=phone
        )
        print("Customer created successfully:", response)
        return response
    except Exception as e:
        print("Error creating customer:", e)
        return None


def create_square_invoice(student):
    """Create an invoice in Square."""
    try:
        invoice_data = {
            'order': {
                'line_items': [
                    {
                        'name': f"{student['instrument']} Lesson",
                        'quantity': '1',
                        'base_price_money': {
                            'amount': int(student['price'] * 100),  # Price in cents
                            'currency': 'USD'
                        }
                    }
                ],
                'location_id': 'your-location-id',  # Replace with your Square location ID
            },
            'primary_recipient': {
                'customer_id': 'your-customer-id'  # Replace with the customer ID created earlier
            }
        }
        response = client.invoices.create_invoice(invoice_data)
        print("Invoice created successfully:", response)
        return response
    except Exception as e:
        print("Error creating invoice:", e)
        return None


if __name__ == '__main__':
    app.run(debug=True)
