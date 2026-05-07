"""
FastAPI File Management Server

A FastAPI-based file management server built by Dr Python Solutions for uploading, downloading, and managing CSV and JSON files with built-in validation, security features, and comprehensive error handling.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rich import print as rprint
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".json"}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Response models
class UploadResponse(BaseModel):
    """Response model for file upload."""
    message: str
    filename: str
    path: str
    size_bytes: int


class FileListResponse(BaseModel):
    """Response model for file listing."""
    files: List[Dict[str, Any]]
    total_count: int


class ErrorResponse(BaseModel):
    """Response model for errors."""
    detail: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    upload_dir: str
    upload_dir_exists: bool


# Initialize FastAPI app (without lifespan for now to avoid issues)
app = FastAPI(
    title="File Management API",
    description='A FastAPI-based file management server built by <b><i><a href="https://drpythonsolutions.netlify.app" target="_blank">Dr Python Solutions</a></i></b> for uploading, downloading, and managing CSV and JSON files with built-in validation, security features, and comprehensive error handling.',
    version="1.0.0"
)

# Add CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Handle startup tasks."""
    rprint(f"[green]✓ Upload directory: {UPLOAD_DIR.absolute()}[/green]")
    rprint(f"[green]✓ Max file size: {MAX_FILE_SIZE_MB}MB[/green]")
    rprint(f"[green]✓ Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}[/green]")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown tasks."""
    rprint("[yellow]Server shutting down...[/yellow]")


# Utility functions
def validate_filename(filename: str) -> None:
    """
    Validate filename for security.
    
    Args:
        filename: Name of the file to validate
        
    Raises:
        HTTPException: If filename is invalid or potentially dangerous
    """
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty"
        )
    
    # Prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: path traversal detected"
        )
    
    # Check file extension
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def get_file_info(filepath: Path) -> Dict[str, Any]:
    """
    Get file information.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary containing file metadata
    """
    stat = filepath.stat()
    return {
        "filename": filepath.name,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": stat.st_mtime,
        "extension": filepath.suffix.lower()
    }


# API Endpoints

@app.get("/", tags=["General"])
async def root():
    """A FastAPI-based file management server built by Dr Python Solutions for uploading, downloading, and managing CSV and JSON files with built-in validation, security features, and comprehensive error handling."""
    return {
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


@app.get(
    "/health", 
    response_model=HealthResponse,
    tags=["General"]
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        Server health status and configuration info
    """
    try:
        return HealthResponse(
            status="healthy",
            upload_dir=str(UPLOAD_DIR.absolute()),
            upload_dir_exists=UPLOAD_DIR.exists()
        )
    except Exception as e:
        rprint(f"[red]✗ Health check error: {e}[/red]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@app.post(
    "/upload-csv",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["CSV Operations"]
)
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a CSV file to the server.
    
    Args:
        file: CSV file to upload
        
    Returns:
        Upload confirmation with file details
        
    Raises:
        HTTPException: If file validation fails or upload error occurs
    """
    return await _upload_file(file, ".csv")


@app.post(
    "/upload-json",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["JSON Operations"]
)
async def upload_json(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a JSON file to the server.
    
    Args:
        file: JSON file to upload
        
    Returns:
        Upload confirmation with file details
        
    Raises:
        HTTPException: If file validation fails or upload error occurs
    """
    return await _upload_file(file, ".json")


async def _upload_file(file: UploadFile, expected_ext: str) -> UploadResponse:
    """
    Internal function to handle file uploads.
    
    Args:
        file: File to upload
        expected_ext: Expected file extension (e.g., '.csv')
        
    Returns:
        Upload response with file details
    """
    try:
        # Validate filename
        validate_filename(file.filename)
        
        # Check file extension matches expected
        if not file.filename.lower().endswith(expected_ext):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {expected_ext} files are allowed"
            )
        
        file_path = UPLOAD_DIR / file.filename
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
            )
        
        # Write file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        rprint(f"[green]✓ Uploaded: {file.filename} ({file_size} bytes)[/green]")
        
        return UploadResponse(
            message="File uploaded successfully",
            filename=file.filename,
            path=str(file_path),
            size_bytes=file_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        rprint(f"[red]✗ Upload error: {e}[/red]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@app.get(
    "/download/{filename}",
    tags=["File Operations"]
)
async def download_file(filename: str) -> FileResponse:
    """
    Download a file from the server.
    
    Args:
        filename: Name of the file to download
        
    Returns:
        File as download response
        
    Raises:
        HTTPException: If file not found or invalid filename
    """
    try:
        validate_filename(filename)
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {filename}"
            )
        
        # Determine media type based on extension
        media_type_map = {
            ".csv": "text/csv",
            ".json": "application/json"
        }
        media_type = media_type_map.get(
            file_path.suffix.lower(), 
            "application/octet-stream"
        )
        
        rprint(f"[blue]↓ Downloading: {filename}[/blue]")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        rprint(f"[red]✗ Download error: {e}[/red]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )


@app.get(
    "/list-files",
    response_model=FileListResponse,
    tags=["File Operations"]
)
async def list_files() -> FileListResponse:
    """
    List all uploaded files with metadata.
    
    Returns:
        List of files with their metadata
    """
    try:
        files = []
        
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                files.append(get_file_info(file_path))
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return FileListResponse(
            files=files,
            total_count=len(files)
        )
        
    except Exception as e:
        rprint(f"[red]✗ List files error: {e}[/red]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@app.delete(
    "/delete/{filename}",
    tags=["File Operations"]
)
async def delete_file(filename: str) -> Dict[str, str]:
    """
    Delete a file from the server.
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        Deletion confirmation
        
    Raises:
        HTTPException: If file not found or deletion fails
    """
    try:
        validate_filename(filename)
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {filename}"
            )
        
        file_path.unlink()
        rprint(f"[yellow]✗ Deleted: {filename}[/yellow]")
        
        return {"message": f"File deleted successfully: {filename}"}
        
    except HTTPException:
        raise
    except Exception as e:
        rprint(f"[red]✗ Delete error: {e}[/red]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}"
        )


# Run server
if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8080"))
    RELOAD = os.getenv("RELOAD", "false").lower() == "true"
    
    rprint(f"\n[bold cyan]Starting File Management API Server[/bold cyan]")
    rprint(f"[cyan]Host: {HOST}[/cyan]")
    rprint(f"[cyan]Port: {PORT}[/cyan]")
    rprint(f"[cyan]Docs: http://{HOST}:{PORT}/docs[/cyan]\n")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info"
    )