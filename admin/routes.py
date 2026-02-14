import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models import Instructor
from extensions import db
import random
import string
import qrcode
from io import BytesIO
import base64

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
    return render_template("dashboard.html", instructors=instructors)


@admin_bp.route("/add", methods=["GET", "POST"])
def add_instructor():
    if request.method == "POST":
        name = request.form["name"]
        color = request.form["color"]
        
        # Generate unique code
        unique_code = generate_code()
        
        # URL for instructor page (you can change this later)
        instructor_url = f"{request.host_url}instructor/{unique_code}"
        
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

        # Redirect to success page with QR code
        return redirect(url_for("admin.instructor_success", instructor_id=new_instructor.id))

    return render_template("add_instructor.html")


@admin_bp.route("/instructor/<int:instructor_id>/success")
def instructor_success(instructor_id):
    instructor = Instructor.query.get_or_404(instructor_id)
    
    # URL for instructor page
    instructor_url = f"{request.host_url}instructor/{instructor.unique_code}"
    
    return render_template("instructor_success.html", instructor=instructor, instructor_url=instructor_url)


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
        
        # Build preview URL
        preview_url = f"{request.host_url}instructor/{temp_code}"
        print(f"Preview URL: {preview_url}")
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(preview_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display
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
    return redirect(url_for("admin.dashboard"))