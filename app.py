import os
from dotenv import load_dotenv
from square.client import Client
from flask import Flask, request, render_template_string, session, redirect, url_for
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Retrieve the access token and location ID from environment variables
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
SQUARE_ACCESS_TOKEN = os.getenv('SQUARE_ACCESS_TOKEN')
SQUARE_LOCATION_ID = os.getenv('SQUARE_LOCATION_ID')

# Initialize the Square client with the access token
client = Client(access_token=SQUARE_ACCESS_TOKEN)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY  # Secret key for session management

# Mapping for pricing options (from dropdown text to actual dollar value)
price_mapping = {
    "Appointment Block": 0.0,  # $0 for appointment block
    "Regular Price": 40.0,      # $40 for regular price
    "Multi-Student/Military Discount": 35.0,  # $35 for multi-student/military discount
    "4 or More Sessions Per Week": 32.50  # $32.50 for 4 or more sessions per week
}

@app.route('/lesson-form', methods=['GET', 'POST'])
def lesson_form():
    # Define options for the form
    instruments = [
        "Piano", "Guitar", "Vocals", "Drums",
        "Banjo", "Bass Guitar", "Brass Horns/WoodWind", "Cello",
        "Clarinet", "Flute", "Oboe", "Percussion Bells",
        "Saxophone", "Trombone", "Trumpet", "Ukulele", "Viola", "Violin"
    ]
    teachers = [
        "Adam Wilson", "Bailey Kuehl", "Chase Jensen", "Jonny Clausing",
        "Eamon Jones", "Raymond Worden", "Joshua Miller", "Kait Widger"
    ]
    pricing_options = [
        "Appointment Block ($0)", "Regular Price ($40)", "Multi-Student/Military Discount ($35)", "4 or More Sessions Per Week ($32.50)"
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"]
    times = [f"{i}:{j}" for i in range(10, 22) for j in ['00', '30']]  # Times from 10:00 AM to 9:30 PM

    # Handle form submission (for adding a student)
    if request.method == 'POST':
        student_info = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'instrument': request.form['instrument'],
            'teacher': request.form['teacher'],
            'lesson_day': request.form['lesson_day'],
            'lesson_time': request.form['lesson_time'],
            'price_label': request.form['price'],  # Store the price label from the dropdown
            'price': price_mapping.get(request.form['price'], 0.0),  # Map the selected price label to the numeric price
        }

        # Add the student info to session
        if 'students' not in session:
            session['students'] = []
        session['students'].append(student_info)
        return redirect(url_for('lesson_form'))

    # Generate the form for the user
    form_html = '''
        <form method="post">
            First Name: <input type="text" name="first_name"><br><br>
            Last Name: <input type="text" name="last_name"><br><br>
            Email: <input type="email" name="email"><br><br>
            Phone: <input type="text" name="phone"><br><br>
            Instrument: <select name="instrument">
                {% for instrument in instruments %}
                    <option value="{{ instrument }}">{{ instrument }}</option>
                {% endfor %}
            </select><br><br>
            Teacher: <select name="teacher">
                {% for teacher in teachers %}
                    <option value="{{ teacher }}">{{ teacher }}</option>
                {% endfor %}
            </select><br><br>
            Lesson Day: <select name="lesson_day">
                {% for day in days %}
                    <option value="{{ day }}">{{ day }}</option>
                {% endfor %}
            </select><br><br>
            Lesson Time: <select name="lesson_time">
                {% for time in times %}
                    <option value="{{ time }}">{{ time }}</option>
                {% endfor %}
            </select><br><br>
            Price: <select name="price">
                {% for option in pricing_options %}
                    <option value="{{ option }}">{{ option }}</option>
                {% endfor %}
            </select><br><br>
            <button type="submit">Submit</button>
        </form>
    '''
    return render_template_string(form_html, instruments=instruments, teachers=teachers, pricing_options=pricing_options, days=days, times=times)

def create_square_customer(first_name, last_name, email, phone):
    """Create a customer in Square using the data from the form."""
    try:
        response = client.customers.create_customer(
            given_name=first_name,
            family_name=last_name,
            email_address=email,
            phone_number=phone
        )
        # Get the Customer ID from the response
        customer_id = response.result.customer.id
        print(f"Customer created successfully with ID: {customer_id}")
        return customer_id  # Return the Customer ID
    except Exception as e:
        print(f"Error creating customer: {e}")
        return None

@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    """This is where you would handle invoice generation."""
    # Retrieve students from the session
    students = session.get('students', [])
    
    if students:
        # Get the most recent student from the list (assuming last added)
        student = students[-1]

        # Create the customer in Square (if not already created)
        customer_id = create_square_customer(student['first_name'], student['last_name'], student['email'], student['phone'])
        
        if customer_id:
            # Create the invoice with the student data and Square customer ID
            create_square_invoice(student, customer_id)
            return render_template_string("<h2>Invoice Created Successfully for {{ student['first_name'] }} {{ student['last_name'] }}!</h2>", student=student)
        
        return "Failed to create customer in Square.", 400
    return "No student data found.", 400

def create_square_invoice(student, customer_id):
    """Create an invoice in Square."""
    # Include teacher and lesson time in the description
    description = f"Lesson with {student['teacher']} at {student['lesson_time']}"
    
    invoice_data = {
        'order': {
            'line_items': [
                {
                    'name': f"{student['instrument']} Lesson",
                    'quantity': '1',
                    'base_price_money': {
                        'amount': int(student['price'] * 100),  # Price in cents
                        'currency': 'USD'
                    },
                    'description': description  # Add description with teacher and lesson time
                }
            ],
            'location_id': SQUARE_LOCATION_ID,  # Use the location ID from .env
        },
        'primary_recipient': {
            'customer_id': customer_id  # Use the created customer ID
        }
    }
    try:
        response = client.invoices.create_invoice(invoice_data)
        print(f"Invoice created successfully: {response}")
        return response
    except Exception as e:
        print(f"Error creating invoice: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
