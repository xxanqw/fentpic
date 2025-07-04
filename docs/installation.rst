# Installation Guide

This guide will help you set up FENTPIC for development or production use.

## Prerequisites

Before installing FENTPIC, ensure you have the following installed:

- **Python 3.8+**: Download from [python.org](https://python.org)
- **pip**: Python package manager (usually included with Python)
- **Node.js 16+**: For Storybook and frontend tooling
- **Git**: For version control

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/xxanqw/fentpic.git
cd fentpic
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies (for Storybook)

```bash
npm install
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-key-here
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
CLOUDFLARE_SITE_KEY=your-cloudflare-site-key-optional
```

### 6. Initialize Database

```bash
python -c "from app import init_db; init_db()"
```

### 7. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Production Setup

### Using Docker

1. **Build the Docker image**:
```bash
docker build -t fentpic .
```

2. **Run the container**:
```bash
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e GOOGLE_CLIENT_ID=your-client-id \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  fentpic
```

### Using Waitress (WSGI Server)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

## Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | No | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | No | - |
| `CLOUDFLARE_SITE_KEY` | Cloudflare Turnstile site key | No | - |
| `DATABASE_URL` | Database connection string | No | `sqlite:///database.db` |
| `UPLOAD_FOLDER` | Image upload directory | No | `static/uploads` |
| `MAX_FILE_SIZE` | Maximum upload size in bytes | No | `20971520` (20MB) |

### Application Configuration

Key configuration options in `app.py`:

```python
app.config.update(
    UPLOAD_FOLDER='static/uploads',
    AVATAR_FOLDER='static/uploads/avatars',
    PERMANENT_SESSION_LIFETIME=timedelta(days=31),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_HTTPONLY=True,
)
```

## Database Setup

### SQLite (Default)

FENTPIC uses SQLite by default, which requires no additional setup. The database file will be created automatically in the project root.

### PostgreSQL (Production Recommended)

1. **Install PostgreSQL adapter**:
```bash
pip install psycopg2-binary
```

2. **Update connection string**:
```env
DATABASE_URL=postgresql://username:password@localhost/fentpic
```

3. **Update app configuration**:
```python
import os
from urllib.parse import urlparse

database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgresql://'):
    # Configure PostgreSQL connection
    pass
```

## File Storage

### Local Storage (Default)

Images are stored in the `static/uploads` directory by default.

### Cloud Storage (Recommended for Production)

For production deployments, consider using cloud storage:

- **AWS S3**: Use boto3 and configure S3 bucket
- **Google Cloud Storage**: Use google-cloud-storage
- **Azure Blob Storage**: Use azure-storage-blob

## Reverse Proxy Configuration

### Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/fentpic/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Apache

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    Alias /static /path/to/fentpic/static
    <Directory "/path/to/fentpic/static">
        Require all granted
    </Directory>
</VirtualHost>
```

## SSL/TLS Configuration

For production, always use HTTPS:

1. **Obtain SSL certificate** (Let's Encrypt recommended)
2. **Configure web server** to use SSL
3. **Update app configuration**:
```python
app.config.update(
    SESSION_COOKIE_SECURE=True,
    PREFERRED_URL_SCHEME='https'
)
```

## Monitoring and Logging

### Application Logs

Configure logging in your production environment:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/fentpic.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Health Checks

Add a health check endpoint:

```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

## Troubleshooting

### Common Issues

1. **Permission denied errors**: Ensure upload directory is writable
2. **Import errors**: Verify virtual environment is activated
3. **Database locked**: Check file permissions on SQLite database
4. **OAuth errors**: Verify Google OAuth configuration

### Debug Mode

Enable debug mode for development:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Log Analysis

Monitor application logs for issues:

```bash
tail -f logs/fentpic.log
```
