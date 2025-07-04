Welcome to FENTPIC's documentation!
=====================================

**FENTPIC** is a modern image hosting platform built with Flask that provides secure image uploading, user authentication, and privacy controls.

Features
--------

- 🖼️ **Image Upload & Hosting**: Support for JPG, PNG, GIF, WEBP formats up to 20MB
- 👤 **User Authentication**: Local registration and Google OAuth integration  
- 🔒 **Privacy Controls**: Public/private image settings
- 📱 **Responsive Design**: Mobile-friendly interface
- 🍪 **GDPR Compliant**: Cookie consent and privacy controls
- 🔍 **Image Gallery**: Browse and manage uploaded images
- 🚀 **REST API**: Full API with Swagger documentation

Quick Start
-----------

1. **Installation**::

    git clone <repository-url>
    cd fentpic
    uv sync --extra dev

2. **Configuration**::

    # Create .env file
    SECRET_KEY=your-secret-key-here
    GOOGLE_CLIENT_ID=your-google-oauth-client-id
    GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

3. **Run the application**::

    uv run python app.py

4. **Access the application**:
   Open http://localhost:5000 in your browser

API Documentation
-----------------

The application provides a REST API with Swagger documentation:

- **API Docs**: http://localhost:5000/api/docs
- **API Spec**: http://localhost:5000/api/spec

Main endpoints:

- ``POST /api/upload`` - Upload image files
- ``GET /api/images`` - Get user's images

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   api
   components
   development

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`tion master file, created by
   sphinx-quickstart on Fri Jul  4 13:28:25 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to FENTPIC's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
