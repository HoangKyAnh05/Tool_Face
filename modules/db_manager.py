import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Định nghĩa Base model
Base = declarative_base()

class PostHistory(Base):
    __tablename__ = 'post_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String, nullable=False, index=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False) # Trạng thái: 'success' hoặc 'error'

class DBManager:
    def __init__(self, db_path='sqlite:///data/autoposter.db'):
        """Khởi tạo kết nối CSDL."""
        # Đảm bảo thư mục lưu trữ SQLite tồn tại
        if db_path.startswith('sqlite:///'):
            dir_path = os.path.dirname(db_path.replace('sqlite:///', ''))
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
                
        # Tạo engine và khởi tạo bảng nếu chưa có
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_post_record(self, topic_name, status):
        """Thêm một bản ghi lịch sử bài đăng vào CSDL."""
        session = self.Session()
        try:
            new_record = PostHistory(
                topic_name=topic_name,
                status=status,
                published_at=datetime.utcnow()
            )
            session.add(new_record)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"[DB Error] Không thể lưu bản ghi: {e}")
            return False
        finally:
            session.close()

    def has_been_posted_recently(self, topic_name, months=6):
        """Kiểm tra xem một chủ đề đã được đăng thành công trong X tháng qua chưa."""
        session = self.Session()
        try:
            # Tính thời điểm 'X tháng trước' (1 tháng ~ 30 ngày)
            time_threshold = datetime.utcnow() - timedelta(days=30 * months)
            
            # Truy vấn các bài đăng có cùng tên, thành công, và sau thời điểm tính toán
            record = session.query(PostHistory).filter(
                PostHistory.topic_name == topic_name,
                PostHistory.status == 'success',
                PostHistory.published_at >= time_threshold
            ).first()
            
            return record is not None
        except Exception as e:
            print(f"[DB Error] Lỗi truy vấn: {e}")
            return False
        finally:
            session.close()

# Đoạn code dùng để test nhanh khi chạy file trực tiếp
if __name__ == '__main__':
    print("🚀 Khởi tạo Database Manager...")
    db = DBManager('sqlite:///../data/test_autoposter.db')
    
    test_topic = "IELTS Speaking Part 2: Describe a book"
    
    print(f"\nKiểm tra xem '{test_topic}' có vừa được đăng gần đây không:")
    print("Kết quả:", db.has_been_posted_recently(test_topic))
    
    print(f"\nTiến hành lưu lịch sử đăng bài thành công cho '{test_topic}'...")
    db.add_post_record(test_topic, "success")
    
    print("\nKiểm tra lại lần nữa:")
    print("Kết quả:", db.has_been_posted_recently(test_topic))
