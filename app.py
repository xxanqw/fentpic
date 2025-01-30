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

load_dotenv()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Enable HTTP for OAuth

# Initialize Flask app
app = Flask(__name__)
app.config.update(
    SECRET_KEY = os.getenv('SECRET_KEY'),
    CLOUDFLARE_SITE_KEY = os.getenv('CLOUDFLARE_SITE_KEY'),
    DATABASE = os.path.join(app.root_path, 'database.db').replace('\\', '/'),
    UPLOAD_FOLDER = os.path.join('static', 'uploads').replace('\\', '/'),
    AVATAR_FOLDER = os.path.join('static', 'uploads', 'avatars').replace('\\', '/'),
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

KYIV_TZ = pytz.timezone('Europe/Kyiv')

def get_avatar_path(filename):
    """Generate consistent avatar path"""
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
        g.user = db.execute('''
            SELECT id, username, avatar_url 
            FROM users 
            WHERE id = ?
        ''', [session['user_id']]).fetchone()

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
        SELECT id, username, avatar_url 
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

    return render_template('profile.html', user=user, images=images)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                [username, hashed_password]
            )
            db.commit()
            flash('Акаунт успішно створено!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Ім\'я користувача вже існує', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        turnstile_response = request.form.get('cf-turnstile-response')
        verification_response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data={
            'secret': os.getenv('CLOUDFLARE_SECRET'),
            'response': turnstile_response
        }).json()

        if not verification_response['success']:
            flash('Підтвердіть, що ви не робот', 'danger')
            return redirect(url_for('login'))
        
        db = get_db()
        username = request.form['username']
        password = request.form['password']

        user = db.execute(
            'SELECT * FROM users WHERE username = ?',
            [username]
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session.permanent = True  # Make session permanent
            session['user_id'] = user['id']
            session['username'] = user['username']  # Add username to session
            flash('Вхід успішний!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Невірні облікові дані', 'danger')
    return render_template('login.html')

@app.route('/profile/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        flash('Будь ласка, увійдіть спочатку', 'danger')
        return redirect(url_for('login'))
        
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('Всі поля повинні бути заповнені', 'danger')
        return redirect(url_for('profile'))
        
    if new_password != confirm_password:
        flash('Нові паролі не співпадають', 'danger')
        return redirect(url_for('profile'))
        
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', [session['user_id']]).fetchone()
    
    if not check_password_hash(user['password'], current_password):
        flash('Неправильний поточний пароль', 'danger')
        return redirect(url_for('profile'))
        
    hashed_password = generate_password_hash(new_password)
    db.execute('UPDATE users SET password = ? WHERE id = ?', 
               [hashed_password, session['user_id']])
    db.commit()
    
    flash('Пароль успішно змінено', 'success')
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
    if 'user_id' not in session:
        flash('Вам потрібно увійти, щоб завантажувати зображення', 'danger')
        return redirect(url_for('login'))

    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?',
        [session['user_id']]
    ).fetchone()
    
    if user is None:
        flash('Користувача не знайдено. Будь ласка, увійдіть знову.', 'danger')
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('Файли не вибрано', 'danger')
        return redirect(url_for('home'))

    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        flash('Файли не вибрано', 'danger')
        return redirect(url_for('home'))

    # Create user-specific folder
    user_folder = hashlib.sha1(user['username'].encode()).hexdigest()
    user_path = f"{app.config['UPLOAD_FOLDER']}/{user_folder}"
    os.makedirs(user_path, exist_ok=True)

    success_count = 0
    error_count = 0

    for file in files:
        if file and file.filename and file.filename.strip():
            try:
                safe_filename = f"{datetime.now(KYIV_TZ).timestamp()}_{file.filename}"
                file_path = f"{user_folder}/{safe_filename}"
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], user_folder, safe_filename).replace('\\', '/')
                file.save(full_path)
                # Store UTC time in database
                db.execute('''
                    INSERT INTO images (filename, user_id, uploaded_at)
                    VALUES (?, ?, ?)
                ''', [file_path, session['user_id'], datetime.now(timezone.utc)])
                success_count += 1
            except Exception as e:
                error_count += 1
                app.logger.error(f"Помилка завантаження {file.filename}: {str(e)}")

    db.commit()

    if success_count > 0:
        if error_count == 0:
            flash(f'{success_count} зображень успішно завантажено!', 'success')
        else:
            flash(f'{success_count} зображень завантажено, {error_count} не вдалося', 'warning')
    else:
        flash('Жодне зображення не було успішно завантажено', 'danger')

    return redirect(url_for('home'))

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

@app.route('/static/sw.js')
def sw():
    response = make_response(
        send_from_directory('static', 'sw.js')
    )
    response.headers['Content-Type'] = 'application/javascript'
    return response

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='localhost', port=5000)
    # app.run(debug=True)
