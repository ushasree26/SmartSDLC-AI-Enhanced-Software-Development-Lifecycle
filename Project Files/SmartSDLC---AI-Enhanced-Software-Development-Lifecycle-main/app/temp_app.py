from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import boto3
import os
import uuid

app = Flask(__name__)
app.secret_key = 'sreeusha790'

# Toggle this for local or AWS deployment
USE_DYNAMODB = False

# Local in-memory temporary databases
users = {
    "dr.john@example.com": {
        "name": "Dr. John",
        "password": "doc123",
        "role": "doctor"
    },
    "patient.rita@example.com": {
        "name": "Rita",
        "password": "pat456",
        "role": "patient"
    }
}

appointments = []  # Local temporary appointment list

# DynamoDB setup
if USE_DYNAMODB:
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    appointments_table = dynamodb.Table('Appointments')
    users_table = dynamodb.Table('Users')

# Helper Functions

def appointments_for_doctor(doctor_name):
    if USE_DYNAMODB:
        response = appointments_table.scan()
        return [item for item in response['Items'] if item['doctor'] == doctor_name]
    return [appt for appt in appointments if appt.get('doctor') == doctor_name]

def appointments_for_patient(patient_name):
    if USE_DYNAMODB:
        response = appointments_table.scan()
        return [item for item in response['Items'] if item['name'] == patient_name]
    return [appt for appt in appointments if appt.get('name') == patient_name]

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def aboutus():
    return render_template('aboutus.html')

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        phone = request.form['phone']
        age = request.form['age']
        department = request.form['department']
        problem = request.form['problem']
        doctor = request.form['doctor']

        appointment_data = {
            'id': str(uuid.uuid4()),
            'name': name,
            'gender': gender,
            'phone': phone,
            'age': age,
            'department': department,
            'problem': problem,
            'doctor': doctor,
            'status': 'Upcoming',
            'date': datetime.today().strftime('%Y-%m-%d'),
            'time': datetime.today().strftime('%H:%M')
        }

        if USE_DYNAMODB:
            appointments_table.put_item(Item=appointment_data)
        else:
            appointments.append(appointment_data)

        flash("Appointment booked successfully!", "success")
        return redirect(url_for('appointment'))

    return render_template('appointment.html')

@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        if not name or not email or not subject or not message:
            flash("All fields are required!", "error")
        else:
            flash("Message sent successfully. Thank you for contacting MedTrack!", 'success')

        return redirect(url_for('contactus'))

    return render_template('contactus.html')

@app.route('/doctordashboard')
def doctordashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('login'))

    doctor_name = session.get('name')
    doctor_appointments = appointments_for_doctor(doctor_name)

    return render_template(
        'doctordashboard.html',
        name=doctor_name,
        email=session.get('email'),
        appointments=doctor_appointments
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users.get(email)
        if USE_DYNAMODB:
            response = users_table.get_item(Key={'email': email})
            user = response.get('Item')

        if user and user['password'] == password:
            session['email'] = email
            session['role'] = user['role']
            session['name'] = user.get('name', email.split('@')[0])

            if user['role'] == 'doctor':
                return redirect(url_for('doctordashboard'))
            elif user['role'] == 'patient':
                return redirect(url_for('patientdashboard'))
        else:
            flash("Invalid credentials", "error")

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/patientdashboard')
def patientdashboard():
    if session.get('role') != 'patient':
        return redirect(url_for('login'))

    patient_name = session.get('name')
    patient_email = session.get('email')
    patient_appointments = appointments_for_patient(patient_name)

    medication_reminders = [
        {"medicine": "Paracetamol", "time": "8:00 AM", "status": "Taken"},
        {"medicine": "Vitamin D", "time": "12:00 PM", "status": "Pending"},
        {"medicine": "Metformin", "time": "8:00 PM", "status": "Pending"}
    ]

    dosage_summary = [
        {"medicine": "Paracetamol", "dosage": "500mg x 2/day", "days_left": 5},
        {"medicine": "Vitamin D", "dosage": "1000 IU/day", "days_left": 12},
        {"medicine": "Metformin", "dosage": "850mg x 2/day", "days_left": 30}
    ]

    medical_history = [
        {"date": "2025-05-10", "diagnosis": "Fever & Cold", "doctor": "Dr. Emily Carter"},
        {"date": "2025-04-18", "diagnosis": "Vitamin D Deficiency", "doctor": "Dr. Rajesh Mehta"},
        {"date": "2025-03-05", "diagnosis": "Type 2 Diabetes", "doctor": "Dr. Anjali Sharma"}
    ]

    return render_template(
        'patientdashboard.html',
        name=patient_name,
        email=patient_email,
        appointments=patient_appointments,
        medication_reminders=medication_reminders,
        dosage_summary=dosage_summary,
        medical_history=medical_history
    )

@app.route('/patientdetails')
def patient_details():
    # You can replace this with a real DB query later
    if USE_DYNAMODB:
        response = appointments_table.scan()
        patients = response.get('Items', [])
    else:
        patients = appointments  # local Python list

    return render_template('patientdetails.html', patients=patients)

@app.route('/doctorreview')
def doctorreview():
    return render_template('doctorreview.html')

@app.route('/review')
def review():
    return render_template('review.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        role = request.form['role']
        reminder = request.form['reminder']

        if USE_DYNAMODB:
            response = users_table.get_item(Key={'email': email})
            if 'Item' in response:
                flash("Email already exists", "error")
                return redirect(url_for('signup'))
            users_table.put_item(Item={
                'email': email,
                'name': name,
                'password': password,
                'role': role,
                'phone': phone,
                'reminder': reminder
            })
        else:
            if email in users:
                flash("Email already exists", "error")
                return redirect(url_for('signup'))
            users[email] = {
                "name": name,
                "password": password,
                "role": role,
                "phone": phone,
                "reminder": reminder
            }

        flash("Signup successful! Now login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
