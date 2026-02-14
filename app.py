from flask import Flask
from extensions import db

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/valentine_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'valentine_secret'

    db.init_app(app)

    # Register Blueprints
    from admin.routes import admin_bp
    from instructor.routes import instructor_bp
    from student.routes import student_bp  # Import student blueprint

    app.register_blueprint(admin_bp, url_prefix="/valentine/admin")
    app.register_blueprint(instructor_bp, url_prefix="/valentine/instructor")  # Your existing instructor routes
    app.register_blueprint(student_bp, url_prefix="/valentine/student")  # New student routes

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)