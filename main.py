import os
import random
import time
import schedule
import re
from datetime import datetime

# Import các module (Giai đoạn 1 đến 4) mà chúng ta đã viết
from modules.db_manager import DBManager
from modules.ai_engine import generate_fb_post, generate_custom_prompt
from modules.media_engine import create_banner
from modules.social_fb import post_to_facebook

# Kho dữ liệu: Danh sách các chủ đề IELTS Speaking
# (Bạn có thể thêm bớt tùy ý hoặc sau này đổi sang đọc từ file Excel/CSV)
IELTS_TOPICS = [
    "Describe a book you have recently read",
    "Describe a famous person you would like to meet",
    "Describe a beautiful place you have visited",
    "Describe a skill that takes a long time to learn",
    "Describe a website you often use",
    "Describe a film you watched recently and liked",
    "Describe a challenging task you completed successfully",
    "Describe an important decision you made in your life",
    "Describe a piece of good news you received",
    "Describe an interesting animal you have seen",
    "Describe a subject you enjoyed studying at school",
    "Describe an interesting conversation you had with a stranger",
    "Describe a goal you want to achieve in the future",
    "Describe a memorable holiday you have had",
    "Describe a time when you helped someone",
    "Describe a favorite piece of clothing you often wear",
    "Describe a natural landscape you found breathtaking",
    "Describe a difficult challenge you overcame"
]

def run_auto_poster_workflow():
    """
    Luồng chạy chính của Tool: Check DB -> Gọi AI -> Tạo Ảnh -> Đăng FB -> Lưu DB
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{current_time}] 🚀 BẮT ĐẦU LUỒNG AUTO POSTER...")
    
    # 1. Kết nối Database
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'autoposter.db')
    db = DBManager(f'sqlite:///{db_path}')
    
    # 2. Chọn chủ đề ngẫu nhiên (chưa đăng trong 6 tháng qua)
    selected_topic = None
    random.shuffle(IELTS_TOPICS) # Trộn ngẫu nhiên danh sách
    
    for topic in IELTS_TOPICS:
        if not db.has_been_posted_recently(topic, months=6):
            selected_topic = topic
            break
            
    if not selected_topic:
        print("⚠️ Tất cả các chủ đề trong danh sách đều đã được đăng gần đây. Cần thêm chủ đề mới vào mảng IELTS_TOPICS!")
        return

    print(f"🎯 Đã chọn chủ đề hôm nay: '{selected_topic}'")
    
    # 3. AI sinh Nội dung bài viết
    print("⏳ Bước 1: Gọi AI viết content...")
    content = generate_fb_post(selected_topic)
    if not content:
        print("❌ Hủy tiến trình do lỗi tạo Content.")
        db.add_post_record(selected_topic, "error")
        return
        
    # 4. Sinh Ảnh Banner
    print("⏳ Bước 2: Tạo Banner hình ảnh...")
    image_path = create_banner(selected_topic)
    
    # 5. Đăng Facebook
    print("⏳ Bước 3: Đẩy bài viết và ảnh lên Facebook...")
    is_success = post_to_facebook(content, image_path)
    
    # 6. Cập nhật lịch sử vào Database
    if is_success:
        db.add_post_record(selected_topic, "success")
        print("🎉 XONG! HOÀN THÀNH LUỒNG ĐĂNG BÀI!")
    else:
        db.add_post_record(selected_topic, "error")
        print("⚠️ Đăng bài thất bại. (Thường do bạn chưa cài đặt đúng Token Fanpage trong file .env)")

def run_multiple_posts(count=10):
    """Chạy liên tục nhiều bài viết"""
    print(f"\n🚀 BẮT ĐẦU LUỒNG ĐĂNG {count} BÀI LIÊN TỤC...")
    for i in range(count):
        print(f"\n{'-'*20} BÀI VIẾT THỨ {i+1}/{count} {'-'*20}")
        run_auto_poster_workflow()
        if i < count - 1:
            delay_seconds = 30
            print(f"⏳ Đợi {delay_seconds} giây trước khi đăng bài tiếp theo để tránh bị Facebook chặn...")
            time.sleep(delay_seconds)
    print(f"\n🎉 ĐÃ HOÀN THÀNH ĐĂNG {count} BÀI LIÊN TỤC!")

def run_mass_generate_to_txt():
    """Tạo nội dung và lưu thành file txt theo thư mục tùy chọn"""
    folder_name = input("\nNhập tên thư mục bạn muốn lưu bài viết (ví dụ: BaiViet_IELTS): ").strip()
    if not folder_name:
        folder_name = "BaiViet_IELTS"
        
    # Tạo thư mục nếu chưa có
    base_dir = os.path.dirname(__file__)
    target_folder = os.path.join(base_dir, folder_name)
    os.makedirs(target_folder, exist_ok=True)
    
    count_str = input("Bạn muốn tạo bao nhiêu bài viết? (Mặc định: 10): ").strip()
    count = int(count_str) if count_str.isdigit() else 10
    
    print(f"\n🚀 BẮT ĐẦU TẠO VÀ LƯU {count} BÀI VIẾT VÀO THƯ MỤC '{folder_name}'...")
    
    db_path = os.path.join(base_dir, 'data', 'autoposter.db')
    db = DBManager(f'sqlite:///{db_path}')
    
    for i in range(count):
        print(f"\n{'-'*20} BÀI VIẾT THỨ {i+1}/{count} {'-'*20}")
        
        selected_topic = None
        random.shuffle(IELTS_TOPICS)
        for topic in IELTS_TOPICS:
            if not db.has_been_posted_recently(topic, months=6):
                selected_topic = topic
                break
                
        if not selected_topic:
            print("⚠️ Hết chủ đề mới trong danh sách IELTS_TOPICS. Vui lòng thêm chủ đề mới vào mảng IELTS_TOPICS.")
            break
            
        print(f"🎯 Đã chọn chủ đề: '{selected_topic}'")
        print("⏳ Đang gọi AI viết content...")
        
        content = generate_fb_post(selected_topic)
        if content:
            # Tạo tên file an toàn
            safe_filename = re.sub(r'[^a-zA-Z0-9 ]', '', selected_topic)
            safe_filename = safe_filename.replace(' ', '_')[:50] + ".txt"
            file_path = os.path.join(target_folder, safe_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Chủ đề: {selected_topic}\n\n")
                f.write(content)
                
            print(f"✅ Đã lưu thành công vào file: {file_path}")
            db.add_post_record(selected_topic, "success")
        else:
            print("❌ Lỗi tạo Content. Bỏ qua bài này.")
            
        if i < count - 1:
            delay_seconds = 10
            print(f"⏳ Đợi {delay_seconds} giây trước khi tạo bài tiếp theo...")
            time.sleep(delay_seconds)
            
    print(f"\n🎉 ĐÃ HOÀN THÀNH LƯU FILE TẠI: {target_folder}")

def run_custom_prompt_workflow():
    print("\n--- TẠO BÀI VIẾT THEO PROMPT TÙY CHỈNH ---")
    user_prompt = input("Nhập Prompt (yêu cầu) của bạn: ").strip()
    if not user_prompt:
        print("Không có prompt. Đang thoát...")
        return
        
    print("\n⏳ Đang gọi AI để tạo bài MẪU đầu tiên cho bạn kiểm tra...")
    sample_content = generate_custom_prompt(user_prompt)
    
    if not sample_content:
        print("❌ Lỗi khi tạo bài mẫu. Vui lòng thử lại sau.")
        return
        
    print("\n" + "="*50)
    print("🎉 KẾT QUẢ BÀI MẪU:")
    print("="*50)
    print(sample_content)
    print("="*50 + "\n")
    
    count_str = input("Bạn có muốn tiếp tục tạo thêm dựa trên prompt này không? Nhập số lượng muốn tạo THÊM (hoặc 0 để thoát): ").strip()
    try:
        count = int(count_str)
    except ValueError:
        count = 0
        
    if count <= 0:
        print("👋 Đã thoát chức năng tạo theo prompt.")
        return
        
    folder_name = input("\nNhập tên thư mục muốn lưu (mặc định: Custom_Posts): ").strip()
    if not folder_name:
        folder_name = "Custom_Posts"
        
    base_dir = os.path.dirname(__file__)
    target_folder = os.path.join(base_dir, folder_name)
    os.makedirs(target_folder, exist_ok=True)
    
    print(f"\n🚀 BẮT ĐẦU TẠO THÊM {count} BÀI VÀ LƯU VÀO '{folder_name}'...")
    
    # Tạo thêm count bài
    for i in range(count):
        print(f"\n{'-'*20} ĐANG TẠO BÀI THỨ {i+1}/{count} {'-'*20}")
        
        delay_seconds = 10
        print(f"⏳ Đợi {delay_seconds} giây trước khi gọi AI để tránh lỗi quá tải...")
        time.sleep(delay_seconds)
        
        print("⏳ Đang gọi AI viết content...")
        content = generate_custom_prompt(user_prompt)
        
        if content:
            # Rút gọn tên file từ prompt và nối thêm timestamp cho khỏi trùng
            safe_filename = re.sub(r'[^a-zA-Z0-9 ]', '', user_prompt[:30])
            safe_filename = safe_filename.replace(' ', '_') + f"_{int(time.time())}.txt"
            file_path = os.path.join(target_folder, safe_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Prompt: {user_prompt}\n\n")
                f.write(content)
                
            print(f"✅ Đã lưu thành công vào: {file_path}")
        else:
            print("❌ Lỗi tạo Content. Bỏ qua bài này.")
            
    print(f"\n🎉 ĐÃ HOÀN THÀNH TẠO VÀ LƯU TẤT CẢ VÀO THƯ MỤC: {target_folder}")

def start_scheduler():
    """Lên lịch chạy ngầm định kỳ"""
    # Bạn có thể đổi giờ ở đây, ví dụ: "20:00" là 8 giờ tối
    run_time = "20:00" 
    print(f"⏰ Chế độ Lên Lịch đã kích hoạt. Tool sẽ TỰ ĐỘNG CHẠY mỗi ngày vào lúc {run_time}.")
    print("Lưu ý: Vui lòng để cửa sổ Terminal này mở (không tắt máy) để tool duy trì hoạt động.")
    
    schedule.every().day.at(run_time).do(run_auto_poster_workflow)
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Cứ 1 phút check đồng hồ 1 lần

if __name__ == "__main__":
    print("="*40)
    print("   🤖 TINO'S IELTS FB AUTO POSTER 🤖   ")
    print("="*40)
    print("1. Chạy Auto Post ngay lập tức (Run Now)")
    print("2. Chạy ngầm theo giờ cấu hình sẵn (Scheduler)")
    print("3. Chạy 10 bài viết liên tục (Mass Poster)")
    print("4. Chỉ tạo nội dung AI và lưu ra file .txt (Không đăng lên FB)")
    print("5. Tạo nội dung theo Prompt tùy chỉnh (Có xem trước)")
    print("="*40)
    
    try:
        choice = input("Nhập phím 1, 2, 3, 4 hoặc 5 rồi bấm Enter: ")
        if choice == '1':
            run_auto_poster_workflow()
        elif choice == '2':
            start_scheduler()
        elif choice == '3':
            run_multiple_posts(10)
        elif choice == '4':
            run_mass_generate_to_txt()
        elif choice == '5':
            run_custom_prompt_workflow()
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chạy lại script.")
    except KeyboardInterrupt:
        print("\n👋 Đã thoát chương trình.")
