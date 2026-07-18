from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sys

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ─── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)

# Secret key: use env var in production, fallback for local dev
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'govind-portfolio-secret-key-2026-local')

# Database: use DATABASE_URL env var (PostgreSQL on Vercel/Neon), fallback to SQLite locally
database_url = os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db')
# Fix for Neon/Heroku: they sometimes use 'postgres://' which SQLAlchemy 1.4+ requires as 'postgresql://'
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

IS_PRODUCTION = bool(os.environ.get('VERCEL') or os.environ.get('DATABASE_URL'))

# SQLite path: use /tmp on Vercel (only writable dir), local uploads folder otherwise
if IS_PRODUCTION and not os.environ.get('DATABASE_URL'):
    # Vercel serverless: SQLite must live in /tmp
    sqlite_path = '/tmp/portfolio.db'
    database_url = f'sqlite:///{sqlite_path}'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

UPLOAD_FOLDER = '/tmp/uploads' if IS_PRODUCTION else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access the admin panel.'

# ─── Models ───────────────────────────────────────────────────────────────────
class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PortfolioContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_title = db.Column(db.String(255), default='Building Secure Systems — Breaking Them Too')
    hero_subtitle = db.Column(db.String(255), default='Govind Pratap Singh | Security Engineer & Python/FastAPI Developer')
    hero_tags = db.Column(db.String(255), default='🔒 Web/API/Mobile Security | 🐍 Python/FastAPI Backend | 🚀 DevSecOps')
    about_bio = db.Column(db.Text, default='"I\'m a Cybersecurity Professional and Python/FastAPI Backend Developer with a unique blend of offensive security expertise and backend engineering skills. I don\'t just find vulnerabilities — I build secure backend systems from the ground up. Recognized in NASA\'s VDP Hall of Fame and author of CVE-2025-61246 (CVSS 9.8), I bring real-world security experience to every project."\n\n"Beyond offensive security, I possess strong foundational knowledge in Security Operations (SOC) — including SIEM monitoring, log analysis, incident response, and threat hunting — gained through 50+ hands-on labs on TryHackMe and the Google Cybersecurity Professional Certificate curriculum."')
    about_philosophy = db.Column(db.String(1000), default='"I believe security is not a feature — it\'s a mindset. Every line of backend code I write is secured by default, and every vulnerability I find teaches me how to write better code."')
    contact_email = db.Column(db.String(255), default='govindsinghpratap123@gmail.com')
    contact_phone = db.Column(db.String(100), default='+91 6396448562')
    contact_location = db.Column(db.String(255), default='Bareilly, Uttar Pradesh, India')
    linkedin_url = db.Column(db.String(255), default='https://linkedin.com/in/govindpratapsingh404')
    github_url = db.Column(db.String(255), default='https://github.com/hackergovind')
    medium_url = db.Column(db.String(255), default='https://medium.com/@hackergovind')
    resume_filename = db.Column(db.String(255), default=None)

# ─── Auth ─────────────────────────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_content():
    content = PortfolioContent.query.get(1)
    if not content:
        content = PortfolioContent()
        db.session.add(content)
        db.session.commit()
    return content

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─── Public Routes ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    content = get_content()
    resume_available = content.resume_filename is not None
    return render_template('index.html', content=content, resume_available=resume_available)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ─── Admin Routes ─────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid username or password.'
    
    return render_template('login.html', error=error)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    content = get_content()
    resume_available = content.resume_filename is not None
    success = request.args.get('success')
    resume_success = request.args.get('resume_success')
    error = request.args.get('error')
    return render_template('admin.html', content=content, resume_available=resume_available,
                           success=success, resume_success=resume_success, error=error)

@app.route('/admin/update', methods=['POST'])
@login_required
def admin_update():
    content = get_content()
    content.hero_title = request.form.get('hero_title', content.hero_title)
    content.hero_subtitle = request.form.get('hero_subtitle', content.hero_subtitle)
    content.hero_tags = request.form.get('hero_tags', content.hero_tags)
    content.about_bio = request.form.get('about_bio', content.about_bio)
    content.about_philosophy = request.form.get('about_philosophy', content.about_philosophy)
    content.contact_email = request.form.get('contact_email', content.contact_email)
    content.contact_phone = request.form.get('contact_phone', content.contact_phone)
    content.contact_location = request.form.get('contact_location', content.contact_location)
    content.linkedin_url = request.form.get('linkedin_url', content.linkedin_url)
    content.github_url = request.form.get('github_url', content.github_url)
    content.medium_url = request.form.get('medium_url', content.medium_url)
    db.session.commit()
    return redirect(url_for('admin_dashboard') + '?success=1')

@app.route('/admin/upload-resume', methods=['POST'])
@login_required
def admin_upload_resume():
    if 'resume_file' not in request.files:
        return redirect(url_for('admin_dashboard') + '?error=no_file')
    
    file = request.files['resume_file']
    if file.filename == '':
        return redirect(url_for('admin_dashboard') + '?error=no_file')
    
    if file and allowed_file(file.filename):
        filename = 'resume.pdf'
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        content = get_content()
        content.resume_filename = filename
        db.session.commit()
        return redirect(url_for('admin_dashboard') + '?resume_success=1')
    
    return redirect(url_for('admin_dashboard') + '?error=invalid_file')

# ─── Init DB & Run ────────────────────────────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not AdminUser.query.filter_by(username='govind').first():
            admin = AdminUser(username='govind')
            admin.set_password('Lemonsec@2006')
            db.session.add(admin)
            db.session.commit()
            print('[OK] Default admin user created: govind / CyberSecurity2026!')
        # Ensure default content exists
        get_content()

# Always init DB on import (needed for Vercel serverless where __main__ never runs)
try:
    init_db()
except Exception as e:
    print(f'[WARN] init_db error (non-fatal on cold start): {e}')

if __name__ == '__main__':
    print('[*] Portfolio running at http://localhost:8080')
    print('[*] Admin panel at http://localhost:8080/admin/login')
    app.run(debug=not IS_PRODUCTION, host='0.0.0.0', port=8080)
