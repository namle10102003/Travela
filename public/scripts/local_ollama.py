from langchain.tools.retriever import create_retriever_tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from seed_data import connect_to_milvus
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

# Hàm khởi tạo Hệ thống truy xuất thông tin kết hợp giữa Milvus (vector) và BM25 (từ khóa)
def get_retriever(collection_name: str = "data_test") -> EnsembleRetriever:
    try:
        # Kết nối đến vectorstore Milvus
        vectorstore = connect_to_milvus('http://localhost:19530', collection_name)

        # Tạo retriever từ vectorstore (dùng truy vấn theo độ tương đồng cosine)
        milvus_retriever = vectorstore.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}  # Lấy 4 kết quả tương đồng nhất
        )

        # Lấy toàn bộ documents (giả lập input trống) để tạo retriever BM25
        documents = [
            Document(page_content=doc.page_content, metadata=doc.metadata)
            for doc in vectorstore.similarity_search("", k=100)
        ]

        # Nếu không có document nào, raise lỗi để chuyển qua fallback retriever
        if not documents:
            raise ValueError(f"Không tìm thấy documents trong collection '{collection_name}'")

        # Tạo BM25 retriever từ documents
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 4  # Số lượng kết quả trả về từ BM25

        # Kết hợp cả hai retriever với trọng số
        ensemble_retriever = EnsembleRetriever(
            retrievers=[milvus_retriever, bm25_retriever],
            weights=[0.7, 0.3]  # Ưu tiên kết quả từ vector hơn (70%)
        )
        return ensemble_retriever

    except Exception as e:
        print(f"Lỗi khi khởi tạo retriever: {str(e)}")

        # Nếu lỗi xảy ra, trả về BM25 retriever với một tài liệu mặc định báo lỗi
        default_doc = [
            Document(
                page_content="Có lỗi xảy ra khi kết nối database. Vui lòng thử lại sau.",
                metadata={"source": "error"}
            )
        ]
        return BM25Retriever.from_documents(default_doc)

# Hàm khởi tạo LLM, định nghĩa tác tử (agent), và công cụ tìm kiếm
def get_llm_and_agent(retriever, system_prompt_vi=True):
    # Tạo công cụ tìm kiếm từ retriever đã truyền vào
    tool = create_retriever_tool(
        retriever,
        "find_documents",  # Tên định danh của công cụ
        "Tìm kiếm thông tin du lịch Việt Nam."  # Mô tả sẽ được dùng cho tác tử
    )

    # Khởi tạo LLM với mô hình llama3 từ Ollama
    llm = ChatOllama(
        model="llama3",
        temperature=0,  # Giữ tính ổn định, tránh sinh câu trả lời ngẫu nhiên
        streaming=True,  # Cho phép streaming (trả lời dần)
        options={"num_predict": 256}  # Giới hạn số token sinh ra
    )

    tools = [tool]  # Danh sách công cụ tác tử có thể dùng

    # Prompt hệ thống định nghĩa cách phản hồi
    system = """
    Bạn là một trợ lý AI du lịch chuyên nghiệp cho khách Việt Nam.
    QUAN TRỌNG: Luôn trả lời 100% bằng TIẾNG VIỆT. Tuyệt đối không sử dụng tiếng Anh.
    Nếu nhận câu hỏi tiếng Anh, hãy tự dịch và trả lời bằng tiếng Việt tự nhiên, lịch sự, thân thiện.
    """

    # Cấu hình prompt với placeholder cho lịch sử hội thoại và scratchpad (ghi chú tác tử)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system.strip()),  # Thiết lập vai trò hệ thống
        MessagesPlaceholder(variable_name="chat_history"),  # Chèn lịch sử hội thoại
        ("human", "{input}"),  # Câu hỏi từ người dùng
        MessagesPlaceholder(variable_name="agent_scratchpad"),  # Dữ liệu nội bộ agent
    ])

    # Tạo agent có khả năng gọi các "function" (công cụ) như tìm kiếm
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)

    # Gắn agent vào executor để có thể thực thi qua API/chatbot
    return AgentExecutor(agent=agent, tools=tools, verbose=True, callbacks=[])