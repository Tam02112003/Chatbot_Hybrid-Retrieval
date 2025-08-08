from langchain_community.vectorstores import FAISS
from app.pkgs.model import call_gemma3n_api
from app.upload_data import embedding_model



# Tìm kiếm theo semantic
def semantic_search(question: str, top_k: int = 3):
    vectorstore = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)
    return vectorstore.similarity_search(question, k=top_k)

# Hỏi và kết hợp thông tin để trả lời
def ask_rag_question(question: str):
    semantic_results = semantic_search(question)

    context_chunks = "\n".join(
        f"- {doc.page_content[:300]}" for doc in semantic_results
    ) if semantic_results else "(Không có ngữ cảnh phù hợp)"

    prompt = f"""
Người dùng hỏi: "{question}"

Các đoạn văn liên quan từ semantic search:
{context_chunks}

Hãy trả lời một cách thân thiện như một trợ lý ảo của công ty HDBank.
""".strip()

    try:
        return "💬 " + call_gemma3n_api(prompt).strip()
    except Exception as e:
        print(f"❌ Lỗi gọi LLM: {e}")
        return context_chunks
