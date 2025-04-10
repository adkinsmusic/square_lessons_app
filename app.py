from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# You can change this to whatever you want
AUTHORIZED_PASSWORD = "lessonaccess123"

@app.route('/')
def home():
    return "🎵 Square Lessons Automation App is Running!"

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == AUTHORIZED_PASSWORD:
            return redirect(url_for('lesson_form'))
        else:
            return "<h3>Access Denied: Incorrect Password</h3>"

    return '''
        <h2>Staff Login</h2>
        <form method="post">
            Password: <input type="password" name="password"><br><br>
            <input type="submit" value="Enter">
        </form>
    '''

@app.route('/lesson-form', methods=['GET', 'POST'])
def lesson_form():
    if request.method == 'POST':
        data = {
            'student_name': request.form['student_name'],
            'instrument': request.form['instrument'],
            'lesson_day': request.form['lesson_day'],
            'lesson_time': request.form['lesson_time'],
            'teacher': request.form['teacher'],
            'start_date': request.form['start_date'],
            'price': request.form['price'],
            'weeks': request.form['weeks']
        }
        return f"<h3>Form submitted successfully!</h3><pre>{data}</pre>"

    return '''
        <h2>New Student Lesson Setup</h2>
        <form method="post">
            Student Name: <input type="text" name="student_name"><br><br>
            Instrument: <input type="text" name="instrument"><br><br>
            Lesson Day: <input type="text" name="lesson_day"><br><br>
            Lesson Time: <input type="text" name="lesson_time"><br><br>
            Teacher: <input type="text" name="teacher"><br><br>
            Start Date: <input type="date" name="start_date"><br><br>
            Price per Lesson ($): <input type="number" name="price"><br><br>
            Number of Weeks: <input type="number" name="weeks"><br><br>
            <input type="submit" value="Submit">
        </form>
    '''
