import json
import os
import traceback
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.upload_data import process_uploaded_vector_only, UPLOAD_LOG_FILE, process_uploaded_markdown_file_directly
from app.crud.HybridSearch import extract_triples_from_text, ask_question
from app.crud.GraphRAG import ask_question_with_graphrag
from app.crud.RAG_VectorSearch import ask_rag_question
app = FastAPI()

# Cho phép CORS nếu cần cho frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "🧠 LangChain + FastAPI is running!"}


@app.post("/hybrid/ask")
def ask(query: str = Form(...)):
    try:
        answer = ask_question(query)
        return {"question": query, "answer": answer}
    except Exception as e:
        # Ghi chi tiết lỗi ra log
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback_str})

@app.post("/graph_rag/ask")
def ask(query: str = Form(...)):
    try:
        answer = ask_question_with_graphrag(query)
        return {"question": query, "answer": answer}
    except Exception as e:
        # Ghi chi tiết lỗi ra log
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback_str})
    
@app.post("/rag/ask")
def rag_ask(query: str = Form(...)):
    try:
        answer = ask_rag_question(query)
        return {"question": query, "answer": answer}
    except Exception as e:
        # Ghi chi tiết lỗi ra log
        traceback_str = traceback.format_exc()
        print(traceback_str)
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback_str})


@app.post("/graphrag_vector/upload")
def upload_markdown(file: UploadFile = File(...)):
    try:
        triple_count = process_uploaded_markdown_file_directly(file)
        return {"message": f"✅ Đã xử lý file {file.filename}, trích xuất {triple_count} triples"}
    except Exception as e:
        import traceback
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})


@app.post("/vector/upload")
def upload_vector(file: UploadFile = File(...)):
    try:
        process_uploaded_vector_only(file)
        return {"message": f"✅ Đã xử lý file {file.filename}"}
    except Exception as e:
        import traceback
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})


@app.get("/upload_history")
def get_upload_history():
    if not os.path.exists(UPLOAD_LOG_FILE):
        return []
    with open(UPLOAD_LOG_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    return history

@app.post("/extract-triples")
def extract(text: str = Form(...)):
    try:
        triples = extract_triples_from_text(text)
        return {"triples": triples}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
