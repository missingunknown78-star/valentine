from flask import Blueprint, render_template, abort
from models import Instructor, StudentMessage

instructor_bp = Blueprint(
    "instructor",
    __name__,
    template_folder="templates"
)


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