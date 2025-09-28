from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_DIR = 'data'
LOGIN_CSV = os.path.join(DATA_DIR, 'users.csv')
TIMETABLE_CSV = os.path.join(DATA_DIR, 'timetable.csv')

os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open(LOGIN_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    session['user'] = username
                    return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open(LOGIN_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password])
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/input', methods=['GET', 'POST'])
def input_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        college = request.form['college']
        subjects = request.form['subjects']
        rooms = request.form['rooms']
        faculty = request.form['faculty']
        hours = request.form['hours']
        with open(TIMETABLE_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([college, subjects, rooms, faculty, hours])
        return redirect(url_for('timetable'))
    return render_template('input_form.html')

@app.route('/timetable')
def timetable():
    if 'user' not in session:
        return redirect(url_for('login'))
    rows = []
    with open(TIMETABLE_CSV, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return render_template('timetable.html', rows=rows)

if __name__ == '__main__':
    # Create users.csv if not exists
    if not os.path.exists(LOGIN_CSV):
        with open(LOGIN_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password'])
    app.run(debug=True)
