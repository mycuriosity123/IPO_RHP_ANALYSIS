from fastapi import FastAPI, File, UploadFile , Request
from fastapi.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError, field_validator,FilePath
from typing import Annotated
from langchain_community.document_loaders.parsers import RapidOCRBlobParser
from langchain_community.document_loaders import PyMuPDFLoader
from fastapi.responses import JSONResponse
from run_local import PDF_Analysis
import os
import json
import sys
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger_config import logger
from dotenv import load_dotenv
load_dotenv()



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
        app.state.pdf_analyser=PDF_Analysis(docs=docs)
        response_json=app.state.pdf_analyser.chunking_data()
        res=json.loads(response_json.body)
        if res["status"]=="failed":
            raise Exception(res["response"])
        logger.info(res["response"])
        return JSONResponse(status_code=200,content={"message":res["response"]})
    
    except Exception as e:
        logger.error(f"error:{e}",exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
     

class UserInput(BaseModel):
    query:str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "validation_failed",
            "errors": exc.errors()
        }
    )

@app.post("/user_query")
async def rag_search(userinput:UserInput):
    try:
        if not hasattr(app.state, "pdf_analyser"):
            return JSONResponse(status_code=400, content={"error": "No PDF uploaded and processed yet."})
        pdf_analyser = app.state.pdf_analyser
        output_json = pdf_analyser.retrieve_generation(usr_qry=userinput.query)
        res=json.loads(output_json.body)
        if res["status"]=="failed":
            raise Exception(res["response"])
        logger.info(res["response"])
        return JSONResponse(status_code=200,content={"message":res["response"]})
    except RequestValidationError as ve:
        logger.error(f"validation error:{ve}",exc_info=True)
        return JSONResponse(status_code=422,content={"error": "Invalid input", "details": ve.errors()})
    except Exception as e:
        logger.error(f"error:{e}",exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
    





        
            
   
@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000,reload=True)


