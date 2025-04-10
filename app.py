from flask import Flask, request, render_template_string, session, redirect, url_for
from datetime import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Make sure to replace this with a real secret key for session security

@app.route('/lesson-form', methods=['GET', 'POST'])
def lesson_form():
    instruments = [
        "Piano", "Guitar", "Vocals", "Drums",
        "Banjo", "Bass Guitar", "Brass Horns/WoodWind", "Cello",
        "Clarinet", "Flute", "Oboe", "Percussion Bells",
        "Saxophone", "Trombone", "Trumpet", "Ukulele", "Viola", "Violin"
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

    # HTML for the form (this should be defined above the POST request block)
    form_html = '''
        <h2>New Student Lesson Setup</h2>
        <form method="post">
            {% for student in students %}
                <h3>Student {{ loop.index + 1 }} Info</h3>
            {% endfor %}
            
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

            Teacher: <input type="text" name="teacher" required><br><br>
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
        <form method="post" action="/generate-invoice">
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
            'weeks': request.form['weeks'],
            'appointment_service_type': request.form['appointment_service_type'],
            'parent_name': request.form.get('parent_name', ''),
            'parent_contact': request.form.get('parent_contact', ''),
            'address_line1': request.form.get('address_line1', ''),
            'city': request.form.get('city', ''),
            'state': request.form.get('state', ''),
            'zip': request.form.get('zip', '')
        }

        # Add student data to the session list
        session['students'].append(student_data)

        # Render the form again with all added students
        return render_template_string(form_html,
                                      students=session['students'],
                                      instruments=instruments,
                                      pricing_options=pricing_options,
                                      service_types=service_types,
                                      days=days,
                                      times=times)

    return render_template_string(form_html,
                                  students=session['students'],
                                  instruments=instruments,
                                  pricing_options=pricing_options,
                                  service_types=service_types,
                                  days=days,
                                  times=times)
