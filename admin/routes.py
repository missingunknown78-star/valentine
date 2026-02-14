import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from models import Instructor, OfficialStudent
from extensions import db
import random
import string
import qrcode
from io import BytesIO
import base64
from datetime import datetime

# Set template folder to the admin/templates folder inside this module
template_dir = os.path.join(os.path.dirname(__file__), "templates")

admin_bp = Blueprint('admin', __name__, 
                     template_folder='templates',
                     static_folder='static')

# Helper to generate unique code
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Helper to generate QR code as base64
def generate_qr_code(data):
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5,
            error_correction=qrcode.constants.ERROR_CORRECT_L
        )
        
        # Add data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

@admin_bp.route("/")
def dashboard():
    instructors = Instructor.query.all()
    students = OfficialStudent.query.all()
    return render_template("dashboard.html", instructors=instructors, students=students)


@admin_bp.route("/add", methods=["GET", "POST"])
def add_instructor():
    if request.method == "POST":
        name = request.form["name"]
        color = request.form["color"]
        
        # Generate unique code
        unique_code = generate_code()
        
        # FIX: Add /instructor/ to match blueprint prefix
        instructor_url = f"{request.host_url}valentine/instructor/{unique_code}/messages"
        
        # Generate QR code
        qr_code_data = generate_qr_code(instructor_url)

        new_instructor = Instructor(
            name=name,
            message=None,
            background_color=color,
            unique_code=unique_code,
            qr_code=qr_code_data,
            is_message_added=False
        )

        db.session.add(new_instructor)
        db.session.commit()

        return redirect(url_for("admin.instructor_success", instructor_id=new_instructor.id))

    return render_template("add_instructor.html")


@admin_bp.route("/instructor/<int:instructor_id>/success")
def instructor_success(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    
    # FIX: Add /instructor/ to match blueprint prefix
    instructor_url = f"{request.host_url}valentine/instructor/{instructor.unique_code}/messages"
    
    return render_template("instructor_success.html", instructor=instructor, instructor_url=instructor_url)

from PIL import Image, ImageDraw, ImageFont
import io
import base64
import qrcode

@admin_bp.route("/generate-qr-preview", methods=["POST"])
def generate_qr_preview():
    """AJAX endpoint for live QR preview"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400
            
        name = data.get('name', 'Instructor')
        
        # Generate temporary preview code
        temp_code = generate_code()
        
        # FIX: Add /instructor/ to match blueprint prefix
        preview_url = f"{request.host_url}valentine/instructor/{temp_code}/messages"
        print(f"Preview URL: {preview_url}")
        
        # Generate QR code with error correction high (to allow overlay)
        qr = qrcode.QRCode(
            version=1, 
            box_size=10, 
            border=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H  # High error correction
        )
        qr.add_data(preview_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to PIL Image for editing
        qr_img = qr_img.convert('RGB')
        
        # Create a copy to work with
        img = qr_img.copy()
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default
        try:
            # You may need to adjust the font path
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (center)
        img_width, img_height = img.size
        center_x = img_width // 2
        center_y = img_height // 2
        
        # Get text size
        try:
            # PIL 10+
            bbox = draw.textbbox((0, 0), name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Older PIL
            text_width, text_height = font.getsize(name)
        
        # Create a white background for text (to make it readable over QR)
        padding = 8
        overlay_x1 = center_x - (text_width // 2) - padding
        overlay_y1 = center_y - (text_height // 2) - padding
        overlay_x2 = center_x + (text_width // 2) + padding
        overlay_y2 = center_y + (text_height // 2) + padding
        
        # Draw white rectangle behind text
        draw.rectangle(
            [overlay_x1, overlay_y1, overlay_x2, overlay_y2],
            fill='white'
        )
        
        # Draw border around rectangle
        draw.rectangle(
            [overlay_x1, overlay_y1, overlay_x2, overlay_y2],
            outline='#ff4d6d',
            width=2
        )
        
        # Draw text
        text_x = center_x - (text_width // 2)
        text_y = center_y - (text_height // 2)
        
        # Draw text in Valentine pink
        draw.text((text_x, text_y), name, fill='#ff4d6d', font=font)
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_code': img_str,
            'preview_url': preview_url,
            'temp_code': temp_code
        })
        
    except Exception as e:
        print(f"Error in generate_qr_preview: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    

@admin_bp.route("/instructor/<int:instructor_id>/delete", methods=["POST"])
def delete_instructor(instructor_id):
    """Delete an instructor"""
    instructor = Instructor.query.get_or_404(instructor_id)
    db.session.delete(instructor)
    db.session.commit()
    flash('Instructor deleted successfully!', 'success')
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/add-student", methods=["POST"])
def add_student():
    """Add a new official student"""
    if request.method == "POST":
        # Get form data
        student_id = request.form.get('student_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Check if student ID already exists
        existing_student = OfficialStudent.query.filter_by(student_id=student_id).first()
        if existing_student:
            flash(f'Student ID {student_id} already exists!', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Create new student
        new_student = OfficialStudent(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        db.session.add(new_student)
        db.session.commit()
        
        flash(f'Student {first_name} {last_name} added successfully!', 'success')
        
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/delete-student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    """Delete an official student"""
    student = OfficialStudent.query.get_or_404(student_id)
    name = f'{student.first_name} {student.last_name}'
    
    db.session.delete(student)
    db.session.commit()
    
    flash(f'Student {name} deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))