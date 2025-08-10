import os
import re

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from app.pkgs.model import call_gemma3n_api, call_llm_studio_api
from app.pkgs.Neo4jManager import neo4j_graph

# -------- Trích xuất triples từ văn bản
def extract_triples_from_text(text: str):
    text = text.strip()[:1000]
    prompt = f"""
    Trích xuất các mối quan hệ (triple) từ đoạn văn sau, theo dạng:
    (Chủ ngữ, Quan hệ, Tân ngữ)
    
    Không cần giải thích gì thêm, chỉ cần trả về các triple theo định dạng
    Văn bản:
    {text}
    Kết quả:
    """.strip()

    try:
        output = call_gemma3n_api(prompt)
        print(f'📤 Output từ Gemma3n:\n', output)
        triple_pattern = r"[\*\-]?\s*\(([^,]+?),\s*([^,]+?),\s*([^)]+?)\)"
        matches = re.findall(triple_pattern, output)

        triples = [tuple(p.strip().replace("'", "\\'") for p in match) for match in matches]
        return triples
    except Exception as e:
        print(f"⚠️ Lỗi khi gọi LLM: {e}")
        return []



def semantic_search(question: str, top_k: int = 3):
    if not os.path.exists("app/faiss_index"):
        print("⚠️ Chưa có index FAISS, vui lòng upload file trước.")
        return []

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.load_local("app/faiss_index", embedding_model, allow_dangerous_deserialization=True)
    return vectorstore.similarity_search(question, k=top_k)

# -------- Trích xuất thực thể từ câu hỏi
def extract_entity_from_question(question: str) -> str:
    prompt = f"""
Từ câu hỏi sau, trích xuất **tên đối tượng chính** (ví dụ tổ chức, sản phẩm, dịch vụ,...)

Ví dụ:
Câu hỏi: "HDBank cung cấp dịch vụ gì?" → HDBank
Câu hỏi: "Dịch vụ kiều hối có những ưu đãi nào?" → Dịch vụ kiều hối

Câu hỏi: "{question}"
Đối tượng:
""".strip()

    try:
        response = call_gemma3n_api(prompt).strip()
        return response
    except Exception as e:
        print(f"⚠️ Lỗi khi tách entity: {e}")
        return ""

# -------- Truy vấn quan hệ từ entity
def query_relations_from_entity(entity: str):
    cypher = f"""
    MATCH (e:Entity)-[r]->(o:Entity)
    WHERE toLower(e.name) CONTAINS '{entity.lower()}'
    RETURN e.name AS ChuNgu, type(r) AS QuanHe, o.name AS TanNgu
    LIMIT 50
    """
    try:
        return neo4j_graph.query(cypher)
    except Exception as e:
        print(f"⚠️ Lỗi Cypher: {e}")
        return []

# -------- Truy vấn
def ask_question(question: str):
    entity = extract_entity_from_question(question)
    graph_results = query_relations_from_entity(entity) if entity else []

    semantic_results = semantic_search(question)

    context_chunks = "\n".join(
        f"- {doc.page_content[:300]}" for doc in semantic_results
    ) if semantic_results else ""

    graph_info = "\n".join(
        f"- {r['ChuNgu']} {r['QuanHe']} {r['TanNgu']}" for r in graph_results
    ) if graph_results else ""

    # Tạo prompt tổng hợp từ 2 nguồn
    prompt = f"""
Người dùng hỏi: "{question}"

Thông tin tìm được từ graph:
{graph_info if graph_info else '(Không có)'}

Các đoạn văn liên quan từ semantic search:
{context_chunks if context_chunks else '(Không có)'}

Nếu trong đó có đường link trùng nhau thì chỉ giữ một
Hãy trả lời một cách thân thiện như một trợ lý ảo của công ty HDBank.
""".strip()

    try:
        return "💬 " + call_gemma3n_api(prompt).strip()
    except:
        return f"{graph_info}\n{context_chunks}"



