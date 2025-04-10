from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/lesson-form', methods=['GET', 'POST'])
def lesson_form():
    instruments = [
        "Piano", "Guitar", "Vocals", "Drums",  # Top 4
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

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday", "Sunday"]

    times = []
    hour = 10
    while hour < 21:
        times.append(f"{hour}:00 AM" if hour < 12 else f"{hour-12}:00 PM" if hour > 12 else "12:00 PM")
        times.append(f"{hour}:30 AM" if hour < 12 else f"{hour-12}:30 PM" if hour > 12 else "12:30 PM")
        hour += 1
    times.append("9:00 PM")

    if request.method == 'POST':
        data = {
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
            'parent_name': request.form.get('parent_name', ''),
            'parent_contact': request.form.get('parent_contact', ''),
            'address_line1': request.form.get('address_line1', ''),
            'city': request.form.get('city', ''),
            'state': request.form.get('state', ''),
            'zip': request.form.get('zip', '')
        }
        return f"<h3>Form submitted successfully!</h3><pre>{data}</pre>"

    form_html = '''
        <h2>New Student Lesson Setup</h2>
        <form method="post">
            <strong>Student Info</strong><br>
            First Name: <input type="text" name="first_name" required><br><br>
            Last Name: <input type="text" name="last_name" required><br><br>
            Email: <input type="email" name="email" required><br><br>
            Phone Number: <input type="text" name="phone" required><br><br>

            Instrument:
            <select name="instrument">
                {% for instrument in instruments %}
                <option value="{{ instrument }}">{{ instrument }}</option>
                {% endfor %}
            </select><br><br>

            Lesson Day:
            <select name="lesson_day">
                {% for day in days %}
                <option value="{{ day }}">{{ day }}</option>
                {% endfor %}
            </select><br><br>

            Lesson Time:
            <select name="lesson_time">
                {% for time in times %}
                <option value="{{ time }}">{{ time }}</option>
                {% endfor %}
            </select><br><br>

            Teacher: <input type="text" name="teacher" required><br><br>
            Start Date: <input type="date" name="start_date" required><br><br>

            Pricing Option:
            <select name="price_option">
                {% for option, value in pricing_options.items() %}
                <option value="{{ option }}">{{ option }} - ${{ '{:.2f}'.format(value) }}</option>
                {% endfor %}
            </select><br><br>

            Number of Lessons:
            <select name="weeks">
                {% for w in range(1, 9) %}
                <option value="{{ w }}">{{ w }}</option>
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

            <input type="submit" value="Submit">
        </form>
    '''
    return render_template_string(form_html,
                                  instruments=instruments,
                                  pricing_options=pricing_options,
                                  days=days,
                                  times=times)
