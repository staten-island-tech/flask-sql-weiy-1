from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grades.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)

# Models
class User(db.Model):  # Teacher
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class StudentGrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), nullable=False)

with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        name = request.form['name']
        student = Student.query.filter_by(name=name).first()
        if student:
            session['student'] = name
            return redirect(url_for('student_dashboard'))
        return "Student not found", 404
    return render_template('student_login.html')

@app.route('/student-dashboard')
def student_dashboard():
    if 'student' not in session:
        return redirect(url_for('student_login'))
    name = session['student']
    grades = StudentGrade.query.filter_by(student_name=name).all()
    return render_template('student_dashboard.html', name=name, grades=grades)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user'] = username
            return redirect(url_for('admin'))
        else:
            return "Invalid credentials", 403
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['student_name']
        subject = request.form['subject']
        grade = request.form['grade']

        # Ensure student exists
        student = Student.query.filter_by(name=name).first()
        if not student:
            student = Student(name=name)
            db.session.add(student)

        db.session.add(StudentGrade(student_name=name, subject=subject, grade=grade))
        db.session.commit()

    grades = StudentGrade.query.all()
    return render_template('admin.html', grades=grades)


if __name__ == '__main__':
    app.run(debug=True)
