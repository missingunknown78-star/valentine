from flask import Blueprint, render_template, request, redirect, url_for, abort
from models import Instructor, StudentMessage
from extensions import db

instructor_bp = Blueprint(
    "instructor",
    __name__,
    template_folder="templates"
)


@instructor_bp.route("/<code>")
def add_message(code):
    """Page where instructor adds their Valentine message"""
    instructor = Instructor.query.filter_by(unique_code=code).first()

    if not instructor:
        return """
        <html>
        <head><title>Invalid Link 💔</title></head>
        <body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; font-family: Arial, sans-serif; margin: 0;">
            <div style="background: white; padding: 3rem; border-radius: 20px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.2);">
                <h1 style="color: #ff4d6d; font-size: 3rem;">💔</h1>
                <h2 style="color: #333;">Invalid Link</h2>
                <p style="color: #666;">This QR code is not valid.</p>
            </div>
        </body>
        </html>
        """
    
    if instructor.is_message_added:
        return redirect(url_for("instructor.messages", code=code))

    return render_template("add_message.html", instructor=instructor)


@instructor_bp.route("/<code>/save", methods=["POST"])
def save_message(code):
    """Save the instructor's Valentine message"""
    instructor = Instructor.query.filter_by(unique_code=code).first()
    
    if not instructor:
        return "Instructor not found", 404
    
    message = request.form.get("message")
    
    if message:
        instructor.message = message
        instructor.is_message_added = True
        db.session.commit()
        
        return redirect(url_for("instructor.messages", code=code))
    
    return redirect(url_for("instructor.add_message", code=code))


@instructor_bp.route("/<code>/messages")
def messages(code):
    """Inbox view - shows all messages from students"""
    instructor = Instructor.query.filter_by(unique_code=code).first()
    
    if not instructor:
        abort(404)
    
    # Get all messages for this instructor with student info
    messages = StudentMessage.query\
        .filter_by(instructor_id=instructor.id)\
        .order_by(StudentMessage.created_at.desc())\
        .all()
    
    return render_template("messages.html", 
                         instructor=instructor, 
                         messages=messages)


@instructor_bp.route("/message/<int:message_id>")
def view_student_message(message_id):
    """View a specific student message"""
    message = StudentMessage.query.get_or_404(message_id)
    
    return render_template("view_student_message.html", 
                         message=message,
                         instructor=message.instructor)


@instructor_bp.route("/<code>/view")
def view_message(code):
    """View the final Valentine message"""
    instructor = Instructor.query.filter_by(unique_code=code).first()
    
    if not instructor or not instructor.is_message_added:
        return redirect(url_for("instructor.add_message", code=code))
    
    return render_template("view_message.html", instructor=instructor)