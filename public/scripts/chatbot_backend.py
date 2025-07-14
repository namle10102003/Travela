import sys
import json
import logging
import os
import re
from pymilvus import connections
from dotenv import load_dotenv
from semantic_retriever import query_rdf_by_keyword
from hybrid_retriever import get_hybrid_retriever
from local_ollama import get_retriever, get_llm_and_agent
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

# Cấu hình logging
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Kết nối Milvus
def connect_milvus():
    try:
        connections.connect(alias='default', host="localhost", port="19530")
        logger.info("Đã kết nối thành công đến Milvus")
        return True
    except Exception as e:
        logger.error(f"Lỗi kết nối Milvus: {str(e)}")
        return False

# Lưu trữ lịch sử chat
CHAT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "chat_history.json")
def load_chat_history():
    try:
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# Prompt template
prompt_template = PromptTemplate(
    input_variables=["input", "chat_history"],
    template="""
    Bạn là chatbot du lịch thông minh, giúp người dùng tìm thông tin về du lịch Việt Nam.
    Dựa trên câu hỏi, thông tin từ Milvus (vector search), RDF (tri thức ngữ nghĩa), và lịch sử trò chuyện, hãy trả lời bằng tiếng Việt chuẩn, tự nhiên, ngắn gọn (2-3 câu).
    Nếu câu hỏi bằng tiếng Anh, dịch sang tiếng Việt và trả lời.

    - Câu hỏi: {input}
    - Lịch sử trò chuyện: {chat_history}
    """
)

def format_rdf_data(semantic_info):
    """Định dạng dữ liệu RDF để dễ đọc hơn."""
    if not semantic_info:
        return "Không tìm thấy dữ liệu RDF phù hợp."
    
    formatted = "Dữ liệu RDF thu thập được:\n"
    if isinstance(semantic_info, list):
        for idx, item in enumerate(semantic_info, 1):
            if isinstance(item, tuple) and len(item) == 3:
                subject = item[0].split("#")[-1].replace('_', ' ').title()
                predicate = item[1].split("#")[-1].replace('_', ' ').title()
                obj = item[2]
                formatted += f"  {idx}. Chủ thể: {subject}\n     Vị ngữ: {predicate}\n     Đối tượng: {obj}\n"
            else:
                formatted += f"  {idx}. {item}\n"
    else:
        formatted += f"  {semantic_info}\n"
    return formatted

def normalize_text(text):
    """Chuẩn hóa câu hỏi để sửa lỗi ký tự."""
    text = re.sub(r'd\?c s\?n', 'đặc sản', text)
    text = re.sub(r'H\?i An', 'Hội An', text)
    return text

def main():
    if len(sys.argv) < 2:
        print("Vui lòng cung cấp câu hỏi.")
        return

    question = normalize_text(sys.argv[1])
    logger.info(f"Processing question: {question}")

    # Kết nối Milvus
    if not connect_milvus():
        print("Không thể kết nối đến Milvus. Vui lòng kiểm tra server.")
        return

    # Load .env
    load_dotenv()

    # Khởi tạo hybrid retriever
    try:
        hybrid_retriever = get_hybrid_retriever(
            collection_name="data_test",
            rdf_path="data/data.rdf"
        )
    except Exception as e:
        logger.error(f"Lỗi khởi tạo hybrid retriever: {str(e)}")
        print("Lỗi khởi tạo retriever.")
        return

    # Khởi tạo Ollama agent
    try:
        retriever = get_retriever(collection_name="data_test")
        agent_executor = get_llm_and_agent(retriever)
    except Exception as e:
        logger.error(f"Lỗi khởi tạo Ollama agent: {str(e)}")
        print("Lỗi khởi tạo AI.")
        return

    # Kiểm tra từ khóa để truy vấn RDF và Milvus
    keyword_trigger = any(word in question.lower() for word in [
        "ẩm thực", "món ăn", "đặc sản", "ăn gì", "ăn uống", "món ngon", "thức ăn", "quán ăn", "nhà hàng",
        "địa điểm", "thắng cảnh", "điểm đến", "nổi bật", "du lịch", "đi đâu", "tham quan",
        "văn hóa", "lễ hội", "phong tục", "truyền thống", "dân tộc", "lịch sử", "di sản",
        "tour", "tour du lịch", "gói tour", "lịch trình", "hành trình", "chuyến đi", "tìm kiếm"
    ])

    # Truy vấn RDF và Milvus
    semantic_info = None
    milvus_info = None
    if keyword_trigger:
        try:
            semantic_info = query_rdf_by_keyword(question)
            logger.info(f"Raw RDF data before formatting: {semantic_info}")
            if semantic_info:
                formatted_rdf = format_rdf_data(semantic_info)
                print("✅ Dữ liệu RDF liên quan:")
                print(formatted_rdf)
                logger.info(f"RDF results:\n{formatted_rdf}")
            else:
                print("⚠️ Không tìm thấy thông tin RDF phù hợp.")
                logger.info("RDF results: Không tìm thấy thông tin RDF phù hợp")
        except Exception as e:
            logger.error(f"Lỗi khi truy vấn RDF: {str(e)}")
            print(f"❌ Lỗi khi truy vấn RDF: {str(e)}")

        try:
            milvus_results = hybrid_retriever.hybrid_search(question, top_k=3)
            milvus_info = "\n".join([result['text'] for result in milvus_results['combined_results'][:3]])
            logger.info(f"Milvus results: {milvus_info}")
            print("✅ Dữ liệu từ Milvus:")
            print(milvus_info if milvus_info else "⚠️ Không tìm thấy thông tin từ Milvus.")
        except Exception as e:
            logger.error(f"Lỗi khi truy vấn Milvus: {str(e)}")
            print(f"❌ Lỗi khi truy vấn Milvus: {str(e)}")

    # Tạo prompt
    prompt = "LUÔN LUÔN trả lời bằng tiếng Việt chuẩn, tự nhiên.\n"
    prompt += "Kết hợp thông tin từ RDF và Milvus để trả lời câu hỏi một cách chi tiết, tự nhiên, ngắn gọn (2-3 câu).\n"
    if semantic_info:
        prompt += f"\nThông tin từ RDF:\n{format_rdf_data(semantic_info)}\n"
    if milvus_info:
        prompt += f"\nThông tin từ Milvus:\n{milvus_info}\n"
    prompt += f"\nCâu hỏi: {question}"

    # Lấy lịch sử chat
    chat_history = []
    for h in load_chat_history()[-3:]:
        chat_history.append(HumanMessage(content=h['question']))
        chat_history.append(AIMessage(content=h['answer']))

    # Gọi agent_executor
    try:
        response = agent_executor.invoke(
            {"input": prompt, "chat_history": chat_history}
        )
        answer = response["output"]
        
        # Lưu lịch sử chat
        chat_history_data = load_chat_history()
        chat_history_data.append({"question": question, "answer": answer})
        save_chat_history(chat_history_data)
        
        print("\n📝 Câu trả lời:")
        print(answer)
    except Exception as e:
        logger.error(f"Error calling AI: {str(e)}")
        print("Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi.")

if __name__ == "__main__":
    main()