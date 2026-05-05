# File Management API

A FastAPI-based file management server for uploading, downloading, and managing CSV and JSON files with built-in validation, security features, and comprehensive error handling.

## Features

- 📤 **File Upload**: Support for CSV and JSON file uploads
- 📥 **File Download**: Download uploaded files with proper content-type headers
- 📋 **File Listing**: View all uploaded files with metadata (size, modification time, etc.)
- 🗑️ **File Deletion**: Remove files from the server
- 🔐 **Security**: Filename validation, path traversal protection, and file size limits
- 🌐 **CORS Support**: Cross-Origin Resource Sharing enabled for all origins
- 📊 **Health Monitoring**: Built-in health check endpoint
- 📖 **Interactive API Docs**: Auto-generated Swagger UI and ReDoc documentation

## Requirements

- Python ≥ 3.13
- FastAPI ≥ 0.136.0
- Uvicorn ≥ 0.44.0
- python-dotenv ≥ 1.2.2
- python-multipart ≥ 0.0.26
- rich ≥ 15.0.0

## Installation

### 1. Clone or navigate to the project directory

```bash
cd api_service
```

### 2. Create a virtual environment (recommended)

```bash
# Using venv
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e .
```

Or install individual packages:

```bash
pip install fastapi uvicorn python-dotenv python-multipart rich
```

## Configuration

Create a `.env` file in the `api_service` directory to configure the server:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8080
RELOAD=false

# File Upload Configuration
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=50
```

### Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address (0.0.0.0 for all interfaces) |
| `PORT` | `8080` | Server port number |
| `RELOAD` | `false` | Auto-reload on code changes (use `true` for development) |
| `UPLOAD_DIR` | `uploads` | Directory to store uploaded files |
| `MAX_FILE_SIZE_MB` | `50` | Maximum file size in megabytes |

## Running the Server

### Development Mode

```bash
python main.py
```

The server will start at `http://localhost:8080`

### With Auto-Reload (Development)

```env
RELOAD=true
```

Then run:
```bash
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

## API Endpoints

### Base URL

```
http://localhost:8080
```

### Interactive Documentation

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI Schema**: `http://localhost:8080/openapi.json`

---

## Endpoint Reference

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

**Response (200 OK)**
```json
{
  "name": "File Management API",
  "version": "1.0.0",
  "endpoints": {
    "upload_csv": "/upload-csv",
    "upload_json": "/upload-json",
    "download": "/download/{filename}",
    "list_files": "/list-files",
    "delete": "/delete/{filename}",
    "health": "/health"
  }
}
```

**Example**
```bash
curl http://localhost:8080/
```

---

### 2. Health Check

**GET** `/health`

Check server health status and configuration.

**Response (200 OK)**
```json
{
  "status": "healthy",
  "upload_dir": "C:\\path\\to\\uploads",
  "upload_dir_exists": true
}
```

**Example**
```bash
curl http://localhost:8080/health
```

---

### 3. Upload CSV File

**POST** `/upload-csv`

Upload a CSV file to the server.

**Request**
- **Content-Type**: `multipart/form-data`
- **Body Parameter**: `file` (file input)

**Response (201 Created)**
```json
{
  "message": "File uploaded successfully",
  "filename": "data.csv",
  "path": "C:\\path\\to\\uploads\\data.csv",
  "size_bytes": 1024
}
```

**Error Responses**

| Status | Description |
|--------|-------------|
| `400` | Invalid filename, wrong file type, or file too large |
| `413` | File exceeds maximum size limit |
| `500` | Server error during upload |

**Examples**

Using curl:
```bash
curl -X POST "http://localhost:8080/upload-csv" \
  -F "file=@data.csv"
```

Using Python requests:
```python
import requests

with open("data.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8080/upload-csv",
        files=files
    )
    print(response.json())
```

Using fetch (JavaScript):
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("http://localhost:8080/upload-csv", {
  method: "POST",
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

---

### 4. Upload JSON File

**POST** `/upload-json`

Upload a JSON file to the server.

**Request**
- **Content-Type**: `multipart/form-data`
- **Body Parameter**: `file` (file input)

**Response (201 Created)**
```json
{
  "message": "File uploaded successfully",
  "filename": "data.json",
  "path": "C:\\path\\to\\uploads\\data.json",
  "size_bytes": 2048
}
```

**Error Responses**

| Status | Description |
|--------|-------------|
| `400` | Invalid filename, wrong file type, or file too large |
| `413` | File exceeds maximum size limit |
| `500` | Server error during upload |

**Examples**

Using curl:
```bash
curl -X POST "http://localhost:8080/upload-json" \
  -F "file=@data.json"
```

Using Python requests:
```python
import requests

with open("data.json", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8080/upload-json",
        files=files
    )
    print(response.json())
```

---

### 5. List Files

**GET** `/list-files`

Retrieve a list of all uploaded files with metadata.

**Response (200 OK)**
```json
{
  "files": [
    {
      "filename": "latest_data.csv",
      "size_bytes": 5120,
      "size_mb": 0.01,
      "modified": 1714896000.0,
      "extension": ".csv"
    },
    {
      "filename": "config.json",
      "size_bytes": 2048,
      "size_mb": 0.0,
      "modified": 1714809600.0,
      "extension": ".json"
    }
  ],
  "total_count": 2
}
```

**Error Responses**

| Status | Description |
|--------|-------------|
| `500` | Server error while listing files |

**Examples**

Using curl:
```bash
curl http://localhost:8080/list-files
```

Using Python requests:
```python
import requests

response = requests.get("http://localhost:8080/list-files")
data = response.json()
print(f"Total files: {data['total_count']}")
for file in data['files']:
    print(f"- {file['filename']} ({file['size_mb']} MB)")
```

---

### 6. Download File

**GET** `/download/{filename}`

Download a file from the server.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Name of the file to download (e.g., `data.csv`) |

**Response (200 OK)**
- Returns the file with appropriate `Content-Type` header
- CSV files: `Content-Type: text/csv`
- JSON files: `Content-Type: application/json`

**Error Responses**

| Status | Description |
|--------|-------------|
| `400` | Invalid filename or path traversal attempt |
| `404` | File not found |
| `500` | Server error during download |

**Examples**

Using curl:
```bash
# Download and save file
curl -O http://localhost:8080/download/data.csv

# Download with custom output filename
curl http://localhost:8080/download/data.csv -o my_data.csv
```

Using Python requests:
```python
import requests

response = requests.get("http://localhost:8080/download/data.csv")

if response.status_code == 200:
    with open("downloaded_data.csv", "wb") as f:
        f.write(response.content)
    print("File downloaded successfully")
else:
    print(f"Error: {response.status_code}")
```

Using fetch (JavaScript):
```javascript
fetch("http://localhost:8080/download/data.csv")
  .then(response => response.blob())
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "data.csv";
    a.click();
  });
```

---

### 7. Delete File

**DELETE** `/delete/{filename}`

Delete a file from the server.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Name of the file to delete (e.g., `data.csv`) |

**Response (200 OK)**
```json
{
  "message": "File deleted successfully: data.csv"
}
```

**Error Responses**

| Status | Description |
|--------|-------------|
| `400` | Invalid filename or path traversal attempt |
| `404` | File not found |
| `500` | Server error during deletion |

**Examples**

Using curl:
```bash
curl -X DELETE "http://localhost:8080/delete/data.csv"
```

Using Python requests:
```python
import requests

response = requests.delete("http://localhost:8080/delete/data.csv")

if response.status_code == 200:
    print(response.json()["message"])
else:
    print(f"Error: {response.status_code} - {response.json()}")
```

Using fetch (JavaScript):
```javascript
fetch("http://localhost:8080/delete/data.csv", {
  method: "DELETE"
})
.then(response => response.json())
.then(data => console.log(data["message"]));
```

---

## File Constraints

### Allowed File Types
- **.csv** - CSV (Comma-Separated Values) files
- **.json** - JSON (JavaScript Object Notation) files

### Size Limits
- **Default**: 50 MB per file
- **Configurable**: Set `MAX_FILE_SIZE_MB` in `.env`

### Security Validations
- Filenames must not be empty
- Path traversal attacks prevented (`..`, `/`, `\` not allowed)
- File extension validation enforced
- File type verification during upload

## Error Handling

The API returns standard HTTP status codes with descriptive error messages.

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "Invalid file type. Allowed: .csv, .json"
}
```

**404 Not Found**
```json
{
  "detail": "File not found: unknown.csv"
}
```

**413 Payload Too Large**
```json
{
  "detail": "File too large. Maximum size: 50MB"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Upload failed: [error details]"
}
```

## CORS Configuration

The API has CORS enabled with the following settings:

```python
allow_origins=["*"]  # All origins allowed
allow_credentials=True
allow_methods=["*"]  # All HTTP methods allowed
allow_headers=["*"]  # All headers allowed
```

**Note**: In production, restrict `allow_origins` to specific domains:
```python
allow_origins=[
    "https://example.com",
    "https://app.example.com"
]
```

## Usage Examples

### Complete Upload and Download Workflow

**Python**
```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8080"

# 1. Upload a CSV file
print("Uploading CSV file...")
with open("mydata.csv", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/upload-csv",
        files={"file": f}
    )
    print(response.json())

# 2. Upload a JSON file
print("Uploading JSON file...")
with open("config.json", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/upload-json",
        files={"file": f}
    )
    print(response.json())

# 3. List all files
print("Listing files...")
response = requests.get(f"{BASE_URL}/list-files")
files = response.json()
for file in files["files"]:
    print(f"- {file['filename']} ({file['size_mb']} MB)")

# 4. Download a file
print("Downloading file...")
response = requests.get(f"{BASE_URL}/download/mydata.csv")
with open("downloaded.csv", "wb") as f:
    f.write(response.content)

# 5. Check health
print("Health check...")
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 6. Delete a file
print("Deleting file...")
response = requests.delete(f"{BASE_URL}/delete/mydata.csv")
print(response.json())
```

**JavaScript/Fetch**
```javascript
const baseURL = "http://localhost:8080";

// 1. Check health
async function checkHealth() {
  const response = await fetch(`${baseURL}/health`);
  const data = await response.json();
  console.log("Health:", data);
}

// 2. List files
async function listFiles() {
  const response = await fetch(`${baseURL}/list-files`);
  const data = await response.json();
  console.log("Files:", data.files);
}

// 3. Upload file
async function uploadFile(file, type = "csv") {
  const formData = new FormData();
  formData.append("file", file);
  
  const endpoint = type === "csv" ? "/upload-csv" : "/upload-json";
  const response = await fetch(`${baseURL}${endpoint}`, {
    method: "POST",
    body: formData
  });
  const data = await response.json();
  console.log("Upload response:", data);
}

// 4. Download file
async function downloadFile(filename) {
  const response = await fetch(`${baseURL}/download/${filename}`);
  const blob = await response.blob();
  
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

// 5. Delete file
async function deleteFile(filename) {
  const response = await fetch(`${baseURL}/delete/${filename}`, {
    method: "DELETE"
  });
  const data = await response.json();
  console.log("Delete response:", data);
}

// Run examples
checkHealth();
listFiles();
```

## Logging and Monitoring

The server uses the `rich` library for colored console output:

- ✓ (Green) - Successful operations
- ↓ (Blue) - Download operations
- ✗ (Yellow) - Delete operations
- ✗ (Red) - Errors and failures

Example output:
```
✓ Upload directory: C:\path\to\uploads
✓ Max file size: 50MB
✓ Allowed extensions: .csv, .json
✓ Uploaded: data.csv (1024 bytes)
↓ Downloading: data.csv
✗ Deleted: data.csv
```

## Troubleshooting

### Issue: "Address already in use"
**Solution**: Change the `PORT` in `.env` or kill the process using the current port.

### Issue: "Permission denied" on uploads
**Solution**: Ensure the `UPLOAD_DIR` folder exists and has write permissions.

### Issue: "Module not found"
**Solution**: Ensure all dependencies are installed: `pip install -e .`

### Issue: CORS errors in browser
**Solution**: CORS is already enabled. Check that your client is sending requests to the correct domain.

### Issue: File not found after upload
**Solution**: Verify the `UPLOAD_DIR` path in `.env` is correct and the file was successfully uploaded (check the response).

## Development

### Project Structure
```
api_service/
├── main.py              # Main application file
├── README.md            # This file
├── pyproject.toml       # Project configuration
├── .env                 # Environment variables (create manually)
└── uploads/             # Upload directory (created automatically)
```

### Code Style
The project uses:
- Type hints for all functions
- Comprehensive docstrings
- Pydantic models for request/response validation
- FastAPI best practices

### Adding New Endpoints

Example of adding a new endpoint:

```python
@app.get("/custom", tags=["Custom"])
async def custom_endpoint():
    """Custom endpoint description."""
    return {"message": "custom response"}
```

## Production Deployment

### Recommended Settings for Production

**.env**
```env
HOST=0.0.0.0
PORT=8080
RELOAD=false
UPLOAD_DIR=/var/data/uploads
MAX_FILE_SIZE_MB=100
```

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8080 \
  --access-logfile - \
  --error-logfile -
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY main.py .

ENV HOST=0.0.0.0
ENV PORT=8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Build and run:
```bash
docker build -t file-api .
docker run -p 8080:8080 -v $(pwd)/uploads:/app/uploads file-api
```

## Security Considerations

- ✓ Filename validation prevents directory traversal attacks
- ✓ File extension validation enforces allowed types
- ✓ File size limits prevent resource exhaustion
- ✓ CORS policy can be restricted for production
- ⚠️ In production, use HTTPS and restrict `allow_origins`
- ⚠️ Consider adding authentication (JWT, OAuth, etc.)
- ⚠️ Implement rate limiting for production use
- ⚠️ Store uploads in isolated directory with restricted permissions

## License

This project is part of the Pamass project.

## Support

For issues, questions, or contributions, please refer to the main project repository.

---

**Version**: 1.0.0  
**Last Updated**: May 5, 2026  
**API Base URL**: `http://localhost:8080`  
**Documentation**: `http://localhost:8080/docs`
