Dự án được thiết kế và triển khai end-to-end, bao gồm phân tích nghiệp vụ, thiết kế database, API, và xử lý logic backend

1. Mục tiêu dự án:
    Đây là backend quản lý học sinh cho trường phổ thông, xử lý nghiệp vụ phức tạp như tổng kết học kỳ, tổng kết cả năm, thi lại, xét lên lớp/lưu ban, phân quyền ba vai trò lớn là
    admin, Teacher, Student; Và đảm bảo tính toàn vẹn dữ liệu

2. Các bài toán backend đã giải quyết:
    - Tổng kết học kỳ chỉ được phép khi tất cả các môn đã được tổng kết
    - Áp dụng đánh giá, xếp loại theo đúng của bộ giáo dục
    - Xử lý các nghiệp vụ theo set-based SQL, tránh loop qua python
    - Xử lý rollback và audit log khi nghiệp vụ lỗi
    - Xử lý chi tiết lịch trùng của giáo viên trong schedule
    - Xử lý cập nhật thông tin giáo viên, môn học triệt để với các phát sinh từ những nghiệp vụ khác có liên quan

3. Kiến trúc hệ thống:
    Route => Service => Repository => Database
        Route: validate, auth
        Service: Business logic
        Repository: SQL & ORM 
        DB: PostgreSQL

4. Công nghệ sử dụng:
    - Backend: Flask REST API
    - ORM: SQLAlchemy
    - Validation: Pydantic
    - Auth: JWT
    - Database: PostgreSQL
    - Background task: Celery + Redis
    - Storage: MinIO
    - Logging: Audit log + Activity log

5. Phân quyền:
    - Admin: Full control
    - Teacher: Nhập điểm, điểm danh, tổng kết, thay đổi thông tin học sinh, chuyển lớp cho cả lớp
    - Student: Xem kết quả học tập của chính mình

6. Nghiệp vụ phức tạp tiêu biểu:
    - Thêm học sinh: xem business_flow.md ## Chức năng thêm học sinh
    - Tổng kết năm học: xem business_flow.md ## Tổng kết Năm học
    - Tổng kết lại học sinh: xem business_flow.md ## Tổng kết kết quả đánh giá lại cho học sinh

7. Test & độ an toàn dữ liệu
    - Mọi nghiệp vụ ghi DB đều chạy trong transaction
    - Tự động rollback khi raise error (logic / validation / DB)
    - Validation đầu vào bằng Pydantic
    - Unique constraint ở DB để chống race-condition
    - Audit log khi thao tác lỗi
    - Activity log khi thao tác thành công

8. Cách chạy
    pip install -r requirements.txt
    uvicorn main:app
