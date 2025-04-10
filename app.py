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
app.secret_key = FLASK_SECRET_KEY  # Use the secret key from the .env file

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
        "Appointment Block", "Regular Price", "Multi-Student/Military Discount", "4 or More Sessions Per Week"
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"]
    times = [f"{i}:{j}" for i in range(10, 22) for j in ['00', '30']]  # Times from 10:00 AM to 9:30 PM
    lesson_count_options = [str(i) for i in range(1, 17)]  # Add dropdown for number of lessons (1 to 16)

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
            'price': float(request.form['price']),
            'lesson_count': int(request.form['lesson_count']),
            'start_date': request.form['start_date']  # Start date for the recurring invoice
        }

        # Add the student info to session
        if 'students' not in session:
            session['students'] = []
        session['students'].append(student_info)
        return redirect(url_for('lesson_form'))

    # Generate the form for the user
    form_html = '''
        <form method="post">
            First Name: <input type="text" name="first_name"><br>
            Last Name: <input type="text" name="last_name"><br>
            Email: <input type="email" name="email"><br>
            Phone: <input type="text" name="phone"><br>
            Instrument: <select name="instrument">
                {% for instrument in instruments %}
                    <option value="{{ instrument }}">{{ instrument }}</option>
                {% endfor %}
            </select><br>
            Teacher: <select name="teacher">
                {% for teacher in teachers %}
                    <option value="{{ teacher }}">{{ teacher }}</option>
                {% endfor %}
            </select><br>
            Lesson Day: <select name="lesson_day">
                {% for day in days %}
                    <option value="{{ day }}">{{ day }}</option>
                {% endfor %}
            </select><br>
            Lesson Time: <select name="lesson_time">
                {% for time in times %}
                    <option value="{{ time }}">{{ time }}</option>
                {% endfor %}
            </select><br>
            Price: <select name="price">
                {% for option in pricing_options %}
                    <option value="{{ option }}">{{ option }}</option>
                {% endfor %}
            </select><br>
            Number of Lessons: <select name="lesson_count">
                {% for count in lesson_count_options %}
                    <option value="{{ count }}">{{ count }}</option>
                {% endfor %}
            </select><br>
            Start Date: <input type="date" name="start_date"><br>  <!-- Start date for recurring invoice -->
            <button type="submit">Submit</button>
        </form>
    '''
    return render_template_string(form_html, instruments=instruments, teachers=teachers, pricing_options=pricing_options, days=days, times=times, lesson_count_options=lesson_count_options)


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

        # Log student info
        print(f"Generating invoice for student: {student['first_name']} {student['last_name']}")
        
        # Create the customer in Square (if not already created)
        customer_id = create_square_customer(student['first_name'], student['last_name'], student['email'], student['phone'])
        
        if customer_id:
            # Create the invoice with the student data and Square customer ID
            invoice_response = create_square_invoice(student, customer_id)
            
            # Log the response from Square
            if invoice_response:
                print(f"Invoice created successfully: {invoice_response}")
                return render_template_string("<h2>Invoice Created Successfully for {{ student['first_name'] }} {{ student['last_name'] }}!</h2>", student=student)
            else:
                print("Error: Could not create invoice.")
                return "Failed to create invoice.", 400
        
        return "Failed to create customer in Square.", 400
    
    return "No student data found.", 400


def create_square_invoice(student, customer_id):
    """Create an invoice in Square."""
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
                    'description': description
                }
            ],
            'location_id': SQUARE_LOCATION_ID,
        },
        'primary_recipient': {
            'customer_id': customer_id
        },
        'scheduled_at': student['start_date']  # Start date for recurring invoices
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
