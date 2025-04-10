import os
from dotenv import load_dotenv
from square.client import Client
from flask import Flask, request, render_template_string, session, redirect, url_for
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Retrieve the access token and location ID from environment variables
SQUARE_ACCESS_TOKEN = os.getenv('SQUARE_ACCESS_TOKEN')
SQUARE_LOCATION_ID = os.getenv('SQUARE_LOCATION_ID')

# Initialize the Square client with the access token
client = Client(access_token=SQUARE_ACCESS_TOKEN)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Secret key from the .env file

@app.route('/lesson-form', methods=['GET', 'POST'])
def lesson_form():
    # Define options for the form
    instruments = [
        "Piano", "Guitar", "Vocals", "Drums", "Banjo", "Bass Guitar", "Brass Horns/WoodWind", "Cello",
        "Clarinet", "Flute", "Oboe", "Percussion Bells", "Saxophone", "Trombone", "Trumpet", "Ukulele", "Viola", "Violin"
    ]
    teachers = [
        "Adam Wilson", "Bailey Kuehl", "Chase Jensen", "Jonny Clausing", "Eamon Jones", "Raymond Worden", 
        "Joshua Miller", "Kait Widger"
    ]
    pricing_options = [
        ("Appointment Block", 0), ("Regular Price", 40), ("Multi-Student/Military Discount", 35), 
        ("4 or More Sessions Per Week", 32.50)
    ]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"]
    
    # Create the time slots (12-hour format with AM/PM)
    times = []
    for hour in range(10, 22):  # Time from 10 AM to 9:30 PM
        for minute in ['00', '30']:
            time_obj = datetime.strptime(f"{hour}:{minute}", "%H:%M")
            times.append(time_obj.strftime("%I:%M %p"))  # Convert to 12-hour format (AM/PM)

    # Number of Lessons Dropdown (1 to 16)
    lesson_options = [str(i) for i in range(1, 17)]  # Create a list of numbers from 1 to 16

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
            'num_lessons': request.form['num_lessons'],  # Get the number of lessons selected
        }

        # Add the student info to session
        if 'students' not in session:
            session['students'] = []
        session['students'].append(student_info)
        return redirect(url_for('lesson_form'))

    # Generate the form for the user
    form_html = '''
        <form method="post" style="font-family: Arial, sans-serif; margin: 20px;">
            <div style="margin-bottom: 15px;">
                First Name: <input type="text" name="first_name" style="width: 100%; padding: 10px;"><br>
            </div>
            <div style="margin-bottom: 15px;">
                Last Name: <input type="text" name="last_name" style="width: 100%; padding: 10px;"><br>
            </div>
            <div style="margin-bottom: 15px;">
                Email: <input type="email" name="email" style="width: 100%; padding: 10px;"><br>
            </div>
            <div style="margin-bottom: 15px;">
                Phone: <input type="text" name="phone" style="width: 100%; padding: 10px;"><br>
            </div>
            <div style="margin-bottom: 15px;">
                Instrument: <select name="instrument" style="width: 100%; padding: 10px;">
                    {% for instrument in instruments %}
                        <option value="{{ instrument }}">{{ instrument }}</option>
                    {% endfor %}
                </select><br>
            </div>
            <div style="margin-bottom: 15px;">
                Teacher: <select name="teacher" style="width: 100%; padding: 10px;">
                    {% for teacher in teachers %}
                        <option value="{{ teacher }}">{{ teacher }}</option>
                    {% endfor %}
                </select><br>
            </div>
            <div style="margin-bottom: 15px;">
                Lesson Day: <select name="lesson_day" style="width: 100%; padding: 10px;">
                    {% for day in days %}
                        <option value="{{ day }}">{{ day }}</option>
                    {% endfor %}
                </select><br>
            </div>
            <div style="margin-bottom: 15px;">
                Lesson Time: <select name="lesson_time" style="width: 100%; padding: 10px;">
                    {% for time in times %}
                        <option value="{{ time }}">{{ time }}</option>
                    {% endfor %}
                </select><br>
            </div>
            <div style="margin-bottom: 15px;">
                Number of Lessons: <select name="num_lessons" style="width: 100%; padding: 10px;">
                    {% for num in lesson_options %}
                        <option value="{{ num }}">{{ num }}</option>
                    {% endfor %}
                </select><br>
            </div>
            <div style="margin-bottom: 15px;">
                Price: <select name="price" style="width: 100%; padding: 10px;">
                    {% for option, price in pricing_options %}
                        <option value="{{ price }}">{{ option }} - ${{ price }}</option>
                    {% endfor %}
                </select><br>
            </div>
            <button type="submit" style="padding: 10px 20px; font-size: 16px;">Submit</button>
        </form>
    '''

    return render_template_string(form_html, instruments=instruments, teachers=teachers, pricing_options=pricing_options, days=days, times=times, lesson_options=lesson_options)

@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    """Generate an invoice for the student."""
    students = session.get('students', [])
    
    if students:
        student = students[-1]
        
        # Create the customer in Square
        customer_id = create_square_customer(student['first_name'], student['last_name'], student['email'], student['phone'])
        
        if customer_id:
            # Generate invoice
            create_square_invoice(student, customer_id)
            return render_template_string("<h2>Invoice Created Successfully for {{ student['first_name'] }} {{ student['last_name'] }}!</h2>", student=student)
        
        return "Failed to create customer in Square.", 400
    
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
        customer_id = response.result.customer.id
        print(f"Customer created successfully with ID: {customer_id}")
        return customer_id  # Return the Customer ID
    except Exception as e:
        print(f"Error creating customer: {e}")
        return None

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
