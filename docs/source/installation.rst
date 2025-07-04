Installation Guide
==================

System Requirements
-------------------

- Python 3.9 or higher
- pip or uv package manager
- Modern web browser

Dependencies
------------

The project uses the following main dependencies:

- **Flask 3.1.0** - Web framework
- **Flask-Dance 7.1.0** - OAuth integration
- **Werkzeug 3.1.3** - WSGI utility library
- **Jinja2 3.1.5** - Template engine
- **PyYAML 6.0.1** - YAML parser
- **python-dotenv 1.0.0** - Environment variables

For a complete list, see the ``pyproject.toml`` file.

Installation Steps
------------------

Using uv (Recommended)
~~~~~~~~~~~~~~~~~~~~~~

1. **Install uv** (if not already installed)::

    curl -LsSf https://astral.sh/uv/install.sh | sh

2. **Clone the repository**::

    git clone <repository-url>
    cd fentpic

3. **Install dependencies**::

    uv sync --extra dev

4. **Create environment file**::

    cp .env.example .env
    # Edit .env with your configuration

5. **Initialize database**::

    uv run python -c "from app import init_db; init_db()"

Using pip
~~~~~~~~~

1. **Create virtual environment**::

    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

2. **Install dependencies**::

    pip install -r requirements.txt

3. **Follow steps 4-5 from uv installation**

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Create a ``.env`` file in the project root:

.. code-block:: env

    # Required
    SECRET_KEY=your-very-secure-random-secret-key
    
    # Optional - for Google OAuth
    GOOGLE_CLIENT_ID=your-google-oauth-client-id
    GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
    
    # Optional - for Cloudflare protection
    CLOUDFLARE_SITE_KEY=your-cloudflare-site-key

Database Setup
~~~~~~~~~~~~~~

The application uses SQLite by default. The database file will be created automatically when you first run the application.

For custom database location, modify ``app.config['DATABASE']`` in ``app.py``.

Development Setup
-----------------

For development with hot reload::

    export FLASK_ENV=development
    export FLASK_DEBUG=1
    uv run python app.py

For Storybook component development::

    npm install
    npm run storybook

Production Deployment
---------------------

Using Waitress (Recommended)::

    uv run waitress-serve --host=0.0.0.0 --port=5000 app:app

Using Gunicorn::

    uv run gunicorn --bind 0.0.0.0:5000 app:app

Security Considerations
-----------------------

1. **Never commit your .env file**
2. **Use strong SECRET_KEY in production**
3. **Enable HTTPS in production**
4. **Configure proper firewall rules**
5. **Regular security updates**

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Port already in use**::

    Error: [Errno 98] Address already in use

Solution: Change the port in app.py or kill the process using the port.

**Database permission errors**::

    Permission denied: 'database.db'

Solution: Check file permissions and ensure the application has write access.

**Missing dependencies**::

    ModuleNotFoundError: No module named 'flask'

Solution: Ensure virtual environment is activated and dependencies are installed.

Getting Help
------------

- Check the GitHub issues: https://github.com/xxanqw/fentpic/issues
- Review the documentation: https://fentpic.readthedocs.io
- Contact support: support@fentpic.com
