DỰ ÁN QUẢN LÝ TRƯỜNG HỌC

1. Mô tả:
    Một app có all in one mục đích quản lý trường học

2. Kỹ thuật:
    - Tách bạch server giữa frontend (Vue) và backend (Flask)
    - Thiết kế chuẩn RestAPI
    - Đảm bảo clean code và design layer out pattern
    - CORS: cho kết nối giữa frontend và backend
    - JWT: cho Auth
    - Pydantic: kiểm soát input đầu vào
    - Database: sử dụng PostgreSQL, SQLAlchemy, Migrate cho dữ liệu chính
    - Storage: sử dụng MiniO cho cloud và local
    - Redis: sử dụng cho Rate Limited và Celery cho task gởi email tự động
    - Audit log: Theo dõi thao tác người dùng

3. Chức năng:
    a. Bảo mật:
        - User phải có 1 tài khoản để đăng nhập
        - Password luôn luôn được hash bằng werkzeug.security
        - Sau khi đăng nhập sẽ được giữ trạng thái liên tục dù có F5 (Sau mỗi 15 phút sẽ được cấp mới access token)
        - Sau khi thêm 1 tài khoản
            - Đối với giáo viên: sẽ tự động gởi 1 email cho giáo viên có đính kèm URL trong thời hạn 7 giờ để vào trang set password
            - Đối với học sinh: sẽ xuất 1 file excel theo lớp trong đó có username và password, lần đầu đăng nhập sẽ chuyển đến trang set password

    b. Phân quyền:
        - Các cấp độ phân quyền:
            - Admin: Toàn quyền cho mọi thao tác
            - Teacher: Chỉ có quyền trong phạm vi của mình
                - Giáo viên chủ nhiệm: có thể thêm học sinh cho lớp của mình
                - Giáo viên bộ môn: chỉ được thêm điểm cho học sinh của lớp mình 
            - Student: Chỉ được xem thông tin của chính mình

    c. Thêm và quản lý lớp học/môn học/thời khóa biểu/giáo viên/học sinh/thông báo theo năm học
        - Đặc biệt với giáo viên/học sinh có kèm cả info (số điện thoại, email, địa chỉ)
        - Thông báo được gởi đến cho lớp/học sinh có đếm số thông báo và tắt sau khi xem 
        **Giáo viên chủ nhiệm có thể thêm học sinh, thời khóa biểu, thông báo của lớp mình
    
    d. Upload và quản lý file lên cloud
        - Admin: có thể thực hiện được mọi thao tác
        - Giáo viên:
            - Giáo viên chủ nhiệm: có thể upload/download file lên thư mục tổng hợp của lớp
            - Giáo viên bộ môn: chỉ có thể upload/download file lên thư mục môn học của mình ở mỗi lớp
        - Học sinh: chỉ có thể download file ở trong lớp của mình

    e. User/Audit log
        - Admin được truy cập vào danh sách user để tìm thông tin 
        - Admin được truy cập vào check thao tác của tất cả user
        **Có công cụ tìm kiếm và phân trang
    
    f. info
        - Tất cả user đều vào để xem thông tin cá nhân và thay đổi trừ username và role

4. Kiến trúc hệ thống
    Frontend (Vue) <------> Backend (FlasK API)
                            |
                            | ---> Middleware layer
                                    - JWT Auth (validate token, provide new one if any, extract user info)
                                    - CORS (FE - BE communication)
                                    - Rate Limited (Redis)

                            | ---> Route layer
                                    - Receive request from FE
                                    - Call Controller

                            | ---> Controller layer
                                    - Get data from FE
                                    - Call Service -> format Response

                            | ---> Service layer
                                    - Push data input to Pydantic for validate ----> Deny with 422 error if any
                                    - Handle business logic ----> Deny with 400 error if any
                                    - Call repository/ DB layer ---> Rollback and deny with 500 if any
                                    - Call external service if any

                            | ---> Repository/DB layer
                                    - Query DB by SQLAlchemy 
                                    - Validator filter

                            | ---> External Service
                                    - Minio (upload/download/delete)
                                    - celery (task.send email)
                                    
                            | ---> Response
                                    - Controller get result and push to route with JSON for FE

5. Mô tả chức năng:
    ##A. Chức năng Môn học:
        ###a. Tạo môn học:
            # Giới thiệu chức năng:
                Cho phép admin tạo môn học

            # Luồng hoạt động:
                1. Frontend gởi payload với {lesson: 'Toán', grade_id: 1}
                2. Backend 
                    - Tạo record mới trong bảng lesson
                    - Truy vấn danh sách class_room_id thuộc về grade_id
                    - Insert vào bảng phụ class_lesson với class_room_id và lesson_id.
                3. Backend trả về: : {"status": "Success", "msg": "..."}
                4. Frontend hiển thị danh sách môn học + khối lớp và reset form

            # Cấu trúc dữ liệu:
                Các thành phần chính có liên quan trong 3 bảng class_room, lesson, class_lesson
                - class_room:
                    - id: primary key integer
                    - class_room: string (VD: 10A, 10B) - tên lớp
                    - grade_id: foreign key integer (VD: 1,2) - link với bảng grade
                - lesson:
                    - id: primary key integer
                    - lesson: string (VD: 'Toán', 'Lý') - Tên môn học cũng là tên folder cho cloud
                    - grade_id: foreign key integer (VD: 1, 2) - link với bảng grade
                - class_lesson:
                    - id: primary key integer
                    - class_room_id: foreign key integer (VD: 1, 2) - link với bảng class_room
                    - lesson_id: foreign key integer (VD: 1, 2) - link với bảng lesson   

                # Mối liên kết giữa bảng:
                    grade.id  → class_room.grade_id
                    grade.id  → lesson.grade_id
                    class_room.id → class_lesson.class_room_id
                    lesson.id → class_lesson.lesson_id

            # API endpoint:
                Endpoint name: 
                    Create lesson
                Method & URL:
                    POST /api/academic/lessons
                Role:
                    admin
                Body:
                    payload = {lesson: 'Toán', grade_id: 1} 
                Response:    
                    {'status': 'Success', 'msg': 'Thêm môn học thành công!'} 201
                    
            # Validation rules:
                input validation (Pydantic):
                    - lesson: không None, không chứa số / ký tự đặc biệt
                    - grade_id: integer, không None
                Business validation (Logic):
                    - lesson: không được trùng tên
                Các lỗi thường gặp nếu vi phạm:
                    - Pydantic: 
                        {'status': 'Validation_error', 'msg': 'Môn học không được chứa số và ký tự đặc biệt!'} 422
                        {'status': 'Validation_error', 'msg': 'Chưa nhập khối lớp!'} 422
                    - Logic:
                        {'status': 'Logic_error', 'msg': 'Môn học đã có!'} 400

        ###b. Cập nhập môn học:
            # Giới thiệu chức năng:
                cho phép admin cập nhật thay đổi tên môn học và khối lớp
            # Luồng hoạt động và Cấu trúc dữ liệu: tương tự như ở tạo môn học
            # API endpoint:
                gọi với PUT /api/academic/lessons với payload = {lesson_id: 1, lesson: 'Toán', grade_id: 3} dược response {'status': 'Success', 'msg': 'Cập nhật môn học thành công!'} 200
            # Validation rules: 
                Cũng tương tự tạo môn học nhưng có bổ sung thêm lesson_id
                Check input với Pydantic:
                    - lesson_id chỉ được chứa số và not None
                Check logic:
                    - Check lesson_id có tồn tại không


