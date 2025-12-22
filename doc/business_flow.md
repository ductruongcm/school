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
        - User phải có 1 tài khoản được tạo bởi quản trị viên
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
                                    - CORS (FE - BE communication)
                                    - JWT Auth (validate token, provide new one if any, extract user info)
                                    - Rate Limited (Redis)
                                    - Record log optional with bad input

                            | ---> Route layer
                                    - Receive request from FE
                                    - Check role
                                    - Push data input to Pydantic for validate ----> Deny with 422 error if any
                                    - Record log optional with raised error by flask error handler if any
                                    - Call Service

                            | ---> Service layer
                                    - Handle business logic ----> Raise ValuerError with code 400, 404 error if any
                                    - Call repository/ DB layer ---> Raise ValuerError and Rollback with code 500 error if any
                                    - Call external service if any
                                    - Record log optional with success result if any

                            | ---> Repository/DB layer
                                    - Query DB by SQLAlchemy 
                                    - Validator filter

                            | ---> External Service
                                    - Minio (upload/download/delete)
                                    - celery (task.send email)
                                    
                            | ---> Response
                                    - Route get result and format response to push to FE

5. Mô tả chức năng:
    ## Chức năng Môn học:
        ### Tạo môn học:
            #### Giới thiệu chức năng:
                Cho phép admin tạo môn học và đăng ký môn học vào danh sách hiển thị tương đương từng khu vực

            #### Luồng hoạt động:
                1. Frontend gởi payload với {lesson: 'Toán', grade: 9, is_visible: true, is_folder: true, is_schedule: true}
                2. Backend 
                    - Check authorization và role (admin)
                    - Check tên lesson tránh trùng
                    - check grade có tồn tại không?
                    - Tạo record mới trong bảng lesson với cái fields: lesson, grade
                    - Tạo record mới trong bảng lessontag với các fields: is_visible, is_folder, is_schedule
                3. Backend trả về: : {"data": lesson}
                4. Frontend hiển thị danh sách môn học + khối lớp + is_visible + is_folder + is_schedule và reset form

            #### Cấu trúc dữ liệu:
                Các thành phần chính có liên quan trong 3 bảng lesson, lessontag
                - lesson:
                    - id: primary key integer
                    - lesson: string (VD: 'Toán', 'Lý') - Tên môn học bao gồm cả thư mục cho cloud và tiết học cho thời khóa biểu
                    - grade: foreign key integer (VD: 1, 2) - link với bảng grade
                - lessontag:
                    - id: primary key integer
                    - lesson_id: foreign key integer (VD: 1, 2) - link với lesson
                    - is_visible: Boolean (True/False) - Để thể hiện môn học chính có giáo viên cụ thể và điểm số
                    - is_folder: Boolean (True/False) - Để thể hiện là thư mục cho danh sách cloud
                    - is_schedule: Boolean (True/False) - Để thể hiện là tiết học để add cho thời khóa biểu

                # Mối liên kết giữa bảng:
                    grade  → lesson.grade
                    lesson.id → teach_class.lesson_id
                    lesson.id → lessontag.lesson_id

            #### API endpoint:
                Endpoint name: 
                    Create lesson
                Method & URL:
                    POST /api/academic/lessons
                Role:
                    admin
                Body:
                    payload = {lesson: 'Toán', grade: 9, is_visible: true, is_folder: true, is_schedule: true}
                Response:    
                    {'msg': 'Đã thêm môn học Toán!'} 201
                    
            #### Validation rules:
                input validation (Pydantic):
                    Lesson(YearID, GradeID)
                        lesson: str (không chứa số / ký tự đặc biệt)
                        is_visible: Optional[bool] | None
                        is_folder: Optional[bool] | None
                        is_schedule: Optional[bool] | None

                Business validation (Logic):
                    - lesson: không được trùng tên
                    - Check grade có tồn tại không

                Các lỗi thường gặp nếu vi phạm:
                    - Pydantic: 
                        {'status': 'Validation_error', 'msg': 'Môn học không được chứa số và ký tự đặc biệt!'} 422
                        {'status': 'Validation_error', 'msg': 'Chưa nhập khối lớp!'} 422
                    - Logic:
                        {'status': 'Logic_error', 'msg': 'Môn học đã có!'} 409
                    *** Tất cả các lỗi raise sẽ kèm rollback db 

        ### Cập nhập môn học:
            #### Giới thiệu chức năng:
                cho phép admin cập nhật thay đổi tên môn học, khối lớp và lessontag
            #### Luồng hoạt động và Cấu trúc dữ liệu: 
                1. Frontend gởi payload với list các môn học đã được sàng lọc nếu có thay đổi bất kỳ ngoài lesson_id
                                           {lesson: 'Toán',
                                            lesson_id: 43, 
                                            grade: 9, 
                                            year_id: 10, 
                                            is_visible: true, 
                                            is_folder: true, 
                                            is_schedule: true}
                    - Loop qua từng môn để thực hiện update
                    - kiểm tra lesson_id: nếu không có sẽ raise 404 {'msg': 'Không tìm thấy ID môn học!'}
                    - kiểm tra year_id: nếu không có sẽ raise 404 {'msg': 'Chưa thiết lập niên khóa!'}
                    
                    - Nếu đổi tag: 
                        - is_folder: sẽ chuyển True/Fasle ở cột is_folder của bảng lessontag
                        - is_schedule: sẽ chuyển True/Fasle ở cột is_schedule của bảng lessontag
                        - is_visible: sẽ chuyển True/Fasle ở cột is_schedule của bảng lessontag và thay đổi liên kết đến bảng teach_class nếu đã có

                    Các phướng án:
                    - Nếu chỉ đổi is_visible:
                        - is_visible to True: 
                            - đổi is_visible thành True trong lessontag
                            - add class_room_id tương ứng với grade và lesson_id, year_id trong teach_class
                        - is_visible to False: 
                            - đổi is_visible thành False trong lessontag
                            - Xóa tất cả các row có year_id và lesson_id tương ứng trong teach_class

                    - Nếu đổi grade:
                        - check grade: nếu id ko hợp lệ sẽ raise 400 {'msg': 'Không tìm thấy grade ID!'}
                        - Nếu chỉ đổi grade:
                                - is_visible là False: chỉ đổi grade trong lesson
                                - is_visible là True: 
                                    - đổi grade trong lesson
                                    - xóa tất cả cả row có year_id và lesson_id tương ứng và sau đó add lại đúng với class_room_id từ grade và lesson_id, year_id trong teach_class

                        - Đổi grade và is_visible:
                                - is_visible từ False sang True: 
                                    - đổi grade trong lesson
                                    - đổi is_visible thành True trong lessontag
                                    - add class_room_id tương ứng với grade và lesson_id, year_id trong teach_class
                                - is_visible từ True sang False:
                                    - đổi grade trong lesson
                                    - đổi is_visible thành False trong lessontag
                                    - xóa tất cả các row có year_id và lesson_id tương ứng trong teach_class
                        
            #### API endpoint:
                gọi với PUT /api/academic/lessons với payload = {lesson_id: 1, lesson: 'Toán', year_id: 1, grade: 9, 'is_folder': true, 'is_schedule': true, 'is_visible': true} 
                được response {'msg': 'Đã cập nhật môn học Toán!'} 200

            #### Validation rules: 
                Cũng tương tự tạo môn học nhưng có bổ sung thêm lesson_id
                input validation (Pydantic):
                    LessonUpdate(Lesson)
                        grade: int

                Check logic:
                    - lesson: không được trùng tên
                    - Check lesson_id có tồn tại không
                    - Check year_id có tồn tại không
                    - Check grade có tồn tại không
                    *** Tất cả các lỗi raise sẽ kèm rollback db 

    ## Chức năng giáo viên
        ### Thêm giáo viên
            #### Giới thiệu chức năng: 
                Cho phép admin tạo 1 giáo viên (bao gồm thông tin cơ bản, login, môn học, lớp giảng dạy và lớp chủ nhiệm)
            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'name': 'Nguyễn Văn Tý',
                     'tel': 0909123445,
                     'add': 'Cần Thơ',
                     'username': 'ty_nguyen',
                     'email': 'ty_nguyen@example.com',
                     'class_room': '10B',
                     'class_room_id': 2,
                     'lesson_id': 5,
                     'teach_class': [1, 2],
                     'year_id': 1
                    }
                    (ở đây field class_room, class_room_id, teach_class có thể None) 
                B2: Backend:
                    - Check authorization và role (chỉ quyền admin)
                    - route tiếp nhận và validate input bằng pydantic
                    - Business Logic Check:
                    - Tạo 1 hashed_password và 1 hashed_temp_token
                    - record vào db:
                        - trong bảng users với {'username': username, 'password': hashed_password, 'role': 'Teacher'}
                        - trong bảng tmp_token với {'user_id': users.id, 'token' = hashed_tmp_token}
                        - trong bảng teacher với {'name': name, 'lesson_id': lesson_id, 'user_id': users.id}
                        - trong bảng teacher_info với {'teacher_id': teacher.id, 'tel': tel, 'add': add, 'email': email}
                    - trong trường hợp là giáo viên chủ nhiệm, sau khi check không lỗi sẽ insert teacher.id vào class_room.teacher_id
                    - với teach_class: sau khi check không lỗi, sẽ lấy mỗi teach_class với lesson_id, year_id để query, từ đó sẽ insert teacher.id vào mỗi teach_class.teacher_id tương ứng
                    - Sau khi hoàn tất commit db, thì sẽ gởi 1 email đến mail của giáo viên có chứa link trong thời hạn là 7 giờ để vào set new password
                    - Backend sẽ trả về với nội dung {'msg': 'Đã thêm giáo viên Nguyễn Văn Tý'}, 201
                    - Activity_log sau khi thao tác gọi API
                B3: FE sẽ hiện thị thông tin với nội dung: Đã thêm giáo viên Nguyễn Văn Tý

                Email gửi cho giáo viên:
                    Xin chào Nguyễn Văn Tý,

                    Tài khoản của bạn đã được tạo tại hệ thống trường BVD.

                    Vui lòng nhấn vào liên kết sau để đặt mật khẩu (hiệu lực trong 7 giờ):
                    http://localhost:5173/setpassword?token=scrypt:32768:8:1$KyWVaZbSLp3HanVQ$847f0e7184c580c8fb6959d90d142d4262a0ec50e72a779447240d8cfff0ae34af56b7a413041a33acde0b7c93edceaf85dd766ec98bd8e8a96cd28de1cc8b64

                    Trân trọng,
                    Phòng quản trị hệ thống
                    (Đây là email tự động, vui lòng không trả lời.)

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 3 bảng users, teachers, teacher_info, class_room, lesson, teach_class, year
                - teachers:
                    - id: primary key integer
                    - name: string (vd: Nguyễn Văn Tý)
                    - lesson_id: foreign key integer - link với lesson
                    - user_id: foreign key integer - link với users

                - teacher_info:
                    - teacher_id: foreign key integer - link với teachers
                    - email: str
                    - tel: str
                    - add: str

                - users:
                    - id: primary key integer
                    - username: str
                    - password: str
                    - role: str ('Teacher')
                    - changed_password: bool 

                - class_room:
                    - teacher_id: foreign key integer - link với teachers
                
                - lesson:
                    - id: primary key integer

                - year:
                    - id: primary key integer

                - teach_class:
                    - teacher_id: foreign key integer - link với teachers
                    - lesson_id: foreign key integer - link với lesson
                    - class_room_id: foreign key integer - link với class_room_id
                    - year_id: foreign key integer - link với year
                    *** ràng buộc unique với class_room_id, lesson_id và year_id:   __table_args__ = (UniqueConstraint('class_room_id', 'lesson_id', 'year_id', name = 'uq_cls_les_year'),)
            
            #### API endpoint:
                Endpoint name: 
                    Create teacher
                Method & URL:
                    POST /api/teachers
                Role:
                    admin
                Body:
                    {'name': 'Nguyễn Văn Tý',
                     'tel': 0909123445,
                     'add': 'Cần Thơ',
                     'username': 'ty_nguyen',
                     'email': 'ty_nguyen@example.com',
                     'class_room': '10B',
                     'class_room_id': 2,
                     'lesson_id': 5,
                     'teach_class': [1, 2],
                     'year_id': 1
                    }
                Response:    
                    {'msg': Đã thêm giáo viên Nguyễn Văn Tý} 201

            #### Validation rule
                Input validation (Pydantic):
                    UserSchemas.User(BaseModel):
                        name: str ko được chứa ký tự đặc biệt và số
                        add: str ko được chứa ký tự đặc biệt
                    TeacherCreateSchema(UserSchemas.User):
                        tel: str chỉ được chứa 10 số
                        username: str chỉ được chữ thường, số và _
                        email: EmailStr
                        class_room: Optional[str] | None 
                        class_room_id: Optional[int] | None
                        lesson_id: int
                        year_id: int
                        teach_class: Optional[list]

                Business validation:
                        - check dup username
                        - year_id có tồn tại không?
                        - lesson_id có hợp lệ không?
                        - class_room_id có hợp lệ không?
                        - home_class đã có giáo viên chủ nhiệm chưa?
                        - teach_class có bị trùng với giáo viên khác không?
                
                Các lỗi thường gặp nếu vi phạm:
                        - pydantic:
                            {'status': 'Validation_error', 'msg': 'Chưa chọn môn học!'} 422
                            {'status': 'Validation_error', 'msg': 'Họ và tên không được chứa số và ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Số điện thoại chỉ được chứa 10 chữ số'} 422
                            {'status': 'Validation_error', 'msg': 'Địa chỉ không được chứa ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Username không hợp lệ'} 422
                             
                        - Business logic:
                            {'status': 'Logic_error', 'msg': 'Lớp học đã có giáo viên bộ môn này!'} 400
                            {'status': 'Logic_error', 'msg': 'Username đã được sử dụng!'} 409
                            {'status': 'Logic_error', 'msg': 'Lớp 10A đã có giáo viên chủ nhiệm!'} 400
                            *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log
                            
        ### Cập nhập Giáo viên:
            #### Giới thiệu chức năng
                Cho phép admin cập nhật thông tin 1 giáo viên (bao gồm thông tin cơ bản, login, môn học, lớp giảng dạy và lớp chủ nhiệm)
            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'name': 'Nguyễn Văn Tý',
                     'tel': 0909123445,
                     'add': 'Cần Thơ',
                     'email': 'ty_nguyen@example.com',
                     'class_room': '10B',
                     'class_room_id': 2,
                     'lesson_id': 5,
                     'teach_class': [1, 2],
                     'year_id': 1,
                     'semester_id': 2
                    }
                    (ở đây field class_room, class_room_id, teach_class có thể None) 
                B2: Backend:
                    - Check authorization và role (chỉ quyền admin)
                    - route tiếp nhận và validate input bằng pydantic
                    - Business Logic Check
                    - update vào db theo teacher_id:
                        - trong bảng teacher với {'name': name, 'lesson_id': lesson_id}
                        - trong bảng teach_info với {'tel': tel, 'add': add, 'email': email}
                    - trong trường hợp là giáo viên chủ nhiệm, sau khi check không lỗi sẽ insert teacher.id vào class_room.teacher_id, 
                    đồng thời insert teacher_id vào Teach_Class với class_room_id và lesson có lessontag.is_visible là True và lessontag.is_schedule là False (môn Tổng hợp) tương ứng
                    ** Môn tổng hợp là thư mục để GVCN upload cho lớp, nó không xuất hiện ở schedule nhưng cần để link với GVCN và lớp
                    - với teach_class: sau khi check không lỗi =>
                        Nếu remove khỏi lớp học:
                            - sẽ set Teach_Class.teacher_id thành None tương ứng với Teach_Class có teacher_id, year_id, lesson_id
                            - sẽ set Schedule.teacher_id thành None tương ứng với Schedule có teacher_id, year_id, semester_id
                        Nếu thay đổi lớp học:
                            - sẽ lấy mỗi teach_class với lesson_id, year_id để query, từ đó sẽ query tất cả Teach_Class.class_room_id với teacher_id, year_id, lesson_id,
                            so sánh với teach_class mới từ đó insert hoặc remove
                            - sẽ lấy mỗi Schedule tương ứng với class_room_id, lesson_id, year_id, semester_id để insert hoặc remove teacher_id
                    - Backend sẽ trả về thông tin mới được cập nhật và {'msg': 'Đã cập nhật lại thông tin của giáo viên Nguyễn Văn Tý!'}
                    - Audit_log sau khi thao tác gọi API
                B3: FE sẽ đóng cửa sổ cập nhật và gọi lại danh sách giáo viên với dữ liệu đã được cập nhật và thông tin: 'Đã cập nhật lại thông tin của giáo viên Nguyễn Văn Tý!'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 3 bảng teachers, teacher_info, class_room, lesson, teach_class, year
                - teachers:
                    - id: primary key integer
                    - name: string (vd: Nguyễn Văn Tý)
                    - lesson_id: foreign key integer - link với lesson

                - teacher_info:
                    - teacher_id: foreign key integer - link với teachers
                    - email: str
                    - tel: str
                    - add: str

                - class_room:
                    - teacher_id: foreign key integer - link với teachers
                
                - lesson:
                    - id: primary key integer

                - year:
                    - id: primary key integer

                - teach_class:
                    - teacher_id: foreign key integer - link với teachers
                    - lesson_id: foreign key integer - link với lesson
                    - class_room_id: foreign key integer - link với class_room_id
                    - year_id: foreign key integer - link với year
                    *** ràng buộc unique với class_room_id, lesson_id và year_id:   __table_args__ = (UniqueConstraint('class_room_id', 'lesson_id', 'year_id', name = 'uq_cls_les_year'),)

                - Schedule:
                    - teacher_id: foreign key integer - link với teachers
                    - lesson_id: foreign key integer - link với lesson
                    - period_id: foreign Key integer - link với period
                    - class_room_id: foreign key integer - link với class_room

            #### API Endpoint
                Endpoint name: 
                    Update teacher
                Method & URL:
                    PUT /api/teachers/<int:teacher_id>
                Role:
                    admin
                Body:
                    {'name': 'Nguyễn Văn Tý',
                     'tel': 0909123445,
                     'add': 'Cần Thơ',
                     'email': 'ty_nguyen@example.com',
                     'class_room': '10B',
                     'class_room_id': 2,
                     'lesson_id': 5,
                     'teach_class': [1, 2],
                     'year_id': 10,
                     'semester_id': 2
                    }
                Response:    
                    {'msg': 'Đã cập nhật lại thông tin của giáo viên Nguyễn Văn Tý!'}, 200
            #### Validation rule
                Input validation (Pydantic):
                    UserSchemas.User(BaseModel):
                        name: str ko được chứa ký tự đặc biệt và số
                        add: str ko được chứa ký tự đặc biệt
                    TeacherCreateSchema(UserSchemas.User):
                        tel: str chỉ được chứa 10 số
                        email: EmailStr
                        class_room: Optional[str] | None 
                        class_room_id: Optional[int] | None
                        lesson_id: int
                        year_id: int
                        teach_class: Optional[list]

                Business validation:
                        - teacher_id có tồn tại không?
                        - year_id có tồn tại không?
                        - lesson_id có hợp lệ không?
                        - class_room_id có hợp lệ không?
                        - home_class đã có giáo viên chủ nhiệm chưa?
                        - teach_class có bị trùng với giáo viên khác không?
                
                Các lỗi thường gặp nếu vi phạm:
                        - pydantic:
                            {'status': 'Validation_error', 'msg': 'Chưa chọn môn học!'} 422
                            {'status': 'Validation_error', 'msg': 'Họ và tên không được chứa số và ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Số điện thoại chỉ được chứa 10 chữ số'} 422
                            {'status': 'Validation_error', 'msg': 'Địa chỉ không được chứa ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Username không hợp lệ'} 422
                             
                        - Business logic:
                            {'status': 'Logic_error', 'msg': 'Lớp học đã có giáo viên bộ môn này!'} 400
                            {'status': 'Logic_error', 'msg': 'Username đã được sử dụng!'} 409
                            {'status': 'Logic_error', 'msg': 'Lớp 10A đã có giáo viên chủ nhiệm!'} 400
                            *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

        ### Các API hỗ trợ khác:
            /api/teachers             | GET | lấy danh sách giáo viên theo (year_id, name, lesson, teach_class) | admin, Teacher 
            /api/teachers/<id>/status | PUT | ẩn hoặc hiện giáo viên theo status | admin

    ## Chức năng học sinh:
        ### Tạo học sinh:
            #### Giới thiệu chức năng
                cho phép admin, Teacher tạo 1 học sinh (bao gồm thông tin cơ bản, login, khối lớp và lớp học)
            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'name': 'Lê Văn Tèo',
                     'tel': 0909123995,
                     'add': 'Cần Thơ',
                     'bod': '2011-06-13',
                     'grade': 9,
                     'year_id': 1
                     'year': "2025 - 2026"
                     'gender': 'Nam',
                     'conduct': True,
                     'absent_day': 1,
                     'note': 'Giỏi, nhanh nhạy'
                     'transfer_info': 'Chuyển từ trường ABC'
                     'lesson': [{'lesson_id': 31, 'score_1': 8.0, 'score_2': 8.0}, 
                                {'lesson_id': 20, 'score_1': 7.0, 'score_2': 8.0}, 
                                {'lesson_id': 26, 'score_1': 7.0, 'score_2': 8.0}, 
                                {'lesson_id': 23, 'score_1': 6.0, 'score_2': 7.0}, 
                                {'lesson_id': 22, 'score_1': 8.0, 'score_2': 6.0}, 
                                {'lesson_id': 24, 'score_1': 8.0, 'score_2': 7.0}, 
                                {'lesson_id': 25, 'score_1': 7.0, 'score_2': 9.0}, 
                                {'lesson_id': 21, 'score_1': 8.0, 'score_2': 8.0}, 
                                {'lesson_id': 27, 'score_1': 6.0, 'score_2': 7.0}]
                    }
                    (ở đây field gender, bod, tel có thể None để cập nhật sau)

                B2: Backend:
                    - Check authorization và role (admin và Teacher)
                    - route tiếp nhận và validate input bằng pydantic
                    - Business Logic Check và lấy user_id
                    - Record db: bảng students với {'name': name} và bảng student_info với {'student_id': student.id, 'tel': tel, 'add': add, 'gender': gender, 'bod': bod}
                    - Tạo 1 student code từ mã trường, niên khóa và chạy liên tục theo số lượng học sinh, sau đó check đảm bảo ko bị trùng student_code và chèn vào bảng student
                    - Generate data cho new user sau đó record vào bảng user với: 
                            {
                            'username': student_code.lower(),
                            'password': hashed_generate_password,
                            'tmp_password': generate_password,
                            'role': 'Student'
                            }
                    - Link student.user_id với user.id
                    - Record vào lịch sử học tập:
                            {
                            'year_id': year_id 
                            'student_id': student_id,
                            'lesson': [{'lesson_id': 31, 'score_1': 8.0, 'score_2': 8.0}, 
                                       {'lesson_id': 20, 'score_1': 7.0, 'score_2': 8.0}, 
                                       {'lesson_id': 26, 'score_1': 7.0, 'score_2': 8.0}, 
                                       {'lesson_id': 23, 'score_1': 6.0, 'score_2': 7.0}, 
                                       {'lesson_id': 22, 'score_1': 8.0, 'score_2': 6.0}, 
                                       {'lesson_id': 24, 'score_1': 8.0, 'score_2': 7.0}, 
                                       {'lesson_id': 25, 'score_1': 7.0, 'score_2': 9.0}, 
                                       {'lesson_id': 21, 'score_1': 8.0, 'score_2': 8.0}, 
                                       {'lesson_id': 27, 'score_1': 6.0, 'score_2': 7.0}]
                            }
                        - bảng student_lesson_period với mỗi môn học và mỗi học kỳ với điểm tương ứng cho học sinh, đồng thời gán kết quả đạt nếu điểm TB >= 5
                        - bảng student_lesson_annual với mỗi môn học với điểm TB môn học cả năm đc tính theo (score1 + score2*2)/3 và gán kết quả đạt nếu >= 5

                        - Từ thông tin điểm các môn qua từng học kỳ năm trước và cả năm, ta xét bảng điểm để xếp loại theo chỉ đạo từ Bộ giáo dục và tính trung bình điểm của các môn 

                            max_lesson = lesson_scores.shape[1]
                            min_required_lesson = max_lesson - 1

                            cond_good = ((np.all(lesson_scores >= 6.5, axis=1)) & (np.sum(lesson_scores >= 8, axis=1) >= 6))

                            cond_fair_A = ((np.all(lesson_scores >= 5, axis=1)) & (np.sum(lesson_scores >= 6.5, axis=1) >= 6))
                            cond_fair_B = ((np.sum(lesson_scores >= 6.5, axis=1) == min_required_lesson) & (np.sum(lesson_scores >= 8, axis=1) >= 6) & (np.sum(lesson_scores < 6.5, axis=1) == 1))
                            cond_fair = cond_fair_A | cond_fair_B

                            cond_avg_A = ((np.all(lesson_scores >= 3.5, axis=1)) & (np.sum(lesson_scores >= 5, axis=1) >= 6))
                            cond_avg_B = ((np.sum(lesson_scores >= 6.5, axis=1) == min_required_lesson) & (np.sum(lesson_scores >= 8, axis=1) >= 6) & (np.sum(lesson_scores < 5, axis=1) == 1))
                            cond_avg_C = ((np.sum(lesson_scores >= 5, axis=1) == min_required_lesson) & (np.sum(lesson_scores >= 6.5, axis=1) >= 6) & (np.sum(lesson_scores < 5, axis=1) == 1))
                            cond_avg = cond_avg_A | cond_avg_B | cond_avg_C

                        - Từ đó insert vào bảng Student_Period_Summary với {'student_id': student_id,
                                                                            'period_id': period_id,
                                                                            'grade': grade,
                                                                            'status': status,
                                                                            'score': avg_score} 

                                               và Student_Year_Summary với {'student_id': student_id,
                                                                            'year_id': year_id,
                                                                            'grade': grade,
                                                                            'conduct': conduct,
                                                                            'absent_day': absent_day
                                                                            'note': note
                                                                            'learning_status': 'Tốt' | 'Khá' | 'Đạt' | 'Chưa đạt', theo điều kiện ở trên
                                                                            'score': avg_score} 
                    - Backend sẽ trả về với nội dung {'msg': 'Đã thêm học sinh Lê Văn Tèo vào hệ thống'}, 201
                    - Activity_log sau khi thao tác thành công
                    - Audi_log nếu có bug

                B3: FE sẽ hiện thị thông tin với nội dung: 'Đã thêm học sinh Lê Văn Tèo vào hệ thống'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 10 bảng users, students, student_info, year, grade, period, student_lesson_period, student_lesson_annual, student_period_summary, student_year_summary
                - students:
                    - id: primary key integer
                    - name: string (vd: Nguyễn Văn Tý)
                    - user_id: foreign key integer - link với users

                - student_info:
                    - student_id: foreign key integer - link với student
                    - bod: date
                    - tel: str
                    - add: str
                    - gender: str

                - users:
                    - id: primary key integer
                    - username: str
                    - password: str
                    - role: str ('Student')
                    - tmp_password: str
                    - changed_password: bool 

                - student_lesson_period:
                    - student_id: foreign key integer - link với student
                    - lesson_id: foreign key integer - link với student
                    - period_id: foreign key integer - link với period
                    *** ràng buộc unique với student_id, lesson_id, period_id:
                        __table_args__ = (UniqueConstraint('student_id', 'lesson_id', 'period_id', name = 'stu_ls_per_uniq'),)

                - student_lesson_annual:
                    - student_id: foreign key integer - link với student
                    - lesson_id: foreign key integer - link với lesson
                    - year_id: foreign key integer - link year
                    *** ràng buộc unique với student_id, lesson_id, period_id:
                        __table_args__ = (UniqueConstraint('student_id', 'lesson_id', 'year_id', name = 'stu_ls_yea_uniq'),)

                - student_period_summary:
                    - student_id: foreign key integer - link với student
                    - lesson_id: foreign key integer - link với student
                    - period_id: foreign key integer - link với period
                        *** ràng buộc unique với student_id, lesson_id, period_id:
                        __table_args__ = (UniqueConstraint('student_id', 'lesson_id', 'period_id', name = 'stu_ls_per_uniq'),)

                - student_year_summary:
                    - student_id: foreign key integer - link với student
                    - year_id: foreign key integer - link year
                    - grade: foreign key integer - link grade
                    *** ràng buộc unique với student_id, lesson_id, period_id:
                        __table_args__ = (UniqueConstraint('student_id', 'year_id', name = 'stu_yea_uniq'),)

                - year:
                    - id: primary key integer
                
                - grade:
                    - id: primary key integer

                - period:
                    - id: primary key integer

            #### API Endpoint
                Endpoint name:
                    Create student
                Method & URL:
                    POST api/students
                Role:
                    admin/Teacher
                Body: 
                    {'name': 'Lê Văn Tèo',
                     'tel': 0909123995,
                     'add': 'Cần Thơ',
                     'bod': '2011-06-13',
                     'grade': 3,
                     'year_id': 1
                     'year': "2025 - 2026"
                     'gender': 'Nam',
                     'conduct': True,
                     'absent_day': 1,
                     'note': 'Giỏi, nhanh nhẹn'
                     'transfer_info': ''Chuyển từ trường ABC'
                     'lesson': [{'lesson_id': 31, 'score_1': 8.0, 'score_2': 8.0}, 
                                {'lesson_id': 20, 'score_1': 7.0, 'score_2': 8.0}, 
                                {'lesson_id': 26, 'score_1': 7.0, 'score_2': 8.0}, 
                                {'lesson_id': 23, 'score_1': 6.0, 'score_2': 7.0}, 
                                {'lesson_id': 22, 'score_1': 8.0, 'score_2': 6.0}, 
                                {'lesson_id': 24, 'score_1': 8.0, 'score_2': 7.0}, 
                                {'lesson_id': 25, 'score_1': 7.0, 'score_2': 9.0}, 
                                {'lesson_id': 21, 'score_1': 8.0, 'score_2': 8.0}, 
                                {'lesson_id': 27, 'score_1': 6.0, 'score_2': 7.0}]
                    }
                Response:
                    {'msg': 'Đã thêm học sinh Lê Văn Tèo vào hệ thống'}, 201

            #### Validation rule
                Input validation (Pydantic):
                    class StudentItem(BaseModel):
                        lesson_id: int
                        score_1: float
                        score_2: float

                        @field_validator('score_1', 'score_2')
                        def score_validates(cls, v):
                            if 0 >= v or v >= 10:
                                raise ValueError('Điểm số phải từ 0 đến 10!')
                            return v

                    class StudentCreate(UserSchemas.User):
                        tel: Optional[str] | None
                        gender: str
                        bod: Optional[date] = None
                        year_id: int
                        year: str
                        grade: int
                        conduct: bool
                        lesson: List['StudentSchemas.StudentItem']
                        note: str
                        absent_day: Optional[int]
                        
                        @field_validator('grade', mode='before')
                        def class_validator(cls, v):
                            if v in ['', 'None', 'null']:
                                raise ValueError('Chưa nhập thông tin khối lớp!')
                            return v
                        
                        @field_validator('bod', 'absent_day', mode='before')
                        def bod_cls_room_validate(cls, v):
                            if v in ['', 'null']:
                                return 
                            return v
                        
                        @field_validator('conduct', mode='before')
                        def conduct_bool_validate(cls, v):
                            if v in ['', 'null']:
                                raise ValueError('Chưa nhập hạnh kiểm của học sinh!')
            
                            return v
    
                    Business validation:
                        - year_id có tồn tại không?
                        - year có hợp lệ không?
                        - grade có hợp lệ không?
                        - class_room_id có hợp lệ không?
                
                Các lỗi thường gặp nếu vi phạm:
                        - pydantic:
                            {'status': 'Validation_error', 'msg': 'Họ và tên không được chứa số và ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Số điện thoại chỉ được chứa 10 chữ số'} 422
                            {'status': 'Validation_error', 'msg': 'Địa chỉ không được chứa ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Chưa nhập thông tin khối lớp'} 422
                             
                            *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

        ### Xét duyệt cho học sinh mới:
            Cho phép admin xét duyệt lên lớp hoặc lưu ban cho học sinh mới sau khi được thêm vào hệ thống
            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    List học sinh
                    [{'student_id': 266, 'status': 'Lên lớp'}, 
                     {'student_id': 267, 'status': 'Lên lớp'}, 
                     {'student_id': 268, 'status': 'Lên lớp'}, 
                     {'student_id': 265, 'status': 'Lên lớp'}]
                    
                B2: Backend:
                    - Check authorization, role (admin) 
                    - route tiếp nhận và validate input bằng pydantic, và lấy user_id, year_id
                    - từ year_id, lấy next_year_id
                    - Vào vòng lặp để add cho từng học sinh:
                        Lấy student từ bảng student để check id và lấy thông tin add vào activity log
                        Sau đó từ lấy student_year_summary với {'student_id': student_id,
                                                                 'year_id': year_id}
                        để cập nhật status, đồng thời bật Treu cho review_status 

                        Học sinh sau khi duyệt sẽ lấy grade từ student_year_summary ở trên + 1 | giữ nguyên đối với 'Lên lớp' | 'Lưu ban'
                        Insert row mới cho student_year_summary với {'student_id': student_id,
                                                                     'year_id': next_year_id,
                                                                     'grade': grade
                                                                     'is_new_student': True}

                    - Activity log ghi lại lịch sử hoạt động của user với {'user_id': user_id,
                                                                            'module': 'user',
                                                                            'target_id': [i.get('student_id') for i in data],
                                                                            'action': 'APPROVE',
                                                                            'detail': f'Xét duyệt học sinh: {', '.join(detail_changes)}
                                                                            }

                B3:  FE sẽ hiển thị nội dung: 'Đã xét duyệt học sinh!'


            #### Cấu trúc dữ liệu:
                Các thành phần chính có liên quan trong 2 bảng student, student_year_summary, year, class_room, grade

            #### API Endpoint
                Endpoint name:
                    Student review for new year
                Method & URL:
                    PUT api/years/<int:id>/students/review
                Role:
                    admin
                Body: 
                    [{'student_id': 266, 'status': 'Lên lớp'}, 
                     {'student_id': 267, 'status': 'Lên lớp'}, 
                     {'student_id': 268, 'status': 'Lên lớp'}, 
                     {'student_id': 265, 'status': 'Lên lớp'}]
                Response:
                    {'msg': 'Đã xét duyệt học sinh!'}, 200


            #### Validation rule
                class StudentReview(BaseModel):
                    student_id: int
                    status: str

                    @field_validator('status')
                    def status_validate(cls, v):
                        if v not in ['', 'Lên lớp', 'Lưu ban', 'Bảo lưu']:
                            return ValueError('Status không hợp lệ!')
                        return v
                  
                            
                    *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

        ### Xếp lớp cho học sinh:
            Cho phép admin xếp lớp cho học sinh sau khi được xét duyệt

            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'year_id': 10, 
                    'student_assign_list': [{'class_room_id': 14, 'student_id': 139},
                                            {'class_room_id': 15, 'student_id': 141}]
                    }
                
                B2: Backend:
                    - Check authorization, role (admin) 
                    - route tiếp nhận và validate input bằng pydantic, và lấy user_id
                    - Business check logic (year_id) từ đó lấy period_id 
                    - Vào vòng lặp để add cho từng học sinh:
                        - Business check logic (class_room_id)
                        - Get student và grade
                        - Bật True cho assign_status cho biết đã assign cho học sinh ở bảng student_year_summary với student_id và year_id 
                        - Lấy student_year_summary với student_id, year_id: cập nhật class_room_id
                        - combo select insert cho row mới
                            - ở student_year_summary với student_id, class_room_id, year_id
                            - ở student_lesson_period với student_id, tất cả các môn học tương đương với grade, và period tương ứng với 2 học kỳ + năm học
                        lấy danh sách tên học sinh để chèn vào activity log
                        - Ghi lại kết quả thành công của thao tác vào bảng activity log

                B3: FE sẽ hiện thị thông tin với nội dung: 'Đã hoàn thành xếp lớp cho học sinh!' 

            #### Cấu trúc dữ liệu:
                Các thành phần chính có liên quan trong 6 bảng student, lesson, class_room, year, semester, period, student_year_summary, student_lesson_period
                    - student_year_summary:
                        - student_id: foreign key integer - link với student
                        - year_id: foreign key integer - link với year 
                        - grade: foreign key integer - link với grade
                        - class_room_id: foreign key integer - link với class_room
                        *** ràng buộc unique với student_id, year_id:
                            __table_args__ = (UniqueConstraint('student_id', 'year_id', name = 'stu_yea_uniq'),)
                    
                    - student_lesson_period:
                        - student_id: foreign key integer - link với student
                        - lesson_id: foreign key integer - link với lesson
                        - period_id: foreign key integer - link với period

                    - student:
                        - id: primary key integer

                    - lesson:
                        - id: primary key integer
        
                    - class_room:
                        - id: primary key integer

                    - year:
                        - id: primary key integer
                    
                    - semester:
                        - id: primary key integer
                    
                    - period:
                        - id: primary key integer
                        - year_id: foreign key integer - link với year
                        - semester_id: foreign key integer - link với semester

            #### API Endpoint
                Endpoint name:
                    Student assignment for new year
                Method & URL:
                    POST api/students/assignment
                Role:
                    admin
                Body: 
                    {'year_id': 10, 
                    'student_assign_list': [{'class_room_id': 14, 'student_id': 139},
                                            {'class_room_id': 15, 'student_id': 141}]
                    }
                Response:
                    {'msg': 'Đã hoàn thành xếp lớp cho học sinh!'}, 201

            #### Validation rule
                    Input validation (Pydantic):
                        class StudentAssignmentItem(BaseModel):
                            class_room_id: int
                            student_id: int

                        class StudentAssignment(BaseModel):
                            year_id: int
                            semester_id: int
                            student_assign_list: List['StudentSchemas.StudentAssignmentItem']   

                    Business validation:
                        - year_id có tồn tại không?
                        - student_id có tồn tại không?
                        - semester_id có tồn tại không?
                        - class_room_id có hợp lệ không?                                  
                             
                        *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

    ## Chức năng cho điểm:
        ### Cho điểm học sinh
            Cho phép giáo viên cho điểm học sinh theo môn học của mình

            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm: 
                    {'year_id': 10, 
                     'lesson_id': 43, 
                     'semester_id': 1, 
                     'students': [{'student_id': 275, 'scores': {1: {1: 6.0}}}]
                     }

                    cấu trúc scores: {score_type_id: {attempt: score}}
                B2: BE:
                    - Check authorization và role (admin và Teacher)
                    - route tiếp nhận và validate input bằng pydantic
                    - Lấy period_id từ year_id và semester_id
                    - Sau đó lặp qua từng học sinh:
                        - Lấy student từ bảng student
                        - Lấy student_lesson_period_id từ student_id, lesson_id, period_id
                        - Check score:
                            - Nếu score chưa có, tiến hành upsert score với {'student_lesson_period_id': data['student_lesson_period_id'],
                                                                             'score_type_id': score_type_id, 
                                                                             'attempt': attempt,
                                                                             'score': score[attempt]}
                            - Nếu score đã có, sẽ chuyển tất cả các tổng kết nếu có về None, để giáo viên tổng kết lại chính xác mà không bị quên
                                - student_lesson_period
                                - student_period_summary
                                - student_lesson_annual
                                - student_year_summary

                    - Ghi lại thao tác vào activity log
                
                B3: FE sẽ hiển thị lại bảng điểm đã cập nhật và msg thông báo 'Đã cho điểm cho học sinh!'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong Score, SCore_Type, Student_Lesson_Period, Student_Lesson_Annual, Student_Period_Summary, Student_Year_Summary, Period, Lesson, Students
                - Score link với Student_Lesson_Period bằng student_lesson_period_id để xác định học kỳ, môn học và học sinh
                - Score link với Score_Type bằng score_type_id để xác định weight(hệ số)
                - Các bảng tổng kết được truy xuất ngược để buộc người dùng không quên tổng kết đúng số liệu đã thay đổi

            #### API Endpoint
                Endpoint name:
                    Upsert Score
                Method & URL:
                    PUT /api/academic/entity/scores
                Role:
                    admin, Teacher
                Body: 
                    {'year_id': 10, 
                     'lesson_id': 43, 
                     'semester_id': 1, 
                     'students': [{'student_id': 275, 'scores': {1: {1: 6.0}}}]
                     }

                Response:
                    {'msg': 'Đã cho điểm cho học sinh!'}, 200

            #### Validation rule
                Input validation (Pydantic):
                    class Scores(YearId):
                        lesson_id: int
                        semester_id: int
                        students: List['AcademicUpdateSchemas.ScoresItem']

                    class ScoresItem(BaseModel):
                        student_id: int
                        scores: Optional[Dict[int, Dict[int, Any]]] = Field(default=None)
                        note: Optional[str] = None

                        @validator('scores')
                        def validate_scores(cls, v):
                            for score_type_id, attempts in v.items():
                                for attempt, score in attempts.items():
                                    if score == '':
                                        attempts[attempt] = None

                                    try:
                                        score = float(score)
                                            
                                    except:
                                        raise ValueError('Điểm số phải là số!')
                                    
                                    if 0 > score or score > 10:
                                        raise ValueError('Điểm sổ nằm trong dãy từ 0 đến 10!')
                                            
                                    attempts[attempt] = score
                                    
                            return v

                *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log
    
    ## Tổng kết điểm môn theo học kỳ cho lớp
        ### Tổng kết điểm môn theo học kỳ cho lớp:
            Cho phép admin và Teacher tổng kết điểm của môn học theo học kỳ cho lớp đã được chọn

            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm: 
                    {'year_id': 10, 'class_room_id': 24, 'lesson_id': 43, 'semester_id': 1}
                    
                B2: BE:
                    - Lấy period_id từ year_id và semester_id
                    - Lấy lớp học từ class_room_id
                    - Lấy toàn bộ student_ids theo period_id và class_room_id

                    - Query lấy toàn bộ danh sách [{'student_id': 275, 'total': Decimal('6.67'), 'status': True}, ...] theo điều kiện:
                        - {'year_id': 10, 'class_room_id': 24, 'lesson_id': 43, 'semester_id': 1}
                        - Và tính trung bình điểm và xét kết quả:
                                    weighted_score = func.sum(Score_Type.weight * Score.score)
                                    total_weight = func.sum(Score_Type.weight)
                                    avg_score = func.round(cast(weighted_score / total_weight, Numeric), 2)
                                    status = case((avg_score >= 5, True), else_ = False)

                        - Vào vòng lặp từng học sinh trong danh sách trên, lấy student_lesson_period bằng student_id, lesson_id, period_id
                        - Từ student_lesson_period, check điểm kiểm tra giữa kỳ và cuối kỳ (2 điểm số quan trọng) nếu chưa có ở bất kỳ học sinh nào sẽ raise lỗi thiếu điểm ko đc tổng kết
                        - Nếu ổn sẽ tiến hành cập nhật vào student_lesson_period với status và avg_score

                    - Tiến hành ghi vào activity log với nội dung {'user_id': user_id,
                                                                   'target_id': student_ids,
                                                                   'module': 'academic/entity',
                                                                   'action': 'UPDATE',
                                                                   'detail': f"Tổng kết điểm cho lớp {class_room.class_room}"}

            #### Cấu trúc dữ liệu:
                Các thành phần chính có liên quan trong Score, Score_Type, Student_Lesson_Period, Period, Lesson, Students, Class_room
                - Score link với Student_Lesson_Period bằng student_lesson_period_id để xác định học kỳ, môn học và học sinh
                - Score link với Score_Type bằng score_type_id để xác định weight(hệ số)
                - Key ở đây là query SQL để đưa về danh sách cần và add vào Student_Lesson_Period

            #### API Endpoint
                Endpoint name:
                    Summary Lesson Period
                Method & URL:
                    PUT /api/academic/entity/scores/lessons/summary
                Role:
                    admin, Teacher
                Body: 
                    {'year_id': 10, 'class_room_id': 24, 'lesson_id': 43, 'semester_id': 1}
                Response:
                    {'msg': Đã tổng kết điểm cho lớp 10A!}, 200

            #### Validation rule
                Input validation (Pydantic):
                    class SummaryLessonPeriod(BaseScores):
                        lesson_id: int
                        semester_id: int

                    class BaseScores(YearId):
                        class_room_id: int
                        
                        @field_validator('class_room_id', mode='before')
                        def validate_class_room_id(cls, v):
                            if v in ['', 'null']:
                                raise ValueError('Chưa chọn lớp học!')

                            return v

                    class YearId(BaseModel):
                        year_id: int

                        @field_validator('year_id')
                        def grade_id_validator(cls, v):
                            if v in ['', None]:
                                raise ValueError('Niên khóa không được bỏ trống')
                            return v

                    Business validation:
                        - kiểm tra điểm giữa kỳ | cuối kỳ đã có chưa?
                
                    Các lỗi thường gặp nếu vi phạm:
                        - Bussiness logic:
                            {'status': 'Logic_error', 'msg': 'Học sinh vẫn chưa có điểm kiểm tra giữa kỳ!'} 400
                            {'status': 'Logic_error', 'msg': 'Học sinh vẫn chưa có điểm thi cuối kỳ!'} 400

                    *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

    ## Tổng kết học kỳ
        ### Tổng kết điểm, xếp loại, hạnh kiểm, chuyên cần cho học kỳ 
            Cho phép admin | Teacher tổng kết điểm, xếp loại, hạnh kiểm, chuyên cần theo học kỳ cho học sinh sau khi đã có đầy đủ tổng kết của các môn trong kỳ

            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'year_id': 10, 
                     'class_room_id': 24, 
                      'students': [{'absent_day': 1, 'conduct': None, 'note': None, 'status': None, 'student_id': 275}, ...]}

                B2: BE:
                    - Query SQL lấy danh sách gồm học sinh, list điểm trung bình tất cả của môn, trung bình cộng điểm của các môn trên theo class_room_id, year_id, semester_id
                    - từ list trên dựng data frame và check nếu có bất kỳ môn học nào của bất kỳ học sinh nào chưa tổng kết sẽ raise lỗi 'Còn môn học chưa tổng kết!'
                    - Chuyển cột danh sách điểm sang np.array để tự động select kết quả tương ứng (tái sử dụng logic ở create new student chỗ add lịch sử học tập)
                    - Sau khi có được status, chèn vào data frame từ đó chuyển sang dict theo dạng {275: {'score': Decimal('7.74'), 'status': 'Khá'}, 
                                                                                                    276: {'score': Decimal('5.29'), 'status': 'Chưa đạt'}}
                    - Từ đó loop từ dict data['students'] và lấy values tương ứng chèn vào student_semester_summary
                    - Lấy thông tin tên lớp từ class_room_id
                    - Ghi lại activity log với {'user_id': user_id,
                                                'target_id': data['class_room_id'],
                                                'module': 'academic/entity',
                                                'action': 'UPDATE',
                                                'detail': f"Tổng kết học kỳ {data['semester_id']} cho lớp {class_room.class_room}"}

                B3: FE sẽ hiện thị lại danh sách lớp với thông tin đc cập nhật và msg với nội dung: 'Đã tổng kết!'
            
            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 3 bảng student_lesson_period, period, class_room, student_period_summary

            #### API Endpoint
                Endpoint name:
                    Summary Period
                Method & URL:
                    PUT /api/academic/entity/semesters/1/summary
                Role:
                    admin, Teacher
                Body: 
                    {'year_id': 10, 
                     'class_room_id': 24, 
                      'students': [{'absent_day': 1, 'conduct': None, 'note': None, 'status': None, 'student_id': 275}, ...]}
                Response:
                    {'msg': 'Đã tổng kết!'}, 200

            #### Validation rule
                class SummaryPeriod(BaseScores):
                    students : List['AcademicUpdateSchemas.SummaryItem']

                    @validator('students')
                    def validate_students(cls, v):
                        for item in v:
                            if item.conduct in ['', None]:
                                raise ValueError('Chưa đánh giá hạnh kiểm học sinh đầy đủ!')
                            
                            if item.absent_day < 0:
                                raise ValueError('Số ngày nghỉ không hợp lệ!')
                            
                            elif item.absent_day in ['', None]:
                                item.absent_day = 0

                        return v

                class SummaryItem(BaseModel):
                    student_id: int
                    absent_day: Optional[int]
                    conduct: Optional[bool]
                    note: Optional[str]
                    status: Optional[str]

                class BaseScores(YearId):
                    class_room_id: int
                    
                    @field_validator('class_room_id', mode='before')
                    def validate_class_room_id(cls, v):
                        if v in ['', 'null']:
                            raise ValueError('Chưa chọn lớp học!')

                        return v
                
                class YearId(BaseModel):
                    year_id: int

                    @field_validator('year_id')
                    def grade_id_validator(cls, v):
                        if v in ['', None]:
                            raise ValueError('Niên khóa không được bỏ trống')
                        return v

                Các lỗi thường gặp nếu vi phạm:
                    - pydantic:
                        {'status': 'Logic_error', 'msg': 'Còn môn học chưa được tổng kết!} 400
                        {'status': 'Validation_error', 'msg': Chưa đánh giá hạnh kiểm học sinh đầy đủ!} 422
                            
                        *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

    ## Tổng kết Năm học
        ### Tổng kết năm học sau khi đã tổng kết 2 học kỳ:
            Cho phép admin, Teacher tổng kết cả năm cho cả lớp sau khi đã tổng kết 2 học kỳ

            #### Luồng hoạt động
                B1: FE truyền dữ liệu 
                    {'students': 
                        [{'absent_day': 1, 
                          'conduct': None,
                          'lessons': {'43': {'Toán': None}, '44': {'Lý': None}, '45': {'Hóa': None}, 
                          '46': {'Sinh': None}, '47': {'Sử': None}, '48': {'Địa': None}, '49': {'Văn': None}, '50': {'Anh văn': None}}, 
                          'name': 'Hàn Lập', 
                          'note': None, 
                          'score': None, 'status': None, 'student_id': 275}], ...} 
                          'class_room_id': 24, 
                          'year_id': 10}
                    Thông tin học sinh chỉ để render bảng, dữ liệu cần ở đây là class_room_id, year_id (absent_day, conduct, note nếu có)
                B2: BE
                    - validate year_id và lấy class_room từ class_room_id
                    - Từ year_id và class_room_id query tính điểm trung bình của từng môn với (học kỳ 2 * 2 + học kỳ 1) / 3 kèm student_id, lesson_id, year_id để upsert vào bảng student_lesson_annual
                    - Từ year_id và class_room_id query lấy student_id và list điểm trung bình tất cả các môn ở bước trên và chuyển sang dataframe
                    - Check xem tất cả học sinh đều đã được tổng kết chưa, nếu chưa sẽ raise 'Còn học sinh chưa được tổng kết!'
                    - tương tự chuyển danh sách điểm sang np.array để select theo logic đánh giá kết quả học tập để lấy learning_status và điểm trung bình và chuyển về dict
                    - Từ year_id lấy next_year_id
                    - loop từng data['students'] để chèn absent_day, conduct, note vào student_year_summary, cùng với learning_status và điểm trung bình
                        - Trong trường hợp learning_status == 'Chưa đạt'
                            - set student_year_summary.status = 'Thi lại' và student_year_summary.retest_status = True
                            - Từ student_id và year_id, hệ thống lấy môn học cần retest tự chèn trực tiếp vào bảng Retest với student_id, year_id, lesson_id
                            (Với số lần query tối thiểu cho mỗi học sinh, ko loop, Các thao tác khởi tạo dữ liệu được thực hiện bằng SQL theo tập (set-based),
                                                                              đảm bảo tính nguyên tử và có thể chạy lặp nhiều lần mà không gây trùng dữ liệu.)
                        - Trong trường hợp learning_status != 'Chưa đạt' và student_year_summary.grade == 12:
                            - set student_year_summary.status = 'Hoàn thành'
                        - Trong trường hợp learning_status != 'Chưa đạt' và student_year_summary.grade < 12: 
                            - set student_year_summary.status = 'Lên lớp' và student_year_summary.review_status = True

                    - Ghi lại thao tác vào activity log với detail là 'Tổng kết cuối năm cho học sinh lớp 10A'

                B3: FE sẽ hiện thị lại danh sách lớp với thông tin đc cập nhật và msg với nội dung: 'Đã tổng kết!'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 3 bảng student_year_summary, period, class_room, student_lesson_annual, Retest, Student_Lesson_Period, Semester

            #### API Endpoint
                Endpoint name:
                    Summary Year
                Method & URL:
                    PUT /api/academic/entity/years/10/summary
                Role:
                    admin, Teacher
                Body: 
                    {'students': 
                        [{'absent_day': 1, 
                          'conduct': None,
                          'lessons': {'43': {'Toán': None}, '44': {'Lý': None}, '45': {'Hóa': None}, 
                          '46': {'Sinh': None}, '47': {'Sử': None}, '48': {'Địa': None}, '49': {'Văn': None}, '50': {'Anh văn': None}}, 
                          'name': 'Hàn Lập', 
                          'note': None, 
                          'score': None, 'status': None, 'student_id': 275}], ...} 
                          'class_room_id': 24, 
                          'year_id': 10}
                Response:
                    {'msg': Đã tổng kết năm học!'}, 200

            #### Validation rule
                class SummaryYear(BaseModel):
                    students : List['AcademicUpdateSchemas.SummaryItem']
                    class_room_id: int
                    
                    @validator('students')
                    def validate_students(cls, v):
                        for item in v:
                            if item.conduct in ['', None]:
                                raise ValueError('Chưa đánh giá hạnh kiểm học sinh đầy đủ!')
                            
                            if item.absent_day in ['', None]:
                                item.absent_day = 0

                            elif item.absent_day < 0:
                                raise ValueError('Số ngày nghỉ không hợp lệ!')

                        return v

                class SummaryItem(BaseModel):
                    student_id: int
                    absent_day: Optional[int]
                    conduct: Optional[bool]
                    note: Optional[str]
                    status: Optional[str]

                Các lỗi thường gặp nếu vi phạm:
                    - pydantic:
                        {'status': 'Validation_error', 'msg': Chưa đánh giá hạnh kiểm học sinh đầy đủ!} 422
                    - Bussness logic:
                        {'status': 'Logic_error', 'msg': 'Còn học sinh chưa được tổng kết!'} 400
                            
                        *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

    ## Cho điểm đánh giá lại cho học sinh
        ### Thêm điểm đánh giá lại:
            Cho phép admin, Teacher thêm điểm vào mục đánh giá lại những môn học chưa đạt yêu cầu để duyệt lên lớp hay lưu ban

            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm: 
                    [{'student_id': 276, 'lessons': {43: {'score': 5.0}}}, ....]

                B2: BE:
                    - Loop qua list để update điểm cho từng học sinh để lấy student qua student_id
                    - từ lessons; lấy lesson_id, score tiến hành cập nhật vào score bảng Retest với student_id, year_id, lesson_id
                    - Tạo 1 list học sinh được cho điểm để ghi vào activity log lịch sử hoạt động với detail 'Thêm điểm thi lại: Hàn Lập, Nam Cung Uyển'

                B3: FE sẽ hiện thị lại danh sách lớp với thông tin đc cập nhật và msg với nội dung: "Đã thêm điểm thi lại cho học sinh!"

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong Retest, students, lesson, year

            #### API Endpoint
                Endpoint name:
                    Update Retest for Score
                Method & URL:
                    PUT /api/years/10/students/retest
                Role:
                    admin, Teacher
                Body: 
                    [{'student_id': 276, 'lessons': {43: {'score': 5.0}}}, ....]
                    
                Response:
                    {'msg': "Đã thêm điểm thi lại cho học sinh!"}, 200

            #### Validation rule
                - Bussness logic:
                    {'status': 'Logic_error', 'msg': 'Vẫn còn chưa nhập đủ điểm cho học sinh!'} 400

    ## Tổng kết kết quả đánh giá lại cho học sinh
        ### Tổng kết kết quả đánh giá lại cho học sinh
            Cho phép admin, Teacher tổng kết kết quả đánh giá lại sau khi đã có đầy đủ điểm đánh giá lại để xác định học sinh lên lớp hay lưu ban

            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm year_id thông qua api
                B2: BE:
                    - Check tất cả các row của retest theo year_id đã được thêm full chưa
                        - Nếu chưa raise 'Vẫn còn chưa nhập đủ điểm cho học sinh!'
                    - Sau đó sẽ lấy tất cả các môn từ mức đạt của học sinh, merge với kết quả thi lại thành 1 cột và chuyển sang np.array để check logic xem kết quả cả năm học sinh có đạt không
                    - Lấy student_year_summary từ student, year:
                        - Nếu chưa đạt thì set status = 'Lưu ban', retest_status = True, review_status = True
                        - Nếu khác chưa đạt:
                            - grade == 12: => status = 'Hoàn thành'
                            - grade < 12: => status = 'Lên lớp', retest_status = True, review_status = True

                B3: FE sẽ hiện thị lại danh sách lớp với thông tin đc cập nhật và msg với nội dung: Đã tổng kết điểm thi lại!

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong Retest, student_lesson_annual, student_year_summary, lesson, students

            #### API Endpoint
                Endpoint name:
                    Year Summary for Retest
                Method & URL:
                    PUT /api/years/10/summary/retest
                Role:
                    admin, Teacher
                    
                Response:
                    {'msg': Đã tổng kết điểm thi lại!}, 200

    ## Chức năng thời khóa biểu:
        ### Tạo và điều chỉnh thời khóa biểu:
            Cho phép admin tạo mới và điều chỉnh thời khóa biểu cho mỗi lớp theo từng học kỳ và niên khóa
        
            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'year_id': 10,
                     'class_room_id': 27,
                     'semester_id': 1,
                     'schedules': {
                        '1': {'1': {'lesson_id': 51}, 
                              '2': {'lesson_id': 47}, 
                              '3': {'lesson_id': 47}, 
                              '4': {'lesson_id': 50},...
                            }
                        }
                    }

                B2: Backend:
                    - Check authorization và role (admin và Teacher)
                    - route tiếp nhận và validate input bằng pydantic
                    - Lấy period_id từ year_id và semester_id
                    - Giải thuật schedules chuyển thành list of dict [{"lesson_time": lesson_time,
                                                                       "day_of_week": day,
                                                                       "lesson_id": lesson_id}]
                    - Chạy loop list trên:
                        - Trường hợp lesson_id == None (Bỏ chọn): Xóa row ở schedule với {'lesson_time': schedule['lesson_time'],
                                                                                          'day_of_week': schedule['day_of_week'],
                                                                                          'period_id': period_id,
                                                                                          'class_room_id': data['class_room_id']}
                        - Ngược lại là add mới:
                            - Lấy teacher_id từ Teach_Class với {'class_room_id': data['class_room_id'],
                                                                 'lesson_id': schedule['lesson_id'],
                                                                 'year_id': data['year_id']}

                            - Tiến hành upsert schedule {'lesson_time': schedule['lesson_time'],
                                                         'day_of_week': schedule['day_of_week'],
                                                         'lesson_id': schedule['lesson_id'],
                                                         'period_id': period_id,
                                                         'class_room_id': data['class_room_id'],
                                                         'teacher_id': teacher_id}

                            - Trong trường hợp raise lỗi vì trùng giờ dạy period_id, day_of_week, lesson_time, teacher_id sẽ rollback và phản hồi lỗi 400
                            'môn Sinh tiết 2 thứ 2 bị trùng giờ dạy!'

                    - Backend sẽ trả về với nội dung {'msg': 'Đã thêm thời khóa biểu!'}, 201
                    - Audit_log sau khi thao tác gọi API bị lỗi

                B3: FE sẽ hiện thị thời khóa biểu và msg với nội dung: 'Đã thêm thời khóa biểu!'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 6 bảng schedule, lesson, class_room, year, semester, period, teach_class
                - schedule:
                    - class_room_id: foreign key integer - link với class_room
                    - lesson_id: foreign key integer - link với lesson
                    - period_id: foreign key integer - link với period
                    *** ràng buộc unique với period_id, class_room_id, day_of_week và lesson_time:
                        __table_args__ = (UniqueConstraint('class_room_id', 'period_id', 'day_of_week', 'lesson_time', name = 'unq_cls_period'),
                                          UniqueConstraint('period_id', 'day_of_week', 'lesson_time', 'teacher_id', name = 'unq_tea_per'))

                - lesson:
                    - id: primary key integer
     
                - class_room:
                    - id: primary key integer

                - year:
                    - id: primary key integer
                
                - semester:
                    - id: primary key integer
                
                period:
                    - id: primary key integer
                    - year_id: foreign key integer - link với year
                    - semester_id: foreign key integer - link với semester
                
            #### API Endpoint
                Endpoint name:
                    Create schedule
                Method & URL:
                    POST /api/academic/entity/schedules
                Role:
                    admin
                Body: 
                    {'year_id': 10,
                     'class_room_id': 27,
                     'semester_id': 1,
                     'schedules': {
                        '1': {'1': {'lesson_id': 51}, 
                              '2': {'lesson_id': 47}, 
                              '3': {'lesson_id': 47}, 
                              '4': {'lesson_id': 50},...
                            }
                        }
                    }
                Response:
                    {'msg': 'Đã thêm thời khóa biểu!'}, 201

            #### Validation rule
                Input validation (Pydantic):
                    class RetestScore(BaseModel):
                        student_id: int
                        lessons: Dict[int, 'AcademicUpdateSchemas.RetestScoreItem']
                    
                    class RetestScoreItem(BaseModel):
                        score: float

                        @field_validator('score')
                        def validate_score(cls, v):
                            try:
                                v = float(v)

                            except:
                                raise ValueError('Điểm số phải là số')
                            
                            if v < 0 or v > 10:
                                raise ValueError('Điểm số trong phạm từ 0 đến 10!')

                            return v
                
                Các lỗi thường gặp nếu vi phạm:
                        - pydantic:
                            {'status': 'Validation_error', 'msg': 'Điểm số phải là số!} 422
                            {'status': 'Validation_error', 'msg': 'Điểm số trong phạm từ 0 đến 10!'} 422
                             
                            *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log

    ## Chức năng tạo bảng điểm:
        ### Tạo và điều chỉnh thời khóa biểu:
            Cho phép admin tạo mới bảng điểm cho từng học sinh theo niên khóa, học kỳ và môn học
        
            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'year_id': 1,
                     'semester_id': 1,
                     'semester': 'HKI'}

                B2: Backend:
                    - Check authorization và role (admin)
                    - route tiếp nhận và validate input bằng pydantic
                    - Business Logic Check và lấy period_id từ year_id và semester_id, student_ids, grade từ year_id
                    - Từ mỗi student_id và grade sẽ lấy số lesson_ids tương ứng:
                        - Từ mỗi lesson_id: 
                            - Record vào db student_lesson_period với {'student_id': student_id,
                                                                       'lesson_id': lesson_id,
                                                                       'period_id': period_id} 
                            - Record vào db Score với {'id': student_lesson_period.id}
                    
                    - Backend sẽ trả về với nội dung {'msg': 'Đã tạo bảng điểm cho HKI!'}, 201
                    - Audit_log sau khi thao tác gọi API

                B3: FE sẽ hiện thị thời khóa biểu và msg với nội dung: 'Đã tạo bảng điểm cho HKI!'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 6 bảng student_lesson_period, lesson, student, year, semester, period, score
                - student_lesson_period:
                    - id: primary key integer
                    - lesson_id: foreign key integer - link với lesson
                    - period_id: foreign key integer - link với period 
                    - student_id: foreign key integer - link với student
                        *** ràng buộc unique với period_id, student_id, lesson_id:
                        _table_args__ = (UniqueConstraint('student_id', 'lesson_id', 'period_id', name = 'uq_student_lesson_period'),)

                - lesson:
                    - id: primary key integer

                - student:
                    - id: primary key integer

                - year:
                    - id: primary key integer
                
                - semester:
                    - id: primary key integer
                
                - period:
                    - id: primary key integer
                    - year_id: foreign key integer - link với year
                    - semester_id: foreign key integer - link với semester

                - score:
                    - id: primary key, foreign key integer link với student_lesson_period

            #### API Endpoint
                            Endpoint name:
                                Create score
                            Method & URL:
                                POST api/scores
                            Role:
                                admin
                            Body: 
                                {'year_id': 1,
                                'semester_id': 1,
                                'semester': 'HKI'}
                            Response:
                                {'msg': 'Đã tạo bảng điểm cho HKI!'}, 201

            #### Validation rule
                Input validation (Pydantic):
                    class Scores(Semester):
                        year_id: int

                    class Scores(Semester, SemesterID):
                        pass

                    Business validation:
                        - year_id có tồn tại không?
                        - semester_id có tồn tại không?
                        - semester có hợp lệ không?
                




                