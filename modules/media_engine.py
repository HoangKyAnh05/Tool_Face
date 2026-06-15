import os
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

def download_font(font_path):
    """Tải font chữ Roboto Black miễn phí từ Google Fonts nếu chưa có"""
    if not os.path.exists(font_path):
        print("⬇️ Đang tải Font chữ...")
        # Link tải trực tiếp file TTF từ kho Google
        url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf"
        r = requests.get(url, allow_redirects=True)
        with open(font_path, 'wb') as f:
            f.write(r.content)

def download_background(bg_path):
    """Tải một hình nền ngẫu nhiên từ thư viện Picsum (có làm mờ)"""
    print("⬇️ Đang tải Hình nền ngẫu nhiên...")
    # Tải ảnh kích thước chuẩn Facebook 1200x630, blur=3 để làm mờ phông nền
    url = "https://picsum.photos/1200/630?blur=3"
    r = requests.get(url, allow_redirects=True)
    with open(bg_path, 'wb') as f:
        f.write(r.content)

def create_banner(topic_text):
    """
    Chèn Tên Chủ Đề vào giữa một bức ảnh để đăng Facebook.
    """
    # 1. Chuẩn bị thư mục (assets chứa font, data chứa ảnh tạm)
    base_dir = os.path.dirname(__file__)
    assets_dir = os.path.join(base_dir, '..', 'assets')
    temp_dir = os.path.join(base_dir, '..', 'data')
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    font_path = os.path.join(assets_dir, 'Roboto-Black.ttf')
    bg_path = os.path.join(temp_dir, 'bg_temp.jpg') # Tải nền mới mỗi lần chạy
    output_path = os.path.join(temp_dir, 'output_banner.jpg')
    
    # 2. Tải Font và Ảnh nền
    download_font(font_path)
    download_background(bg_path)
    
    # 3. Mở ảnh và làm tối (Darken) để chữ trắng dễ đọc hơn
    img = Image.open(bg_path).convert("RGBA")
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 120)) # Phủ lớp đen mờ 50%
    img = Image.alpha_composite(img, overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    
    # 4. Cấu hình chữ
    try:
        font = ImageFont.truetype(font_path, 60)
    except IOError:
        font = ImageFont.load_default()
        
    # Tiền xử lý chữ: Thêm tiêu đề phụ và ngắt dòng (Wrap text) nếu chữ quá dài
    full_text = "IELTS SPEAKING PART 2:\n\n" + topic_text.upper()
    wrapped_text = "\n".join(textwrap.wrap(full_text, width=32))
    
    # Tính toán tọa độ để chữ nằm chính giữa ảnh
    try:
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align='center')
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        # Dự phòng cho Pillow bản cũ
        text_w, text_h = draw.multiline_textsize(wrapped_text, font=font)
        
    x = (img.width - text_w) / 2
    y = (img.height - text_h) / 2
    
    # 5. Vẽ chữ (Stroke width = viền đen bao quanh chữ để chữ nổi bật 3D)
    draw.multiline_text(
        (x, y), 
        wrapped_text, 
        font=font, 
        fill="white", 
        align="center",
        stroke_width=3,
        stroke_fill="black"
    )
    
    # 6. Lưu file
    img.save(output_path, "JPEG", quality=95)
    print(f"✅ Đã tạo Banner thành công: {output_path}")
    return output_path

if __name__ == '__main__':
    print("🎨 Đang khởi tạo Media Engine...")
    test_topic = "Describe a book you have recently read"
    create_banner(test_topic)
