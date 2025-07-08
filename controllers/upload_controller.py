# file: controllers/upload_controller.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import shutil
import uuid
from pathlib import Path
from auth import require_permission

router = APIRouter()

UPLOAD_DIRECTORY = Path("static/images")

@router.post("/image", dependencies=[Depends(require_permission("FILE_UPLOAD"))])
async def upload_image(file: UploadFile = File(...)):
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    
    unique_id = uuid.uuid4()
    # Sanitize filename
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('.', '_', '-')).strip()
    filename = f"{unique_id}_{safe_filename}"
    file_path = UPLOAD_DIRECTORY / filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    # Return a relative URL path
    return {"url": f"/{file_path.as_posix()}"}