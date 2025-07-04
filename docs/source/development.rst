Development Guide
=================

This guide covers the development workflow, project structure, and contribution guidelines for FENTPIC.

Project Structure
-----------------

.. code-block:: text

   fentpic/
   ├── app.py                 # Main Flask application
   ├── schema.sql            # Database schema
   ├── requirements.txt      # Python dependencies
   ├── pyproject.toml        # Project configuration
   ├── package.json          # Node.js dependencies
   ├── LICENSE               # MIT license
   ├── README.md             # Project documentation
   ├── PRIVACY.md            # Privacy policy
   ├── TERMS.md              # Terms of service
   ├── LICENSE_REPORT.md     # License compliance report
   ├── .env.example          # Environment variables template
   ├── static/               # Static assets
   │   ├── css/
   │   │   └── styles.css    # Main stylesheet
   │   ├── fplogo.png        # Application logo
   │   ├── sw.js             # Service worker
   │   └── uploads/          # User uploaded files
   │       └── avatars/      # User avatar images
   ├── templates/            # Jinja2 templates
   │   ├── base.html         # Base template
   │   ├── index.html        # Home page
   │   ├── login.html        # Login page
   │   ├── profile.html      # User profile
   │   ├── privacy.html      # Privacy policy page
   │   └── terms.html        # Terms of service page
   ├── docs/                 # Sphinx documentation
   │   ├── source/
   │   │   ├── conf.py       # Sphinx configuration
   │   │   ├── index.rst     # Documentation index
   │   │   └── *.rst         # Documentation pages
   │   └── build/            # Built documentation
   ├── stories/              # Storybook component stories
   │   ├── UploadCard.stories.js
   │   └── ImageCard.stories.js
   └── .storybook/           # Storybook configuration
       ├── main.js
       └── preview.js

Development Environment Setup
-----------------------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.9+
- Node.js 18+ (for Storybook)
- uv package manager
- Git

Initial Setup
~~~~~~~~~~~~~

1. **Clone the repository**::

    git clone <repository-url>
    cd fentpic

2. **Set up Python environment**::

    uv sync --extra dev

3. **Install Node.js dependencies**::

    npm install

4. **Create environment file**::

    cp .env.example .env
    # Edit .env with your configuration

5. **Initialize database**::

    uv run python -c "from app import init_db; init_db()"

Development Workflow
--------------------

Starting Development Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Flask Application:**

.. code-block:: bash

   # Development mode with hot reload
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   uv run python app.py

**Storybook (Component Development):**

.. code-block:: bash

   npm run storybook

**Documentation (Sphinx):**

.. code-block:: bash

   cd docs
   uv run sphinx-build -b html source build
   # Or use auto-rebuild
   uv run sphinx-autobuild source build

Code Style and Standards
~~~~~~~~~~~~~~~~~~~~~~~~~

**Python:**

- Follow PEP 8 style guide
- Use type hints where appropriate
- Document functions with docstrings
- Maximum line length: 88 characters

**JavaScript:**

- Use ES6+ features
- Follow Airbnb style guide
- Use JSDoc for documentation
- Prefer const/let over var

**HTML/CSS:**

- Use semantic HTML5 elements
- Follow BEM naming convention for CSS
- Mobile-first responsive design
- Ensure WCAG 2.1 AA compliance

Testing
-------

Running Tests
~~~~~~~~~~~~~

**Python Tests:**

.. code-block:: bash

   uv run pytest
   
   # With coverage
   uv run pytest --cov=app

**Component Tests (Storybook):**

.. code-block:: bash

   npm run test-storybook

**License Compliance:**

.. code-block:: bash

   uv run pip-licenses --format=markdown > LICENSE_REPORT.md

Test Structure
~~~~~~~~~~~~~~

**Unit Tests:**

- Test individual functions and methods
- Mock external dependencies
- Focus on edge cases and error handling

**Integration Tests:**

- Test API endpoints
- Test database operations
- Test authentication flows

**Component Tests:**

- Test component rendering
- Test user interactions
- Test accessibility features

Database Management
-------------------

Schema Changes
~~~~~~~~~~~~~~

1. **Modify** ``schema.sql``
2. **Create migration script** (if needed)
3. **Test migration** on development database
4. **Document changes** in commit message

**Example Migration:**

.. code-block:: sql

   -- Add new column to images table
   ALTER TABLE images ADD COLUMN description TEXT;

Backup and Recovery
~~~~~~~~~~~~~~~~~~~

**Create Backup:**

.. code-block:: bash

   sqlite3 database.db ".backup backup_$(date +%Y%m%d).db"

**Restore Backup:**

.. code-block:: bash

   sqlite3 database.db ".restore backup_20250704.db"

API Development
---------------

Adding New Endpoints
~~~~~~~~~~~~~~~~~~~~

1. **Define route** in ``app.py``
2. **Add OpenAPI specification** in ``get_api_spec()``
3. **Implement request validation**
4. **Add comprehensive error handling**
5. **Write tests**
6. **Update documentation**

**Example Endpoint:**

.. code-block:: python

   @app.route('/api/example', methods=['POST'])
   def api_example():
       """Example API endpoint"""
       if 'user_id' not in session:
           return jsonify({"error": "Authentication required"}), 401
       
       data = request.get_json()
       if not data:
           return jsonify({"error": "Invalid JSON"}), 400
       
       # Process request
       result = process_data(data)
       
       return jsonify({"success": True, "data": result}), 200

Error Handling
~~~~~~~~~~~~~~

**Consistent Error Format:**

.. code-block:: json

   {
     "error": "Human-readable error message",
     "code": 400,
     "details": "Additional error context"
   }

**HTTP Status Codes:**

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

Frontend Development
--------------------

Component Development
~~~~~~~~~~~~~~~~~~~~~

**Creating New Components:**

1. **Design component** in Figma/Sketch
2. **Create HTML/CSS** structure
3. **Add JavaScript** functionality
4. **Create Storybook story**
5. **Test accessibility**
6. **Document component**

**Component Structure:**

.. code-block:: javascript

   // Component story template
   export default {
     title: 'Components/ComponentName',
     argTypes: {
       property: {
         control: 'type',
         description: 'Property description'
       }
     }
   };

   const createComponent = (args) => {
     // Component creation logic
   };

   export const Default = {
     render: createComponent,
     args: {
       // Default properties
     }
   };

Styling Guidelines
~~~~~~~~~~~~~~~~~~

**CSS Custom Properties:**

.. code-block:: css

   .component {
     background: var(--surface-color);
     color: var(--text-primary);
     border: 1px solid var(--border-color);
   }

**Responsive Design:**

.. code-block:: css

   .component {
     /* Mobile first */
     padding: 1rem;
   }

   @media (min-width: 768px) {
     .component {
       padding: 2rem;
     }
   }

Security Considerations
-----------------------

Authentication
~~~~~~~~~~~~~~

- Session-based authentication
- CSRF protection enabled
- Secure cookie settings
- OAuth2 integration

File Upload Security
~~~~~~~~~~~~~~~~~~~~

- File type validation (magic numbers)
- File size limits
- Filename sanitization
- Virus scanning (planned)

Data Protection
~~~~~~~~~~~~~~~

- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS protection (template escaping)
- HTTPS enforcement (production)

Deployment
----------

Development Deployment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Local development
   uv run python app.py

Production Deployment
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Using Waitress
   uv run waitress-serve --host=0.0.0.0 --port=5000 app:app
   
   # Using Gunicorn
   uv run gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

Docker Deployment
~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   WORKDIR /app
   COPY . .
   
   RUN pip install uv
   RUN uv sync
   
   EXPOSE 5000
   CMD ["uv", "run", "waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

**Production Settings:**

.. code-block:: env

   FLASK_ENV=production
   SECRET_KEY=secure-random-key
   SESSION_COOKIE_SECURE=True
   SESSION_COOKIE_HTTPONLY=True
   SESSION_COOKIE_SAMESITE=Strict

Contributing
------------

Git Workflow
~~~~~~~~~~~~

1. **Create feature branch**::

    git checkout -b feature/amazing-feature

2. **Make changes and commit**::

    git add .
    git commit -m "Add amazing feature"

3. **Push and create PR**::

    git push origin feature/amazing-feature

**Commit Message Format:**

.. code-block:: text

   type(scope): description
   
   Longer description if needed
   
   Fixes #123

**Types:**

- ``feat``: New feature
- ``fix``: Bug fix
- ``docs``: Documentation
- ``style``: Code style changes
- ``refactor``: Code refactoring
- ``test``: Adding tests
- ``chore``: Maintenance tasks

Code Review Process
~~~~~~~~~~~~~~~~~~~

1. **Self-review** code before submitting
2. **Ensure tests pass** and coverage is maintained
3. **Update documentation** if needed
4. **Request review** from maintainers
5. **Address feedback** and update PR
6. **Merge** after approval

Pull Request Template
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes

Release Process
---------------

Version Management
~~~~~~~~~~~~~~~~~~

**Semantic Versioning (SemVer):**

- ``MAJOR.MINOR.PATCH``
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

**Release Steps:**

1. **Update version** in ``pyproject.toml``
2. **Update CHANGELOG.md**
3. **Create release tag**::

    git tag -a v1.0.1 -m "Release v1.0.1"
    git push origin v1.0.1

4. **Build and publish** (if applicable)
5. **Deploy to production**

Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

**After each release:**

1. **Update API documentation**
2. **Rebuild Sphinx docs**::

    cd docs
    uv run sphinx-build -b html source build

3. **Update component library**::

    npm run build-storybook

4. **Publish documentation** to GitHub Pages

Monitoring and Maintenance
--------------------------

Error Tracking
~~~~~~~~~~~~~~

- Monitor application logs
- Track error rates and patterns
- Set up alerting for critical issues

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

- Database query performance
- File upload speeds
- API response times
- Resource usage

Security Updates
~~~~~~~~~~~~~~~~

- Regular dependency updates
- Security vulnerability scanning
- Penetration testing (periodic)
- Access log monitoring

Backup Strategy
~~~~~~~~~~~~~~~

- Daily database backups
- Weekly full system backups
- Off-site backup storage
- Backup restoration testing

Getting Help
------------

**Resources:**

- Project documentation: ``/docs``
- API documentation: ``/api/docs``
- Component library: Storybook
- Issue tracker: GitHub Issues

**Communication:**

- GitHub Discussions for questions
- Discord/Slack for real-time chat
- Email for security issues

**Support:**

- Community support via GitHub
- Commercial support available
- Priority support for sponsors
