from flask import Flask, render_template, request, redirect, url_for, flash, session, g, make_response, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
import sqlite3
import os
import hashlib
from pathlib import Path
import pytz
import requests
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_swagger_ui import get_swaggerui_blueprint
import yaml
import json

load_dotenv()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Enable HTTP for OAuth

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize Flask app
app = Flask(__name__)
app.config.update(
    SECRET_KEY = os.getenv('SECRET_KEY'),
    CLOUDFLARE_SITE_KEY = os.getenv('CLOUDFLARE_SITE_KEY'),
    DATABASE = os.path.join(app.root_path, 'database.db').replace('\\', '/'),
    UPLOAD_FOLDER = os.path.join('static', 'uploads').replace('\\', '/'),
    AVATAR_FOLDER = os.path.join('static', 'uploads', 'avatars').replace('\\', '/'),
    PERMANENT_SESSION_LIFETIME = timedelta(days=31),
    SESSION_COOKIE_SECURE = True,
    SESSION_COOKIE_SAMESITE = 'None',
    SESSION_COOKIE_HTTPONLY = True,
    )

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

KYIV_TZ = pytz.timezone('Europe/Kyiv')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

IMAGE_SIGNATURES = {
    'jpeg': (b'\xFF\xD8\xFF',),
    'png': (b'\x89PNG\r\n\x1a\n',),
    'gif': (b'GIF87a', b'GIF89a'),
    'webp': (b'RIFF', b'WEBP')
}
            
def validate_image(stream):
    """Validate image using magic numbers"""
    header = stream.read(12)
    stream.seek(0)
    
    for format_type, signatures in IMAGE_SIGNATURES.items():
        if any(header.startswith(sig) for sig in signatures):
            return '.' + format_type
    return None

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(stream):
    """Check if file size is within limit"""
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    return size <= MAX_FILE_SIZE

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def get_avatar_path(filename):
    """Generate consistent avatar path"""
    # If it starts with http/https, it's a Google avatar URL
    if filename.startswith(('http://', 'https://')):
        return filename
    return f"uploads/avatars/{filename}"

def adapt_datetime(dt):
    """Convert datetime to text for storage"""
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat()

def convert_datetime(s):
    """Convert stored text back to datetime"""
    try:
        if s is None:
            return None
        dt = datetime.fromisoformat(s.decode('utf-8'))
        return dt.replace(tzinfo=timezone.utc)
    except (AttributeError, ValueError):
        return None

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

@app.template_filter('format_datetime')
def format_datetime(value):
    """Format datetime for template display in Kyiv timezone"""
    if value is None:
        return ''
    kyiv_time = value.astimezone(KYIV_TZ)
    return kyiv_time.strftime('%Y-%m-%d %H:%M')

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    db = g.pop('db', None)
    if db is not None:
        db.close()

if not Path(app.config['DATABASE']).exists():
    init_db()

@app.before_request
def load_logged_in_user():
    g.user = None
    if 'user_id' in session:
        db = get_db()
        # Retrieve user data
        g.user = db.execute('''
            SELECT id, username, avatar_url, email
            FROM users 
            WHERE id = ?
        ''', [session['user_id']]).fetchone()

    # Simplified notification - no need to warn about adding email for password users
    if g.user and not g.user['email'] and 'email_notification_closed' not in session and request.endpoint not in ['static', 'logout', 'profile']:
        session['email_notification_prompted'] = True
        flash(
            "Будь ласка, перевірте, що ваша електронна адреса правильно додана у вашому профілі.",
            "info"
        )

def check_cookies_accepted():
    """Check if user has accepted cookies."""
    return request.cookies.get('cookies_accepted') == 'true'

@app.before_request
def before_request():
    """Check GDPR cookie before each request."""
    g.cookies_accepted = check_cookies_accepted()

@app.route('/')
def home():
    db = get_db()
    if 'user_id' in session:
        images = db.execute(
            'SELECT * FROM images WHERE user_id = ? ORDER BY uploaded_at DESC',
            [session['user_id']]
        ).fetchall()
    else:
        images = []
    return render_template('index.html', images=images)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))

    db = get_db()
    user = db.execute('''
        SELECT id, username, avatar_url, email 
        FROM users 
        WHERE id = ?
    ''', [session['user_id']]).fetchone()

    if user is None:
        flash('Користувача не знайдено. Будь ласка, увійдіть знову.', 'danger')
        return redirect(url_for('login'))

    images = db.execute('''
        SELECT * 
        FROM images 
        WHERE user_id = ? 
        ORDER BY uploaded_at DESC
    ''', [session['user_id']]).fetchall()

    # Count the number of images
    image_count = len(images)

    import os
    total_size = 0
    for image in images:
        # Assumes image has a 'filename' column and files are in 'static/uploads'
        filepath = os.path.join(app.root_path, 'static', 'uploads', image['filename'])
        if os.path.exists(filepath):
            total_size += os.path.getsize(filepath)
    limit = 500 * 1024 * 1024  # 500 MB in bytes
    percent = (total_size / limit) * 100 if limit > 0 else 0
    print(total_size, limit, percent)

    return render_template('profile.html', user=user, total_size=total_size, percent=percent, image_count=image_count)

@app.route('/profile/add-email', methods=['POST'])
def add_email():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))

    email = request.form.get('email')
    if not email:
        flash('Будь ласка, введіть email', 'danger')
        return redirect(url_for('profile'))

    db = get_db()
    try:
        db.execute('UPDATE users SET email = ? WHERE id = ?', [email, session['user_id']])
        db.commit()
        flash('Email успішно додано', 'success')
    except sqlite3.IntegrityError:
        flash('Цей email вже використовується', 'danger')
    return redirect(url_for('profile'))

@app.route('/register', methods=['POST'])
def register():
    # Redirect to Google login instead of traditional registration
    flash('Реєстрація доступна лише через Google', 'info')
    return redirect(url_for('google_login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Show login page but only with Google option
    if request.method == 'POST':
        # Redirect any form submissions to Google login
        return redirect(url_for('google_login'))
    return render_template('login.html')

# Remove password change functionality
@app.route('/profile/change-password', methods=['POST'])
def change_password():
    flash('Зміна паролю недоступна при використанні Google аутентифікації', 'info')
    return redirect(url_for('profile'))

@app.route('/profile/change-avatar', methods=['POST'])
def change_avatar():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))

    if 'avatar' not in request.files:
        flash('Файл не вибрано', 'danger')
        return redirect(url_for('profile'))

    avatar = request.files['avatar']
    if not avatar.filename:
        flash('Файл не вибрано', 'danger')
        return redirect(url_for('profile'))

    # Validate file type
    if not avatar.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        flash('Підтримуються лише зображення (PNG, JPG, GIF, WEBP)', 'danger')
        return redirect(url_for('profile'))

    try:
        # Generate unique filename
        filename = f"avatar_{session['user_id']}_{int(datetime.now().timestamp())}{os.path.splitext(avatar.filename)[1]}"
        
        # Get paths
        avatar_path = get_avatar_path(filename)  # For database
        full_path = os.path.join('static', avatar_path)  # For file system
        
        # Save file
        avatar.save(full_path)

        # Update database with web-friendly path
        db = get_db()
        db.execute('UPDATE users SET avatar_url = ? WHERE id = ?', 
                  [avatar_path, session['user_id']])
        db.commit()

        flash('Аватар успішно оновлено', 'success')
    except Exception as e:
        app.logger.error(f"Error updating avatar: {str(e)}")
        flash('Помилка при оновленні аватара', 'danger')

    return redirect(url_for('profile'))

@app.route('/upload', methods=['POST'])
def upload():
    # Authentication check
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', [session['user_id']]).fetchone()
    
    if user is None:
        return {'error': 'User not found'}, 404

    # Check for files
    if 'file' not in request.files:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'error': 'No file provided'}, 400
        flash('Файли не вибрано', 'danger')
        return redirect(url_for('home'))

    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'error': 'No file selected'}, 400
        flash('Файли не вибрано', 'danger')
        return redirect(url_for('home'))

    # Setup user folder
    user_folder = hashlib.sha1(user['username'].encode()).hexdigest()
    user_path = os.path.join(app.config['UPLOAD_FOLDER'], user_folder).replace('\\', '/')
    os.makedirs(user_path, exist_ok=True)

    # Calculate current storage usage for this user
    USER_UPLOAD_LIMIT = 500 * 1024 * 1024  # 500 MB limit
    current_usage = 0
    for root, dirs, files_in_dir in os.walk(user_path):
        for f in files_in_dir:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                current_usage += os.path.getsize(fp)

    results = []
    success_count = 0
    error_count = 0

    for file in files:
        if file and file.filename:
            # Check individual file size limit first
            if not validate_file_size(file):
                error_count += 1
                results.append({
                    'filename': file.filename,
                    'error': 'File too large'
                })
                continue

            # Get file size for quota check
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            if current_usage + file_size > USER_UPLOAD_LIMIT:
                error_count += 1
                results.append({
                    'filename': file.filename,
                    'error': 'Upload quota exceeded'
                })
                continue

            try:
                # Validate file type
                if not allowed_file(file.filename):
                    error_count += 1
                    results.append({
                        'filename': file.filename,
                        'error': 'Invalid file type'
                    })
                    continue

                # Validate image content
                img_ext = validate_image(file)
                if not img_ext:
                    error_count += 1
                    results.append({
                        'filename': file.filename,
                        'error': 'Invalid image content'
                    })
                    continue

                # Save file
                timestamp = datetime.now(KYIV_TZ).timestamp()
                safe_filename = secure_filename(f"{timestamp}_{file.filename}")
                file_path = os.path.join(user_folder, safe_filename).replace('\\', '/')
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
                file.save(full_path)

                # Update usage counter
                current_usage += os.path.getsize(full_path)

                # Save to database
                db.execute('''
                    INSERT INTO images (filename, user_id, uploaded_at)
                    VALUES (?, ?, ?)
                ''', [file_path, session['user_id'], datetime.now(timezone.utc)])
                
                success_count += 1
                results.append({
                    'filename': file.filename,
                    'success': True,
                    'path': url_for('static', filename=f'uploads/{file_path}', _external=True),
                    'timestamp': datetime.now(KYIV_TZ).strftime('%Y-%m-%d %H:%M')
                })

            except Exception as e:
                app.logger.error(f"Upload error for {file.filename}: {str(e)}")
                error_count += 1
                results.append({
                    'filename': file.filename,
                    'error': str(e)
                })

    db.commit()

    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {
            'success': success_count > 0,
            'results': results,
            'message': f'{success_count} images uploaded successfully' if success_count > 0 else 'Upload failed'
        }

    # Handle regular form submit
    if success_count > 0:
        if error_count == 0:
            flash(f'{success_count} зображень успішно завантажено!', 'success')
        else:
            flash(f'{success_count} зображень завантажено, {error_count} не вдалося', 'warning')
    else:
        flash('Жодне зображення не було успішно завантажено', 'danger')

    response = make_response(redirect(url_for('home')))
    if g.cookies_accepted:
        response.headers.update({
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
    return response

@app.route('/logout')
def logout():
    session.clear()
    flash('Ви вийшли з системи', 'info')
    return redirect(url_for('home'))

@app.route('/delete/<int:image_id>')
def delete_image(image_id):
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))

    db = get_db()
    
    # Get image with user verification
    image = db.execute('''
        SELECT i.*, u.username 
        FROM images i
        JOIN users u ON i.user_id = u.id
        WHERE i.id = ? AND i.user_id = ?
    ''', [image_id, session['user_id']]).fetchone()
    
    if not image:
        flash('Зображення не знайдено або не авторизовано', 'danger')
        return redirect(url_for('home'))
    
    # Construct file path using forward slashes
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filename']).replace('\\', '/')
    
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
            
            # Clean up empty user folder with forward slashes
            user_folder = os.path.dirname(full_path).replace('\\', '/')
            if os.path.exists(user_folder) and not os.listdir(user_folder):
                os.rmdir(user_folder)
    except OSError as e:
        flash(f'Помилка видалення файлу: {str(e)}', 'danger')
        return redirect(url_for('home'))
    
    # Remove database entry
    db.execute('DELETE FROM images WHERE id = ?', [image_id])
    db.commit()
    
    flash('Зображення успішно видалено', 'success')
    return redirect(url_for('home'))

@app.route('/delete_multiple', methods=['POST'])
def delete_multiple_images():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))

    image_ids = request.form.getlist('image_ids')
    if not image_ids:
        flash('Немає вибраних зображень', 'warning')
        return redirect(url_for('profile'))

    db = get_db()
    deleted_count = 0

    for image_id in image_ids:
        try:
            image_id_int = int(image_id)
        except ValueError:
            continue

        image = db.execute('''
            SELECT i.*, u.username 
            FROM images i
            JOIN users u ON i.user_id = u.id
            WHERE i.id = ? AND i.user_id = ?
        ''', [image_id_int, session['user_id']]).fetchone()

        if not image:
            continue

        full_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filename']).replace('\\', '/')

        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                # Remove empty user folder if exists
                user_folder = os.path.dirname(full_path).replace('\\', '/')
                if os.path.exists(user_folder) and not os.listdir(user_folder):
                    os.rmdir(user_folder)
            db.execute('DELETE FROM images WHERE id = ?', [image_id_int])
            db.commit()
            deleted_count += 1
        except OSError as e:
            flash(f'Помилка видалення файлу {image["filename"]}: {str(e)}', 'danger')

    flash(f'Видалено {deleted_count} зображень', 'success')
    return redirect(url_for('home'))

@app.route('/auth/google')
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = requests.Request(
        'GET',
        authorization_endpoint,
        params={
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": url_for('google_callback', _external=True, _scheme='https'), # Use http scheme for development
            "scope": "openid email profile",
            "response_type": "code",
            "prompt": "consent",
            "access_type": "offline"
        }
    ).prepare().url
    return redirect(request_uri)

@app.route('/auth/google/callback')
def google_callback():
    code = request.args.get("code")
    if not code:
        flash("Авторизація не вдалася.", "danger")
        return redirect(url_for("login"))

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_response = requests.post(
        token_endpoint,
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": url_for('google_callback', _external=True, _scheme='https'), # Use http scheme for development
            "grant_type": "authorization_code"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if token_response.status_code != 200:
        flash("Помилка обміну токеном", "danger")
        print(token_response.text)
        return redirect(url_for("login"))

    tokens = token_response.json()
    access_token = tokens.get("access_token")
    if not access_token:
        flash("Немає access token", "danger")
        return redirect(url_for("login"))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if userinfo_response.status_code != 200:
        flash("Не вдалося отримати інформацію про користувача від Google", "danger")
        return redirect(url_for("login"))

    userinfo = userinfo_response.json()
    if not userinfo.get("email_verified"):
        flash("Email не підтверджено Google", "danger")
        return redirect(url_for("login"))

    google_id = userinfo["sub"]
    email = userinfo["email"]
    username = userinfo.get("given_name") or email.split('@')[0]
    picture = userinfo.get("picture", "")

    db = get_db()
    existing_user = db.execute("SELECT * FROM users WHERE email = ?", [email]).fetchone()

    if existing_user:
        # If user already registered, update google_id if not already set
        if not existing_user["google_id"]:
            db.execute("UPDATE users SET google_id = ? WHERE id = ?", [google_id, existing_user["id"]])
            db.commit()
            flash("Google аккаунт додано до існуючого профіля", "success")
        session["user_id"] = existing_user["id"]
        session["username"] = existing_user["username"]
        flash("Ви увійшли через Google", "success")
        return redirect(url_for("home"))
    else:
        # Register new user with Google account details
        db.execute(
            "INSERT INTO users (username, email, google_id, avatar_url) VALUES (?, ?, ?, ?)",
            [username, email, google_id, picture]
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE email = ?", [email]).fetchone()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Реєстрація через Google пройшла успішно", "success")
        return redirect(url_for("home"))
    
@app.route('/profile/change-username', methods=['POST'])
def change_username():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))
    
    new_username = request.form.get('new_username')
    if not new_username:
        flash('Будь ласка, введіть нове ім\'я користувача', 'danger')
        return redirect(url_for('profile'))
    db = get_db()
    try:
        db.execute('UPDATE users SET username = ? WHERE id = ?', [new_username, session['user_id']])
        db.commit()
        session['username'] = new_username
        flash('Ім\'я користувача успішно змінено', 'success')
    except sqlite3.IntegrityError:
        flash('Це ім\'я користувача вже використовується', 'danger')
    return redirect(url_for('profile'))

@app.route('/profile/delete-account', methods=['GET', 'POST'])
def delete_account():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))
    db = get_db()
    user_id = session['user_id']
    # Get all images associated with the user
    images = db.execute('SELECT * FROM images WHERE user_id = ?', [user_id]).fetchall()
    # Delete image files from the file system
    for image in images:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filename']).replace('\\', '/')
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                # Clean up empty user folder if exists
                user_folder = os.path.dirname(full_path).replace('\\', '/')
                if os.path.exists(user_folder) and not os.listdir(user_folder):
                    os.rmdir(user_folder)
        except OSError as e:
            flash(f'Помилка видалення файлу {image["filename"]}: {str(e)}', 'danger')
    # Delete images from the database
    db.execute('DELETE FROM images WHERE user_id = ?', [user_id])
    # Delete the user from the database
    db.execute('DELETE FROM users WHERE id = ?', [user_id])
    db.commit()
    # Clear the session
    session.clear()

    flash('Акаунт успішно видалено', 'success')
    return redirect(url_for('home'))

@app.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@app.route('/accept_cookies')
def accept_cookies():
    """Set cookie to indicate user has accepted cookies."""
    response = make_response(redirect(request.referrer or url_for('home')))
    response.set_cookie('cookies_accepted', 'true', max_age=365*24*60*60)  # 1 year
    return response

@app.route('/static/sw.js')
def sw():
    response = make_response(
        send_from_directory('static', 'sw.js')
    )
    response.headers['Content-Type'] = 'application/javascript'
    return response

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/api/spec'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "FENTPIC API",
        'dom_id': '#swagger-ui',
        'deepLinking': True,
        'showExtensions': True,
        'showCommonExtensions': True
    }
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# API Specification
def get_api_spec():
    """Generate OpenAPI specification"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "FENTPIC API",
            "description": "Image hosting platform API for uploading and managing images",
            "version": "1.0.0",
            "contact": {
                "name": "FENTPIC Support",
                "email": "support@fentpic.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Development server"
            }
        ],
        "components": {
            "schemas": {
                "Image": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Unique image identifier"},
                        "filename": {"type": "string", "description": "Original filename"},
                        "url": {"type": "string", "description": "Public URL to access the image"},
                        "size": {"type": "integer", "description": "File size in bytes"},
                        "uploaded_at": {"type": "string", "format": "date-time", "description": "Upload timestamp"},
                        "is_public": {"type": "boolean", "description": "Whether image is publicly accessible"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "description": "Error message"},
                        "code": {"type": "integer", "description": "Error code"}
                    }
                }
            },
            "securitySchemes": {
                "sessionAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "session"
                }
            }
        },
        "paths": {
            "/api/upload": {
                "post": {
                    "summary": "Upload image files",
                    "description": "Upload one or more image files. Supports JPG, PNG, GIF, and WEBP formats up to 20MB each.",
                    "tags": ["Images"],
                    "security": [{"sessionAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "file": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "format": "binary"
                                            },
                                            "description": "Image files to upload"
                                        },
                                        "is_public": {
                                            "type": "boolean",
                                            "default": True,
                                            "description": "Whether images should be publicly accessible"
                                        }
                                    },
                                    "required": ["file"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Images uploaded successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "images": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Image"}
                                            },
                                            "message": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request - invalid file format or size",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized - login required",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/images": {
                "get": {
                    "summary": "Get user's images",
                    "description": "Retrieve a list of images uploaded by the authenticated user",
                    "tags": ["Images"],
                    "security": [{"sessionAuth": []}],
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Page number for pagination",
                            "schema": {"type": "integer", "minimum": 1, "default": 1}
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Number of images per page",
                            "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                        },
                        {
                            "name": "public_only",
                            "in": "query",
                            "description": "Filter to only public images",
                            "schema": {"type": "boolean", "default": False}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of user's images",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "images": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Image"}
                                            },
                                            "pagination": {
                                                "type": "object",
                                                "properties": {
                                                    "page": {"type": "integer"},
                                                    "limit": {"type": "integer"},
                                                    "total": {"type": "integer"},
                                                    "pages": {"type": "integer"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Unauthorized - login required",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

@app.route('/api/spec')
def get_api_specification():
    """Return OpenAPI specification"""
    return json.dumps(get_api_spec(), indent=2), 200, {'Content-Type': 'application/json'}

# API Routes

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for image upload"""
    if 'user_id' not in session:
        return json.dumps({"error": "Authentication required", "code": 401}), 401, {'Content-Type': 'application/json'}
    
    if 'file' not in request.files:
        return json.dumps({"error": "No file provided", "code": 400}), 400, {'Content-Type': 'application/json'}
    
    files = request.files.getlist('file')
    is_public = request.form.get('is_public', 'true').lower() == 'true'
    
    if not files or all(file.filename == '' for file in files):
        return json.dumps({"error": "No files selected", "code": 400}), 400, {'Content-Type': 'application/json'}
    
    uploaded_images = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
            
        if not allowed_file(file.filename):
            errors.append(f"Invalid file type for {file.filename}")
            continue
            
        if not validate_file_size(file.stream):
            errors.append(f"File {file.filename} exceeds size limit")
            continue
            
        # Validate image using magic numbers
        file_extension = validate_image(file.stream)
        if not file_extension:
            errors.append(f"Invalid image format for {file.filename}")
            continue
            
        try:
            # Generate unique filename
            import uuid
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{file_id}_{name}{ext}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Save to database
            db = get_db()
            cursor = db.execute('''
                INSERT INTO images (user_id, filename, original_filename, file_path, file_size, uploaded_at, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', [
                session['user_id'],
                unique_filename,
                filename,
                file_path,
                file_size,
                datetime.now(timezone.utc),
                is_public
            ])
            
            image_id = cursor.lastrowid
            db.commit();
            
            uploaded_images.append({
                "id": image_id,
                "filename": filename,
                "url": f"/uploads/{unique_filename}",
                "size": file_size,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "is_public": is_public
            })
            
        except Exception as e:
            errors.append(f"Error uploading {file.filename}: {str(e)}")
    
    if uploaded_images:
        response_data = {
            "success": True,
            "images": uploaded_images,
            "message": f"Successfully uploaded {len(uploaded_images)} image(s)"
        }
        if errors:
            response_data["warnings"] = errors
        return json.dumps(response_data), 200, {'Content-Type': 'application/json'}
    else:
        return json.dumps({"error": "No images uploaded", "details": errors, "code": 400}), 400, {'Content-Type': 'application/json'}

@app.route('/api/images', methods=['GET'])
def api_get_images():
    """API endpoint to get user's images"""
    if 'user_id' not in session:
        return json.dumps({"error": "Authentication required", "code": 401}), 401, {'Content-Type': 'application/json'}
    
    # Parse query parameters
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 per page
    public_only = request.args.get('public_only', 'false').lower() == 'true'
    
    # Calculate offset
    offset = (page - 1) * limit
    
    db = get_db()
    
    # Build query based on filters
    if public_only:
        query = '''
            SELECT id, filename, original_filename, file_size, uploaded_at, is_public
            FROM images 
            WHERE user_id = ? AND is_public = 1
            ORDER BY uploaded_at DESC
            LIMIT ? OFFSET ?
        '''
        count_query = 'SELECT COUNT(*) FROM images WHERE user_id = ? AND is_public = 1'
        query_params = [session['user_id'], limit, offset]
        count_params = [session['user_id']]
    else:
        query = '''
            SELECT id, filename, original_filename, file_size, uploaded_at, is_public
            FROM images 
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
            LIMIT ? OFFSET ?
        '''
        count_query = 'SELECT COUNT(*) FROM images WHERE user_id = ?'
        query_params = [session['user_id'], limit, offset]
        count_params = [session['user_id']]
    
    # Get images
    images = db.execute(query, query_params).fetchall()
    
    # Get total count
    total_count = db.execute(count_query, count_params).fetchone()[0]
    
    # Calculate total pages
    total_pages = (total_count + limit - 1) // limit
    
    # Format response
    formatted_images = []
    for image in images:
        formatted_images.append({
            "id": image['id'],
            "filename": image['original_filename'],
            "url": f"/uploads/{image['filename']}",
            "size": image['file_size'],
            "uploaded_at": image['uploaded_at'].isoformat() if hasattr(image['uploaded_at'], 'isoformat') else image['uploaded_at'],
            "is_public": bool(image['is_public'])
        })
    
    response_data = {
        "images": formatted_images,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_count,
            "pages": total_pages
        }
    }
    
    return json.dumps(response_data), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='localhost', port=5000)
    # app.run(host="localhost", port=1337, debug=True)
