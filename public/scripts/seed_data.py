import os
import json
from langchain_community.vectorstores import Milvus
from langchain.schema import Document
from dotenv import load_dotenv
from uuid import uuid4
from crawl import crawl_web
from langchain_ollama import OllamaEmbeddings

load_dotenv()

def load_data_from_local(filename: str, directory: str) -> tuple:
    """
    Hàm đọc dữ liệu từ file JSON local
    Args:
        filename (str): Tên file JSON cần đọc (ví dụ: 'data.json')
        directory (str): Thư mục chứa file (ví dụ: 'data_v3')
    Returns:
        tuple: Trả về (data, doc_name) trong đó:
            - data: Dữ liệu JSON đã được parse
            - doc_name: Tên tài liệu đã được xử lý (bỏ đuôi .json và thay '_' bằng khoảng trắng)
    """
    file_path = os.path.join(directory, filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    print(f'Data loaded from {file_path}')
    return data, filename.rsplit('.', 1)[0].replace('_', ' ')

def seed_milvus(URI_link: str, collection_name: str, filename: str, directory: str):
    """
    Hàm tạo và lưu vector embeddings vào Milvus từ dữ liệu local
    Args:
        URI_link (str): Đường dẫn kết nối đến Milvus
        collection_name (str): Tên collection trong Milvus để lưu dữ liệu
        filename (str): Tên file JSON chứa dữ liệu nguồn
        directory (str): Thư mục chứa file dữ liệu
    """
    embeddings = OllamaEmbeddings(model="llama3")
    
    # Đọc dữ liệu từ file local
    local_data, doc_name = load_data_from_local(filename, directory)

    # Chuyển đổi dữ liệu thành danh sách các Document
    documents = [
        Document(
            page_content=doc.get('page_content') or '',
            metadata={
                'source': doc['metadata'].get('source') or '',
                'content_type': doc['metadata'].get('content_type') or 'text/plain',
                'title': doc['metadata'].get('title') or '',
                'description': doc['metadata'].get('description') or '',
                'language': doc['metadata'].get('language') or 'vi',
                'doc_name': doc_name,
                'start_index': doc['metadata'].get('start_index') or 0
            }
        )
        for doc in local_data
    ]

    print('documents: ', documents)

    # Tạo ID duy nhất cho mỗi document
    uuids = [str(uuid4()) for _ in range(len(documents))]

    # Khởi tạo và cấu hình Milvus
    vectorstore = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": URI_link},
        collection_name=collection_name,
        drop_old=True
    )
    # Thêm documents vào Milvus
    vectorstore.add_documents(documents=documents, ids=uuids)
    print('vector: ', vectorstore)
    return vectorstore

def seed_milvus_live(URL: str, URI_link: str, collection_name: str, doc_name: str) -> Milvus:
    """
    Hàm crawl dữ liệu trực tiếp từ URL và tạo vector embeddings trong Milvus
    Args:
        URL (str): URL của trang web cần crawl dữ liệu
        URI_link (str): Đường dẫn kết nối đến Milvus
        collection_name (str): Tên collection trong Milvus
        doc_name (str): Tên định danh cho tài liệu được crawl
    """
    embeddings = OllamaEmbeddings(model="llama3")
    
    documents = crawl_web(URL)

    # Cập nhật metadata cho mỗi document
    for doc in documents:
        metadata = {
            'source': doc.metadata.get('source') or '',
            'content_type': doc.metadata.get('content_type') or 'text/plain',
            'title': doc.metadata.get('title') or '',
            'description': doc.metadata.get('description') or '',
            'language': doc.metadata.get('language') or 'vi',
            'doc_name': doc_name,
            'start_index': doc.metadata.get('start_index') or 0
        }
        doc.metadata = metadata

    uuids = [str(uuid4()) for _ in range(len(documents))]

    vectorstore = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": URI_link},
        collection_name=collection_name,
        drop_old=True
    )
    # Thêm documents vào Milvus
    vectorstore.add_documents(documents=documents, ids=uuids)
    print('vector: ', vectorstore)
    return vectorstore

def connect_to_milvus(URI_link: str, collection_name: str) -> Milvus:
    """
    Hàm kết nối đến collection có sẵn trong Milvus
    Args:
        URI_link (str): Đường dẫn kết nối đến Milvus
        collection_name (str): Tên collection cần kết nối
    Returns:
        Milvus: Đối tượng Milvus đã được kết nối, sẵn sàng để truy vấn
    """
    embeddings = OllamaEmbeddings(model="llama3")
    vectorstore = Milvus(
        embedding_function=embeddings,
        connection_args={"uri": URI_link},
        collection_name=collection_name,
    )
    return vectorstore

def main():
    """
    Hàm chính để kiểm thử các chức năng của module
    """
    seed_milvus('http://localhost:19530', 'data_test', 'tour.json', 'data')
    # seed_milvus_live('https://www.stack-ai.com/docs', 'http://localhost:19530', 'data_test_live', 'stack-ai')

if __name__ == "__main__":
    main()