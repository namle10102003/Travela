import os
import logging
import sys
from typing import Optional, Tuple, List, Dict, Any
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("semantic_retriever.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SemanticRetriever:
    def __init__(self, rdf_path: Optional[str] = None):
        """
        Khởi tạo trình truy xuất ngữ nghĩa sử dụng RDF
        
        :param rdf_path: Đường dẫn đến file RDF
        """
        self.graph = Graph()
        self.EX = Namespace("http://example.org/du-lich#")
        self.graph.bind("ex", self.EX)
        
        # Nếu có đường dẫn file, load RDF
        if rdf_path:
            rdf_path = os.path.abspath(rdf_path)  # Chuyển sang đường dẫn tuyệt đối
            if os.path.exists(rdf_path):
                try:
                    self.graph.parse(rdf_path, format="xml")
                    self.rdf_loaded = True
                    logger.info(f"Đã tải RDF từ {rdf_path} với {len(self.graph)} triple")
                except Exception as e:
                    self.rdf_loaded = False
                    logger.error(f"Lỗi khi tải RDF: {str(e)}")
            else:
                self.rdf_loaded = False
                logger.warning(f"Không tìm thấy file RDF tại {rdf_path}")
        else:
            self.rdf_loaded = False
            logger.warning("Không cung cấp đường dẫn RDF")
    
    def query_rdf_by_keyword(self, query: str) -> Optional[str]:
        """
        Truy vấn RDF dựa trên từ khóa
        
        :param query: Câu truy vấn chứa từ khóa
        :return: Kết quả dạng text hoặc None nếu không tìm thấy
        """
        if not self.rdf_loaded or len(self.graph) == 0:
            logger.warning("RDF chưa được tải, không thể truy vấn")
            return None
        
        # Lấy từ khóa từ câu truy vấn
        keywords = self._extract_keywords(query.lower())
        logger.info(f"Keywords extracted: {keywords}")
        
        # Tìm kiếm các thực thể liên quan đến từ khóa
        results = self._find_entities_by_keywords(keywords)
        
        if not results:
            logger.info("Không tìm thấy thực thể RDF phù hợp")
            return None
        
        # Định dạng kết quả
        formatted_result = self._format_results(results)
        return formatted_result
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Trích xuất từ khóa quan trọng từ câu truy vấn
        
        :param query: Câu truy vấn
        :return: Danh sách từ khóa
        """
        topic_keywords = {
            "ẩm thực": ["ẩm thực", "món ăn", "đặc sản", "món ăn gì", "ăn uống", "món ngon", 
                      "thức ăn", "quán ăn", "nhà hàng", "bánh", "bún", "phở", "cơm"],
            "địa điểm": ["địa điểm", "thắng cảnh", "điểm đến", "du lịch", "đi đâu", 
                       "tham quan", "khách sạn", "lưu trú", "resort", "homestay", 
                       "biển", "núi", "thác", "hang động"],
            "văn hóa": ["văn hóa", "lễ hội", "phong tục", "truyền thống", "dân tộc", 
                      "lịch sử", "di sản", "nghệ thuật"],
            "tour": ["tour", "tour du lịch", "gói tour", "lịch trình", "hành trình", 
                   "chuyến đi", "tour ghép", "tour riêng"]
        }
        
        words = query.split()
        found_keywords = []
        
        for i in range(len(words)):
            for length in range(1, 4):
                if i + length <= len(words):
                    phrase = " ".join(words[i:i+length])
                    for topic, keywords in topic_keywords.items():
                        if phrase in keywords:
                            found_keywords.append(phrase)
                    
                    locations = ["hà nội", "hồ chí minh", "đà nẵng", "huế", "hội an", 
                                "hạ long", "phú quốc", "đà lạt", "nha trang", "sapa",
                                "hà giang", "ninh bình", "cần thơ", "vũng tàu", "quy nhơn",
                                "phú yên", "lào cai", "sơn la", "buôn ma thuột", "quảng ngãi"]
                    
                    if phrase in locations:
                        found_keywords.append(phrase)
        
        if not found_keywords:
            stop_words = ["là", "và", "của", "có", "không", "những", "các", "được", "cho", "tôi", "bạn"]
            found_keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return found_keywords
    
    def _find_entities_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Tìm thực thể trong RDF dựa trên từ khóa
        
        :param keywords: Danh sách từ khóa
        :return: Danh sách thực thể tìm thấy
        """
        if not keywords:
            return []
        
        results = []
        location = None
        topic = None
        
        locations = ["hà nội", "hồ chí minh", "đà nẵng", "huế", "hội an", "hạ long", 
                     "phú quốc", "đà lạt", "nha trang", "sapa", "hà giang", "ninh bình", 
                     "cần thơ", "vũng tàu", "quy nhơn", "phú yên", "lào cai", "sơn la", 
                     "buôn ma thuột", "quảng ngãi"]
        
        topic_keywords = {
            "ẩm thực": ["ẩm thực", "món ăn", "đặc sản", "ăn gì", "ăn uống", "món ngon", 
                      "thức ăn", "quán ăn", "nhà hàng", "bánh", "bún", "phở", "cơm"],
            "địa điểm": ["địa điểm", "thắng cảnh", "điểm đến", "du lịch", "đi đâu", 
                       "tham quan", "khách sạn", "lưu trú", "resort", "homestay", 
                       "biển", "núi", "thác", "hang động"],
            "văn hóa": ["văn hóa", "lễ hội", "phong tục", "truyền thống", "dân tộc", 
                      "lịch sử", "di sản", "nghệ thuật"],
            "tour": ["tour", "tour du lịch", "gói tour", "lịch trình", "hành trình", 
                   "chuyến đi", "tour ghép", "tour riêng"]
        }
        
        for kw in keywords:
            if kw in locations:
                location = kw.title()
            for t, kws in topic_keywords.items():
                if kw in kws:
                    topic = t
                    break
        
        if not location or not topic:
            logger.info(f"Không xác định được địa điểm ({location}) hoặc chủ đề ({topic})")
            return []
        
        if topic == "ẩm thực":
            query = f"""
            PREFIX ex: <http://example.org/du-lich#>
            SELECT ?food
            WHERE {{
                ?entity ex:ten "{location}"@vi .
                ?entity ex:am_thuc ?food .
            }}
            """
            qres = self.graph.query(query)
            foods = [str(row.food) for row in qres]
            if foods:
                results.append({
                    "uri": f"http://example.org/du-lich#{location.lower().replace(' ', '_')}",
                    "label": location,
                    "description": f"Ẩm thực nổi bật tại {location}",
                    "type": "Location",
                    "properties": {"Ẩm thực": ", ".join(foods)}
                })
        
        elif topic == "địa điểm":
            query = f"""
            PREFIX ex: <http://example.org/du-lich#>
            SELECT ?place
            WHERE {{
                ?entity ex:ten "{location}"@vi .
                ?entity ex:diem_noi_bat ?place .
            }}
            """
            qres = self.graph.query(query)
            places = [str(row.place) for row in qres]
            if places:
                results.append({
                    "uri": f"http://example.org/du-lich#{location.lower().replace(' ', '_')}",
                    "label": location,
                    "description": f"Địa điểm nổi bật tại {location}",
                    "type": "Location",
                    "properties": {"Địa điểm": ", ".join(places)}
                })
        
        elif topic == "tour":
            query = f"""
            PREFIX ex: <http://example.org/du-lich#>
            SELECT ?tour ?tour_name ?desc ?price
            WHERE {{
                ?tour ex:diem_den ?dest .
                ?dest ex:ten "{location}"@vi .
                ?tour ex:ten_tour ?tour_name .
                ?tour ex:mo_ta ?desc .
                ?tour ex:gia ?price .
            }}
            """
            qres = self.graph.query(query)
            for row in qres:
                results.append({
                    "uri": str(row.tour),
                    "label": str(row.tour_name),
                    "description": str(row.desc),
                    "type": "Tour",
                    "properties": {"Giá": str(row.price)}
                })
        
        return results
    
    def _get_predicate_name(self, predicate_uri) -> str:
        """
        Lấy tên ngắn gọn của thuộc tính
        """
        uri_str = str(predicate_uri)
        return uri_str.split('#')[-1] if '#' in uri_str else uri_str.split('/')[-1]
    
    def _get_object_value(self, obj) -> str:
        """
        Lấy giá trị của đối tượng
        """
        if isinstance(obj, URIRef):
            for _, p, o in self.graph.triples((obj, self.EX.ten, None)):
                return str(o)
            uri_str = str(obj)
            return uri_str.split('#')[-1] if '#' in uri_str else uri_str.split('/')[-1]
        return str(obj)
    
    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Định dạng kết quả thành text dễ đọc
        
        :param results: Danh sách thực thể
        :return: Text đã định dạng
        """
        if not results:
            return None
        
        formatted_text = ""
        for entity in results:
            if entity.get('label'):
                formatted_text += f"## {entity['label']}\n\n"
            if entity.get('description'):
                formatted_text += f"{entity['description']}\n\n"
            if entity.get('properties'):
                formatted_text += "### Thông tin chi tiết:\n"
                for prop, value in entity['properties'].items():
                    prop_name = prop.replace('_', ' ').title()
                    formatted_text += f"- **{prop_name}**: {value}\n"
                formatted_text += "\n"
        
        return formatted_text

# === CÁC HÀM TIỆN ÍCH ===

def query_rdf_by_keyword(query: str, rdf_path: str = "data/data.rdf") -> Optional[str]:
    """
    Truy vấn RDF dựa trên từ khóa từ câu hỏi
    
    :param query: Câu truy vấn có chứa từ khóa
    :param rdf_path: Đường dẫn đến file RDF
    :return: Kết quả dạng text hoặc None nếu không tìm thấy
    """
    retriever = SemanticRetriever(rdf_path)
    return retriever.query_rdf_by_keyword(query)