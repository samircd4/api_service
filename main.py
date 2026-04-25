from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
import requests
import time
import os
import shutil
from rich import print
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

MAX_RETRIES = 3
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- CSV File Management Endpoints ---

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Check if the uploaded file is a CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only .csv files are allowed")

        # We use the original filename to allow overwriting/updating
        # Warning: Ensure the filename is safe
        filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, filename)

        # If the file already exists, 'wb' mode will overwrite it automatically
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "File updated/uploaded successfully",
            "filename": filename,
            "path": file_path
        }
    except Exception as e:
        print(f"Error during upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='text/csv'
    )

@app.get("/list-files")
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)