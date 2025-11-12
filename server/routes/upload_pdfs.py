from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from modules.load_vectorstore import load_vectorstore
from logger import logger


router=APIRouter()

@router.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    try:
        logger.info("Received uploaded files")
        count = load_vectorstore(files)
        logger.info(f"Documents added to vectorstore: {count}")
        return {"message": f"Successfully processed {len(files)} files and added {count} chunks to vectorstore"}
    except ValueError as e:
        logger.warning(f"Invalid files: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error during PDF upload")
        raise HTTPException(status_code=500, detail="Internal server error")