from app.pkgs.model import call_gemma3n_api
from app.pkgs.Neo4jManager import neo4j_graph


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
def ask_question_with_graphrag(question: str):
    entity = extract_entity_from_question(question)
    if not entity:
        return "🤖 Tôi không xác định được nội dung bạn hỏi."

    results = query_relations_from_entity(entity)
    if not results:
        return f"🤖 Không tìm thấy dữ liệu liên quan đến: {entity}"

    rows = [f"- {r['ChuNgu']} {r['QuanHe']} {r['TanNgu']}" for r in results]

    prompt = f"""
Người dùng hỏi: "{question}"

Tôi thu được các thông tin sau:
{chr(10).join(rows)}

Nếu trong đó có đường link trùng nhau thì chỉ giữ một

Hãy trả lời một cách thân thiện như một trợ lý ảo của công ty HDBank.
"""
    try:
        return "💬 " + call_gemma3n_api(prompt).strip()
    except:
        return "\n".join(rows)

