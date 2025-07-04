API Reference
=============

FENTPIC provides a RESTful API for programmatic access to image hosting functionality.

Base URL
--------

All API endpoints are relative to: ``http://localhost:5000/api``

Authentication
--------------

The API uses session-based authentication. You must be logged in to access most endpoints.

**Authentication Methods:**

1. **Session Cookies** - After logging in through the web interface
2. **OAuth Tokens** - Google OAuth integration

**Session Management:**

- Sessions expire after 31 days of inactivity
- Secure cookies are used in production
- CSRF protection is implemented

Endpoints
---------

Upload Images
~~~~~~~~~~~~~

.. http:post:: /api/upload

   Upload one or more image files.

   **Request:**

   .. sourcecode:: http

      POST /api/upload HTTP/1.1
      Content-Type: multipart/form-data
      Cookie: session=...

   **Form Parameters:**

   :file: Image files to upload (required, multiple allowed)
   :is_public: Whether images should be publicly accessible (optional, default: true)

   **Supported Formats:**
   
   - JPEG (.jpg, .jpeg)
   - PNG (.png)
   - GIF (.gif)
   - WebP (.webp)

   **File Size Limits:**
   
   - Maximum: 20MB per file
   - Multiple files allowed

   **Response:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "success": true,
        "images": [
          {
            "id": 123,
            "filename": "example.jpg",
            "url": "/uploads/abc123_example.jpg",
            "size": 1048576,
            "uploaded_at": "2025-07-04T12:00:00Z",
            "is_public": true
          }
        ],
        "message": "Successfully uploaded 1 image(s)"
      }

   **Error Responses:**

   .. sourcecode:: http

      HTTP/1.1 401 Unauthorized
      Content-Type: application/json

      {
        "error": "Authentication required",
        "code": 401
      }

   .. sourcecode:: http

      HTTP/1.1 400 Bad Request
      Content-Type: application/json

      {
        "error": "No images uploaded",
        "details": ["Invalid file type for image.txt"],
        "code": 400
      }

Get Images
~~~~~~~~~~

.. http:get:: /api/images

   Retrieve a paginated list of user's uploaded images.

   **Request:**

   .. sourcecode:: http

      GET /api/images?page=1&limit=20&public_only=false HTTP/1.1
      Cookie: session=...

   **Query Parameters:**

   :page: Page number for pagination (optional, default: 1)
   :limit: Number of images per page (optional, default: 20, max: 100)
   :public_only: Filter to only public images (optional, default: false)

   **Response:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "images": [
          {
            "id": 123,
            "filename": "example.jpg",
            "url": "/uploads/abc123_example.jpg",
            "size": 1048576,
            "uploaded_at": "2025-07-04T12:00:00Z",
            "is_public": true
          }
        ],
        "pagination": {
          "page": 1,
          "limit": 20,
          "total": 45,
          "pages": 3
        }
      }

   **Error Response:**

   .. sourcecode:: http

      HTTP/1.1 401 Unauthorized
      Content-Type: application/json

      {
        "error": "Authentication required",
        "code": 401
      }

Response Formats
----------------

Success Response
~~~~~~~~~~~~~~~~

All successful API responses include:

- ``success``: Boolean indicating success (for upload endpoint)
- ``data``: Response data (varies by endpoint)
- ``message``: Human-readable success message (optional)

Error Response
~~~~~~~~~~~~~~

All error responses include:

- ``error``: Human-readable error message
- ``code``: HTTP status code
- ``details``: Additional error details (optional)

Rate Limiting
-------------

**Current Limits:**

- No rate limiting implemented
- File size limit: 20MB per file
- Session timeout: 31 days

**Planned Limits:**

- 100 uploads per hour per user
- 1000 API requests per hour per user

Data Models
-----------

Image Object
~~~~~~~~~~~~

.. code-block:: json

   {
     "id": 123,
     "filename": "original-filename.jpg",
     "url": "/uploads/unique-filename.jpg",
     "size": 1048576,
     "uploaded_at": "2025-07-04T12:00:00Z",
     "is_public": true
   }

**Fields:**

:id: Unique integer identifier
:filename: Original filename as uploaded
:url: Relative URL to access the image
:size: File size in bytes
:uploaded_at: ISO 8601 timestamp in UTC
:is_public: Boolean indicating public accessibility

Pagination Object
~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "page": 1,
     "limit": 20,
     "total": 45,
     "pages": 3
   }

**Fields:**

:page: Current page number
:limit: Items per page
:total: Total number of items
:pages: Total number of pages

Error Codes
-----------

:400: Bad Request - Invalid input data
:401: Unauthorized - Authentication required
:403: Forbidden - Access denied
:404: Not Found - Resource not found
:413: Payload Too Large - File too large
:415: Unsupported Media Type - Invalid file format
:429: Too Many Requests - Rate limit exceeded
:500: Internal Server Error - Server error

Usage Examples
--------------

cURL Examples
~~~~~~~~~~~~~

**Upload an image:**

.. code-block:: bash

   curl -X POST http://localhost:5000/api/upload \
     -H "Cookie: session=your-session-cookie" \
     -F "file=@/path/to/image.jpg" \
     -F "is_public=true"

**Get images:**

.. code-block:: bash

   curl -X GET "http://localhost:5000/api/images?page=1&limit=10" \
     -H "Cookie: session=your-session-cookie"

Python Examples
~~~~~~~~~~~~~~~

**Using requests library:**

.. code-block:: python

   import requests

   # Upload image
   with open('image.jpg', 'rb') as f:
       response = requests.post(
           'http://localhost:5000/api/upload',
           files={'file': f},
           data={'is_public': 'true'},
           cookies={'session': 'your-session-cookie'}
       )
   
   print(response.json())

   # Get images
   response = requests.get(
       'http://localhost:5000/api/images',
       params={'page': 1, 'limit': 20},
       cookies={'session': 'your-session-cookie'}
   )
   
   print(response.json())

JavaScript Examples
~~~~~~~~~~~~~~~~~~~

**Using fetch API:**

.. code-block:: javascript

   // Upload image
   const formData = new FormData();
   formData.append('file', fileInput.files[0]);
   formData.append('is_public', 'true');

   fetch('/api/upload', {
       method: 'POST',
       body: formData,
       credentials: 'same-origin'
   })
   .then(response => response.json())
   .then(data => console.log(data));

   // Get images
   fetch('/api/images?page=1&limit=20', {
       credentials: 'same-origin'
   })
   .then(response => response.json())
   .then(data => console.log(data));

Swagger Documentation
---------------------

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:5000/api/docs
- **OpenAPI Spec**: http://localhost:5000/api/spec

The Swagger interface allows you to:

- Explore all available endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download the OpenAPI specification
