from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError, field_validator,FilePath
from typing import Annotated
from langchain_community.document_loaders.parsers import RapidOCRBlobParser
from langchain_community.document_loaders import PyMuPDFLoader
from fastapi.responses import JSONResponse
from .run_local import chunking_data , retrieve_generation
import os
import json
from logger_config import logger


app = FastAPI()

DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(status_code=400, content={"error": "File must be a PDF."})

    file_location = os.path.join(DATA_DIR, file.filename)
    try:
        contents = await file.read()
        with open(file_location, 'wb') as f:
            f.write(contents)
        loader = PyMuPDFLoader(file_location, mode="page", images_inner_format="markdown-img",images_parser=RapidOCRBlobParser())
        docs = loader.load()
        logger.info("file was parsed successfully using PyMUPDFLoader")
        response_json=chunking_data(docs)
        res=json.loads(response_json.body)
        if res["status"]=="failed":
            raise Exception(res["response"])
        logger.info(res["response"])
        return JSONResponse(status_code=200,content={"message":res["response"]})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
     

        
            
   
@app.get("/")
def read_root():
    return {"Hello": "World"}

# if __name__=="__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


