from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Instructor(db.Model):
    __tablename__ = "instructors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unique_code = db.Column(db.String(100), unique=True, nullable=False)
    message = db.Column(db.Text, nullable=True)
    background_color = db.Column(db.String(50))
    qr_code = db.Column(db.Text, nullable=True)
    is_message_added = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with student messages
    student_messages = db.relationship('StudentMessage', backref='instructor', lazy=True, cascade='all, delete-orphan')


class Student(UserMixin, db.Model):
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)  # Student ID number
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)  # 1st Year, 2nd Year, etc.
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with messages
    messages = db.relationship('StudentMessage', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentMessage(db.Model):
    __tablename__ = "student_messages"
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  # Admin can approve messages
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    # Add this to your models.py file

class OfficialStudent(db.Model):
    __tablename__ = 'official_students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OfficialStudent {self.student_id}: {self.first_name} {self.last_name}>'