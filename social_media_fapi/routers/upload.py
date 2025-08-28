import logging
import tempfile

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from social_media_fapi.libs.b2 import b2_upload_file

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile):
    try:
        with tempfile.NamesTemporyFile() as temp_file:
            filename = temp_file.name
            logger.info("Saving upload file temp {filename}")
            async with aiofiles.open(filename, "wb") as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)
            file_url = b2_upload_file(local_file=filename, file_name=file.fielname)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        )

    return {"detail": f"Successfully uploaded {file.fielname}", "file_url": file_url}
