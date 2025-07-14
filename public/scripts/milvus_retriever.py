from typing import List, Dict, Any, Optional
import logging
import sys
import codecs
from pymilvus import Collection, connections, utility
from langchain_community.vectorstores import Milvus
from langchain_ollama import OllamaEmbeddings


# Kiểm tra nếu chạy qua web (giả định từ tham số --web)
is_web_mode = "--web" in sys.argv if len(sys.argv) > 1 else False

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("milvus_retriever.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MilvusRetriever:
    def __init__(self, 
                 collection_name: str, 
                 milvus_host: str = 'localhost', 
                 milvus_port: str = '19530'):
        """
        Khởi tạo trình truy xuất Milvus
        
        :param collection_name: Tên collection trong Milvus
        :param milvus_host: Host của Milvus server
        :param milvus_port: Port của Milvus server
        """
        # Kết nối đến Milvus
        try:
            connections.connect(alias="default", host=milvus_host, port=milvus_port)
            if not utility.has_collection(collection_name):
                raise ValueError(f"Collection '{collection_name}' không tồn tại trong Milvus")
            self.collection = Collection(collection_name)
            self.collection.load()
        except Exception as e:
            logger.error(f"Không thể kết nối đến Milvus: {str(e)}")
            raise ConnectionError(f"Không thể kết nối đến Milvus: {str(e)}")
        
        # Khởi tạo model embeddings
        try:
            self.embeddings = OllamaEmbeddings(model="llama3")
        except Exception as e:
            logger.error(f"Không thể khởi tạo OllamaEmbeddings: {str(e)}")
            raise RuntimeError(f"Không thể khởi tạo OllamaEmbeddings: {str(e)}")
        
        logger.info(f"Đã khởi tạo MilvusRetriever với collection '{collection_name}'")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm vector trong Milvus
        
        :param query: Câu truy vấn
        :param top_k: Số lượng kết quả tối đa
        :return: Danh sách kết quả
        """
        try:
            # Tạo embedding từ câu truy vấn
            query_embedding = self.embeddings.embed_query(query)
            
            # Tìm kiếm trong Milvus
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",  # Khớp với schema trong seed_milvus.py
                param=search_params,
                limit=top_k,
                output_fields=["text", "metadata"]
            )
            
            # Định dạng kết quả
            formatted_results = []
            for hits in results:
                for hit in hits:
                    formatted_results.append({
                        "id": hit.id,
                        "score": hit.score,
                        "text": hit.entity.get("text", ""),
                        "metadata": hit.entity.get("metadata", {})
                    })
            
            logger.info(f"Đã tìm thấy {len(formatted_results)} kết quả cho '{query}'")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm vector: {str(e)}")
            raise RuntimeError(f"Lỗi tìm kiếm vector: {str(e)}")
    
    def close(self):
        """
        Đóng kết nối đến Milvus
        """
        try:
            self.collection.release()
            connections.disconnect("default")
            logger.info("Đã đóng kết nối đến Milvus")
        except Exception as e:
            logger.error(f"Lỗi khi đóng kết nối Milvus: {str(e)}")