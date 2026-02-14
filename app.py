from flask import Flask
from extensions import db
import os

def create_app():
    app = Flask(__name__)

    # Use SQLite for PythonAnywhere deployment
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///valentine.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'valentine_secret'

    db.init_app(app)

    # Register Blueprints
    from admin.routes import admin_bp
    from instructor.routes import instructor_bp
    from student.routes import student_bp

    app.register_blueprint(admin_bp, url_prefix="/valentine/admin")
    app.register_blueprint(instructor_bp, url_prefix="/valentine/instructor")
    app.register_blueprint(student_bp, url_prefix="/valentine/student")

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)