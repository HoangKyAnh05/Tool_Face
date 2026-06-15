import os
import requests
import json
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Tải API key dùng chung từ file shared_config.json ở thư mục cha nếu có
try:
    shared_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "shared_config.json"))
    if os.path.exists(shared_config_path):
        with open(shared_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            shared_key = config.get("geminiApiKey")
            if shared_key:
                GEMINI_API_KEY = shared_key
except Exception as e:
    pass

def get_best_model(api_key):
    """
    Tự động gọi API của Google để lấy danh sách các model mới nhất.
    Tìm model nào chứa chữ 'flash' (chạy nhanh, rẻ) và có hỗ trợ sinh nội dung.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            # Ưu tiên tìm model dòng Flash (ví dụ gemini-2.5-flash)
            for m in models:
                name = m.get('name', '')
                methods = m.get('supportedGenerationMethods', [])
                if 'flash' in name.lower() and 'generateContent' in methods:
                    return name
            # Nếu không tìm thấy Flash, lấy đại model đầu tiên hỗ trợ
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    return m.get('name')
    except Exception as e:
        pass
    return "models/gemini-2.5-flash" # Giá trị dự phòng

def generate_fb_post(topic):
    """
    Gửi HTTP Request trực tiếp lên API của Google Gemini để sinh bài đăng,
    cách này giúp tránh được toàn bộ lỗi của thư viện SDK cũ.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("your_"):
        print("❌ Lỗi: Không tìm thấy API Key hợp lệ trong file .env.")
        return None

    # Tìm model tự động
    model_name = get_best_model(GEMINI_API_KEY)
    print(f"🤖 Đang sử dụng phiên bản AI: {model_name.replace('models/', '')}")

    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    # Thiết kế Câu lệnh (Prompt) chuẩn chỉnh dành riêng cho IELTS Facebook Fanpage
    prompt = f"""
    Bạn là một chuyên gia dạy IELTS 8.5 và là một người quản lý Fanpage Facebook xuất sắc.
    Hãy viết một bài đăng Facebook (sử dụng tiếng Việt, kết hợp tiếng Anh) về chủ đề IELTS Speaking Part 2 sau đây: "{topic}".
    
    Yêu cầu cấu trúc bài đăng chặt chẽ như sau:
    1. Tiêu đề giật tít, thu hút sự chú ý (sử dụng chữ IN HOA cho các từ khóa quan trọng) kèm emoji phù hợp.
    2. Một bài trả lời mẫu (Sample Answer) hoàn chỉnh bằng tiếng Anh, đạt Band 8.0+. Bài mẫu nên chia thành các đoạn văn ngắn gọn (2-3 câu/đoạn) để dễ đọc trên điện thoại.
    3. Trích xuất đúng 5 từ vựng hoặc cụm từ vựng (Idioms/Collocations) "đắt giá" nhất từ bài mẫu trên. Giải thích nghĩa tiếng Việt và cách dùng.
    4. Lời kêu gọi hành động (Call To Action - CTA) ở cuối bài để khuyến khích mọi người bình luận hoặc chia sẻ bài viết.
    5. Cung cấp sẵn các hashtag liên quan như #IELTS #IELTSSpeaking #TuVungIELTS.
    
    Lưu ý cực kỳ quan trọng: TUYỆT ĐỐI KHÔNG in ra các câu hội thoại thừa như "Dưới đây là bài viết của bạn...". Hãy in ra duy nhất nội dung bài đăng để tôi có thể copy-paste trực tiếp lên Facebook luôn.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        # Gọi trực tiếp qua API (requests)
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            print(f"❌ [API Error] Máy chủ Google từ chối với mã lỗi: {response.status_code}")
            print(f"Chi tiết: {response.json()}")
            return None
            
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        print(f"❌ [AI Error] Có lỗi xảy ra trong lúc kết nối: {e}")
        return None

def generate_custom_prompt(prompt_text):
    """
    Gửi prompt tùy chỉnh trực tiếp lên Google Gemini.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("your_"):
        print("❌ Lỗi: Không tìm thấy API Key hợp lệ trong file .env.")
        return None

    model_name = get_best_model(GEMINI_API_KEY)
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    try:
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            print(f"❌ [API Error] Máy chủ Google từ chối với mã lỗi: {response.status_code}")
            print(f"Chi tiết: {response.json()}")
            return None
            
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        print(f"❌ [AI Error] Có lỗi xảy ra trong lúc kết nối: {e}")
        return None

# Đoạn code dùng để chạy test nhanh
if __name__ == '__main__':
    print("⏳ Đang kết nối trực tiếp với máy chủ Google AI...")
    
    test_topic = "Describe a famous person you would like to meet"
    post_content = generate_fb_post(test_topic)
    
    if post_content:
        print("\n" + "="*60)
        print("🎉 KẾT QUẢ: BÀI ĐĂNG FACEBOOK HOÀN CHỈNH")
        print("="*60 + "\n")
        print(post_content)
        print("\n" + "="*60)
    else:
        print("\n❌ Thử nghiệm thất bại. Hãy kiểm tra lại API Key ở trên.")
