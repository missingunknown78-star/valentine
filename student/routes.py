from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import Student, Instructor, StudentMessage, OfficialStudent
from extensions import db
from functools import wraps
from flask import abort

student_bp = Blueprint('student', __name__, 
                       template_folder='templates',
                       static_folder='static')

# Login required decorator
def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('student.login'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        course = request.form['course']
        year = request.form['year']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        # Check if student exists in OfficialStudent database (ID only, no name check)
        official_student = OfficialStudent.query.filter_by(student_id=student_id).first()
        
        if not official_student:
            flash('Student ID not found in official records! Please contact the administrator.', 'error')
            return render_template('register.html')
        
        # Check if student already registered in the system
        existing_student = Student.query.filter(
            (Student.student_id == student_id) | (Student.email == email)
        ).first()
        
        if existing_student:
            flash('Student ID or Email already registered! Please login.', 'error')
            return render_template('register.html')
        
        # Create new student (using the name they provided, not from official records)
        new_student = Student(
            student_id=student_id,
            name=name,  # Use the name from the form
            course=course,
            year=year,
            email=email
        )
        new_student.set_password(password)
        
        db.session.add(new_student)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('student.login'))
    
    return render_template('register.html')



@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        
        student = Student.query.filter_by(student_id=student_id).first()
        
        if student and student.check_password(password):
            session['student_id'] = student.id
            session['student_name'] = student.name
            flash(f'Welcome back, {student.name}!', 'success')
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid Student ID or password!', 'error')
    
    return render_template('login.html')


@student_bp.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('student.login'))



@student_bp.route('/dashboard')
@student_login_required
def dashboard():
    student_id = session['student_id']
    student = Student.query.get(student_id)
    
    # Get ALL instructors
    instructors = Instructor.query.all()
    
    # Get messages sent by this student
    my_messages = StudentMessage.query.filter_by(student_id=student_id)\
        .join(Instructor)\
        .order_by(StudentMessage.created_at.desc())\
        .all()
    
    return render_template('student_dashboard.html', 
                         student=student, 
                         instructors=instructors,
                         my_messages=my_messages)


@student_bp.route('/instructor/<int:instructor_id>')
@student_login_required
def view_instructor(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    student_id = session['student_id']
    
    # Check if student already sent a message to this instructor
    existing_message = StudentMessage.query.filter_by(
        student_id=student_id,
        instructor_id=instructor_id
    ).first()
    
    return render_template('view_instructor.html', 
                         instructor=instructor, 
                         existing_message=existing_message)


@student_bp.route('/instructor/<int:instructor_id>/send-message', methods=['POST'])
@student_login_required
def send_message(instructor_id):
    student_id = session['student_id']
    instructor = Instructor.query.get_or_404(instructor_id)
    
    message_text = request.form.get('message')
    
    if not message_text:
        flash('Please enter a message!', 'error')
        return redirect(url_for('student.view_instructor', instructor_id=instructor_id))
    
    # Create new message (allow multiple messages)
    new_message = StudentMessage(
        student_id=student_id,
        instructor_id=instructor_id,
        message=message_text,
        is_approved=True
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    flash('Your Valentine message has been sent to instructor! 💖', 'success')
    return redirect(url_for('student.view_instructor', instructor_id=instructor_id))



@student_bp.route('/my-messages')
@student_login_required
def my_messages():
    student_id = session['student_id']
    messages = StudentMessage.query.filter_by(student_id=student_id)\
        .join(Instructor)\
        .order_by(StudentMessage.created_at.desc())\
        .all()
    
    return render_template('my_messages.html', messages=messages)


@student_bp.route('/profile')
@student_login_required
def profile():
    student_id = session['student_id']
    student = Student.query.get(student_id)
    
    # Count messages
    message_count = StudentMessage.query.filter_by(student_id=student_id).count()
    approved_count = StudentMessage.query.filter_by(student_id=student_id, is_approved=True).count()
    
    return render_template('profile.html', student=student, message_count=message_count, approved_count=approved_count)