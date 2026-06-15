import os
import requests
from dotenv import load_dotenv

load_dotenv()

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

def post_to_facebook(message, image_path=None):
    """
    Đăng bài lên Facebook Fanpage thông qua API Graph v19.0.
    """
    if not PAGE_ID or not ACCESS_TOKEN or PAGE_ID.startswith("your_"):
        print("❌ Lỗi: Chưa cấu hình FACEBOOK_PAGE_ID hoặc FACEBOOK_ACCESS_TOKEN trong file .env")
        return False
        
    print("🌐 Đang đẩy bài viết và ảnh lên Facebook Fanpage...")
    
    try:
        if image_path and os.path.exists(image_path):
            # Nếu có ảnh -> Sử dụng Endpoint Upload Photos
            url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
            payload = {
                'caption': message,
                'access_token': ACCESS_TOKEN
            }
            with open(image_path, 'rb') as img:
                files = {'source': img}
                response = requests.post(url, data=payload, files=files)
        else:
            # Nếu không có ảnh -> Chỉ đăng Text
            url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
            payload = {
                'message': message,
                'access_token': ACCESS_TOKEN
            }
            response = requests.post(url, data=payload)
            
        result = response.json()
        
        if response.status_code == 200:
            post_id = result.get("post_id") or result.get("id")
            print(f"✅ ĐĂNG BÀI THÀNH CÔNG! Post ID: {post_id}")
            return True
        else:
            print(f"❌ [FB API Error] Facebook từ chối đăng bài (Lỗi {response.status_code})")
            print(f"Chi tiết: {result.get('error', {}).get('message', result)}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi mạng khi kết nối với máy chủ Facebook: {e}")
        return False

if __name__ == "__main__":
    print("Khởi tạo Facebook Publisher Test...")
    # Cần điền đúng Token và Page ID vào .env thì code test này mới chạy được.
    test_message = "Xin chào! Đây là bài test từ hệ thống Auto Poster bằng Python 🤖"
    
    base_dir = os.path.dirname(__file__)
    test_image = os.path.join(base_dir, '..', 'data', 'output_banner.jpg')
    
    post_to_facebook(test_message, test_image)
