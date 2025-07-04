# FENTPIC - Image Hosting Platform

A modern web application for secure image hosting and sharing with user authentication and privacy controls.

![FENTPIC Logo](static/fplogo.png)

## Features

- 🖼️ **Image Upload & Hosting**: Support for JPG, PNG, GIF, WEBP formats
- 👤 **User Authentication**: Local registration and Google OAuth integration
- 🔒 **Privacy Controls**: Public/private image settings
- 📱 **Responsive Design**: Mobile-friendly interface
- 🍪 **GDPR Compliant**: Cookie consent and privacy controls
- 🔍 **Image Gallery**: Browse and manage uploaded images

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Authentication**: Flask-Session, OAuth 2.0
- **Documentation**: Swagger/OpenAPI

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd fentpic
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
CLOUDFLARE_SITE_KEY=your-cloudflare-site-key
```

5. **Initialize Database**
```bash
python -c "from app import init_db; init_db()"
```

## Running the Application

### Development Mode
```bash
python app.py
```
The application will be available at `http://localhost:5000`

### Production Mode
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## API Documentation

The application provides REST API endpoints documented with Swagger:

- **API Docs**: `http://localhost:5000/api/docs`
- **API Spec**: `http://localhost:5000/api/spec`

### Main API Endpoints

- `POST /api/upload` - Upload image files
- `GET /api/images` - Get user's images

## Commands

- **Run tests**: `python -m pytest tests/`
- **Check license compliance**: `pip-licenses --format=markdown > LICENSE_REPORT.md`
- **Generate docs**: `python generate_docs.py`
- **Start Storybook**: `npm run storybook` (after setup)

## Configuration

Key configuration options in `app.py`:

- `MAX_FILE_SIZE`: Maximum upload size (20MB default)
- `ALLOWED_EXTENSIONS`: Supported file formats
- `SESSION_COOKIE_SECURE`: Cookie security settings
- `PERMANENT_SESSION_LIFETIME`: Session duration

## Privacy & Compliance

- **Privacy Policy**: See [PRIVACY.md](PRIVACY.md)
- **Cookie Policy**: GDPR-compliant cookie consent
- **Terms of Service**: See [TERMS.md](TERMS.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For support, please contact the development team or create an issue on GitHub.

## Author

**xxanqw** - *Initial work*

---

Built with ❤️ using Flask and modern web technologies.

## Quick Start with uv

**uv** is a fast Python package manager. Install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd fentpic

# Install dependencies
uv sync --extra dev

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Initialize database
uv run python -c "from app import init_db; init_db()"

# Run the application
uv run python app.py
```

### Development Commands

```bash
# Run with development settings
uv run python app.py

# Run tests
uv run pytest

# Generate license report
uv run pip-licenses --format=markdown > LICENSE_REPORT.md

# Build documentation
cd docs && uv run sphinx-build -b html source build

# Start Storybook (requires Node.js)
npm run storybook
```
