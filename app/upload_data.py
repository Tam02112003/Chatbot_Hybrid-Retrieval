from datetime import datetime
import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.pkgs.model import EMBEDDING_MODEL
from app.crud.HybridSearch import extract_triples_from_text
from app.pkgs.Neo4jManager import neo4j_graph


UPLOAD_LOG_FILE = "app/upload_history.json"

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)


def show_upload_history():
    if not os.path.exists(UPLOAD_LOG_FILE):
        return "Chưa có file nào được upload."

    with open(UPLOAD_LOG_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)

    output = "📁 **Lịch sử Upload:**\n"
    for record in history:
        output += f"\n📝 `{record['file_name']}` ({record['num_chunks']} chunks) - {record['upload_time']}\n"
        for i, chunk in enumerate(record["chunk_preview"][:3]):  # Xem trước 3 chunks
            output += f"  🔹 Đoạn {i+1}: {chunk.strip()[:100]}...\n"
        if len(record["chunk_preview"]) > 3:
            output += f"  ... ({len(record['chunk_preview']) - 3} đoạn nữa)\n"
    return output

def save_upload_history(file_name, chunks):
    history = []
    if os.path.exists(UPLOAD_LOG_FILE):
        with open(UPLOAD_LOG_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    record = {
        "file_name": file_name,
        "upload_time": datetime.now().isoformat(),
        "num_chunks": len(chunks),
        "chunk_preview": [c.page_content[:300] for c in chunks]
    }

    history.append(record)
    with open(UPLOAD_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# -------- Xử lý nội dung Markdown in-memory
def process_uploaded_markdown_file_directly(uploaded_file):


    # Đọc nội dung file
    content = uploaded_file.file.read().decode("utf-8")
    doc = Document(page_content=content)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents([doc])

    # 1️⃣ Lưu triples vào Neo4j
    all_triples = []
    for chunk in chunks:
        text = chunk.page_content.strip()
        if len(text) >= 50:
            triples = extract_triples_from_text(text)
            for s, p, o in triples:
                cypher = f"""
                MERGE (s:Entity {{name: '{s}'}})
                MERGE (o:Entity {{name: '{o}'}})
                MERGE (s)-[:`{p}`]->(o)
                """
                neo4j_graph.query(cypher)
            all_triples.extend(triples)

    # 2️⃣ Lưu vector semantic vào FAISS
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    vectorstore.save_local("faiss_index")
    # Lưu lịch sử upload
    save_upload_history(uploaded_file.filename, chunks)
    print(f"✅ Đã lưu {len(all_triples)} triples và index FAISS.")
    return len(all_triples)


# Xử lý file Markdown để sinh vector FAISS
def process_uploaded_vector_only(uploaded_file):
    
    # Đọc nội dung
    content = uploaded_file.file.read().decode("utf-8")
    doc = Document(page_content=content)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents([doc])

    # Tạo FAISS index
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    vectorstore.save_local("faiss_index")
    save_upload_history(uploaded_file.filename, chunks)
    print(f"✅ Đã index {len(chunks)} đoạn văn.")
    return len(chunks)
    