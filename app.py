from flask import Flask, render_template
from config import Config
from routes.auth import auth_bp
from flask_wtf.csrf import CSRFProtect
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CSRF Protection
    csrf = CSRFProtect(app)

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from routes.profile import profile_bp
    from routes.ranking import ranking_bp
    from routes.admin import admin_bp
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(ranking_bp, url_prefix='/ranking')
    app.register_blueprint(admin_bp, url_prefix='/secured-dir-admin-panel99')

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net; img-src 'self' data: https://ui-avatars.com https://cdn.codechef.com;"
        return response

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
