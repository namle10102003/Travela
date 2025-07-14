import logging
import sys
from typing import List, Dict, Any, Optional
import numpy as np

from semantic_retriever import SemanticRetriever
from milvus_retriever import MilvusRetriever
from langchain_ollama import OllamaEmbeddings

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hybrid_retriever.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HybridRetriever:
    def __init__(self, 
                 collection_name: str, 
                 rdf_path: Optional[str] = None,
                 milvus_host: str = 'localhost',
                 milvus_port: str = '19530'):
        """
        Khởi tạo trình truy xuất kết hợp sử dụng RDF và Milvus
        
        :param collection_name: Tên collection trong Milvus
        :param rdf_path: Đường dẫn đến file RDF
        :param milvus_host: Host của Milvus server
        :param milvus_port: Port của Milvus server
        """
        # Khởi tạo trình truy xuất RDF
        self.semantic_retriever = SemanticRetriever(rdf_path)
        
        # Khởi tạo trình truy xuất vector Milvus
        try:
            self.vector_retriever = MilvusRetriever(
                collection_name=collection_name,
                milvus_host=milvus_host,
                milvus_port=milvus_port
            )
        except Exception as e:
            logger.error(f"Không thể khởi tạo MilvusRetriever: {str(e)}")
            raise
        
        logger.info(f"Đã khởi tạo HybridRetriever với collection '{collection_name}' và RDF '{rdf_path}'")
    
    def hybrid_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Thực hiện tìm kiếm kết hợp giữa RDF và vector search
        
        :param query: Câu truy vấn
        :param top_k: Số lượng kết quả tối đa
        :return: Từ điển chứa kết quả từ RDF và vector search
        """
        # Truy vấn RDF
        semantic_results = self._semantic_query(query)
        
        # Truy vấn vector search
        vector_results = self._vector_query(query, top_k)
        
        # Kết hợp và xếp hạng kết quả
        combined_results = self._combine_results(semantic_results, vector_results, query)
        
        return {
            'semantic_results': semantic_results,
            'vector_results': vector_results,
            'combined_results': combined_results
        }
    
    def _semantic_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Truy vấn thông tin từ RDF
        
        :param query: Câu truy vấn
        :return: Danh sách kết quả từ RDF
        """
        try:
            rdf_text = self.semantic_retriever.query_rdf_by_keyword(query)
            if rdf_text:
                return [{
                    'type': 'semantic',
                    'text': rdf_text,
                    'score': 1.0
                }]
            return []
        except Exception as e:
            logger.error(f"Lỗi truy vấn RDF: {str(e)}")
            return []
    
    def _vector_query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm vector gần đúng
        
        :param query: Câu truy vấn
        :param top_k: Số lượng kết quả tối đa
        :return: Danh sách kết quả từ vector search
        """
        try:
            results = self.vector_retriever.search(query, top_k)
            return [{
                'type': 'vector',
                'text': result['text'],
                'score': result['score']
            } for result in results]
        except Exception as e:
            logger.error(f"Lỗi truy vấn vector: {str(e)}")
            return []
    
    def _combine_results(
        self, 
        semantic_results: List[Dict[str, Any]], 
        vector_results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Kết hợp và xếp hạng kết quả từ RDF và vector search
        
        :param semantic_results: Kết quả từ RDF
        :param vector_results: Kết quả từ vector search
        :param query: Câu truy vấn gốc
        :return: Danh sách kết quả đã được kết hợp và xếp hạng
        """
        combined = semantic_results.copy()
        seen_texts = set(result['text'] for result in semantic_results)
        
        for vec_result in vector_results:
            if vec_result['text'] not in seen_texts:
                combined.append(vec_result)
                seen_texts.add(vec_result['text'])
        
        combined.sort(
            key=lambda x: (
                1 if x['type'] == 'semantic' else 0,
                x['score']
            ), 
            reverse=True
        )
        
        return combined[:5]

# Hàm tiện ích để tạo trình truy xuất kết hợp
def get_hybrid_retriever(
    collection_name: str, 
    rdf_path: Optional[str] = None,
    milvus_host: str = 'localhost',
    milvus_port: str = '19530'
) -> HybridRetriever:
    """
    Tạo và trả về trình truy xuất kết hợp
    
    :param collection_name: Tên collection trong Milvus
    :param rdf_path: Đường dẫn đến file RDF
    :param milvus_host: Host của Milvus server
    :param milvus_port: Port của Milvus server
    :return: Đối tượng HybridRetriever
    """
    return HybridRetriever(
        collection_name=collection_name,
        rdf_path=rdf_path,
        milvus_host=milvus_host,
        milvus_port=milvus_port
    )