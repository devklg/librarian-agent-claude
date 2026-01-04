from fastapi import UploadFile, HTTPException
from pathlib import Path
import uuid
import aiofiles
from typing import Dict, Any

UPLOAD_DIR = Path("./uploads")
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.md', '.html'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

async def handle_file_upload(file: UploadFile, category: str = "general") -> Dict[str, Any]:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

    doc_id = str(uuid.uuid4())
    filename = f"{doc_id}{ext}"
    filepath = UPLOAD_DIR / filename

    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(content)

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "saved_as": filename,
        "size": len(content),
        "category": category,
        "status": "uploaded"
    }
