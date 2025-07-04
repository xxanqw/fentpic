# API Reference

FENTPIC provides a RESTful API for programmatic access to image hosting functionality. The API supports JSON responses and follows REST conventions.

## Base URL

```
http://localhost:5000/api
```

## Authentication

The API uses session-based authentication. Users must be logged in to access protected endpoints.

### Session Authentication

Include session cookies with your requests. For web applications, this happens automatically. For programmatic access, you'll need to maintain session state.

## Endpoints

### Upload Images

Upload one or more image files to the platform.

**Endpoint:** `POST /api/upload`

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file[] | Yes | One or more image files |
| `is_public` | boolean | No | Whether images should be public (default: true) |

**Supported Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

**File Size Limit:** 20MB per file

**Example Request:**

```bash
curl -X POST \
  http://localhost:5000/api/upload \
  -F "file=@image1.jpg" \
  -F "file=@image2.png" \
  -F "is_public=true" \
  -b "session=your-session-cookie"
```

**Example Response:**

```json
{
  "success": true,
  "images": [
    {
      "id": 123,
      "filename": "image1.jpg",
      "url": "/uploads/uuid_image1.jpg",
      "size": 1048576,
      "uploaded_at": "2025-07-04T12:00:00Z",
      "is_public": true
    },
    {
      "id": 124,
      "filename": "image2.png",
      "url": "/uploads/uuid_image2.png",
      "size": 2097152,
      "uploaded_at": "2025-07-04T12:00:01Z",
      "is_public": true
    }
  ],
  "message": "Successfully uploaded 2 image(s)"
}
```

**Error Responses:**

```json
{
  "error": "No file provided",
  "code": 400
}
```

```json
{
  "error": "Authentication required",
  "code": 401
}
```

### Get User Images

Retrieve a paginated list of images uploaded by the authenticated user.

**Endpoint:** `GET /api/images`

**Authentication:** Required

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number for pagination |
| `limit` | integer | No | 20 | Number of images per page (max 100) |
| `public_only` | boolean | No | false | Filter to only public images |

**Example Request:**

```bash
curl -X GET \
  "http://localhost:5000/api/images?page=1&limit=10&public_only=false" \
  -b "session=your-session-cookie"
```

**Example Response:**

```json
{
  "images": [
    {
      "id": 123,
      "filename": "sunset.jpg",
      "url": "/uploads/uuid_sunset.jpg",
      "size": 1048576,
      "uploaded_at": "2025-07-04T12:00:00Z",
      "is_public": true
    },
    {
      "id": 122,
      "filename": "private-doc.png",
      "url": "/uploads/uuid_private-doc.png",
      "size": 512000,
      "uploaded_at": "2025-07-04T11:30:00Z",
      "is_public": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

**Error Response:**

```json
{
  "error": "Authentication required",
  "code": 401
}
```

## Response Format

All API responses use JSON format with consistent structure:

### Success Response

```json
{
  "success": true,
  "data": {}, // Response data
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "error": "Error description",
  "code": 400,
  "details": [] // Optional additional error details
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters or file format |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 413 | Payload Too Large - File size exceeds limit |
| 500 | Internal Server Error |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Upload endpoint:** 10 requests per minute per user
- **Get images endpoint:** 60 requests per minute per user

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1641024000
```

## Error Handling

### File Validation Errors

When uploading files, various validation errors may occur:

```json
{
  "error": "No images uploaded",
  "details": [
    "Invalid file type for document.pdf",
    "File large-image.jpg exceeds size limit",
    "Invalid image format for corrupted.jpg"
  ],
  "code": 400
}
```

### Common Error Scenarios

1. **Invalid file format**
   - Only JPEG, PNG, GIF, and WebP are supported
   - File content must match the file extension

2. **File size exceeded**
   - Maximum file size is 20MB per file
   - Total upload size should not exceed reasonable limits

3. **Authentication issues**
   - Session expired or invalid
   - User not logged in

## Swagger Documentation

Interactive API documentation is available at:

```
http://localhost:5000/api/docs
```

The OpenAPI specification can be found at:

```
http://localhost:5000/api/spec
```

## SDK and Libraries

### Python

```python
import requests

class FentpicAPI:
    def __init__(self, base_url, session_cookie):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.cookies.set('session', session_cookie)
    
    def upload_images(self, files, is_public=True):
        """Upload images to FENTPIC"""
        url = f"{self.base_url}/api/upload"
        
        file_data = []
        for file_path in files:
            with open(file_path, 'rb') as f:
                file_data.append(('file', f))
        
        data = {'is_public': is_public}
        response = self.session.post(url, files=file_data, data=data)
        return response.json()
    
    def get_images(self, page=1, limit=20, public_only=False):
        """Get user's images"""
        url = f"{self.base_url}/api/images"
        params = {
            'page': page,
            'limit': limit,
            'public_only': public_only
        }
        response = self.session.get(url, params=params)
        return response.json()

# Usage
api = FentpicAPI('http://localhost:5000', 'your-session-cookie')
result = api.upload_images(['image1.jpg', 'image2.png'])
print(result)
```

### JavaScript

```javascript
class FentpicAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async uploadImages(files, isPublic = true) {
        const formData = new FormData();
        
        files.forEach(file => {
            formData.append('file', file);
        });
        
        formData.append('is_public', isPublic);
        
        const response = await fetch(`${this.baseUrl}/api/upload`, {
            method: 'POST',
            body: formData,
            credentials: 'include' // Include session cookies
        });
        
        return await response.json();
    }
    
    async getImages(page = 1, limit = 20, publicOnly = false) {
        const params = new URLSearchParams({
            page: page.toString(),
            limit: limit.toString(),
            public_only: publicOnly.toString()
        });
        
        const response = await fetch(`${this.baseUrl}/api/images?${params}`, {
            credentials: 'include'
        });
        
        return await response.json();
    }
}

// Usage
const api = new FentpicAPI('http://localhost:5000');

// Upload files from file input
const fileInput = document.getElementById('fileInput');
const result = await api.uploadImages(fileInput.files);
console.log(result);
```

## Testing the API

### Using cURL

```bash
# Upload an image
curl -X POST \
  http://localhost:5000/api/upload \
  -F "file=@test-image.jpg" \
  -F "is_public=true" \
  -b "session=your-session-cookie"

# Get images
curl -X GET \
  "http://localhost:5000/api/images?limit=5" \
  -b "session=your-session-cookie"
```

### Using Postman

1. Import the OpenAPI specification from `/api/spec`
2. Set up authentication by including session cookies
3. Test endpoints with various parameters

### Using the Swagger UI

Visit `http://localhost:5000/api/docs` to interactively test the API endpoints with a web interface.
