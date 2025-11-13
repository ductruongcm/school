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
                1. Frontend gởi payload với {lesson: 'Toán', grade_id: 1, is_visible: true, is_folder: true, is_schedule: true}
                2. Backend 
                    - Check authorization và role (admin)
                    - Check tên lesson tránh trùng
                    - check grade_id có tồn tại không?
                    - Tạo record mới trong bảng lesson với cái fields: lesson, grade_id
                    - Tạo record mới trong bảng lessontag với các fields: is_visible, is_folder, is_schedule
                3. Backend trả về: : {"data": lesson}
                4. Frontend hiển thị danh sách môn học + khối lớp + is_visible + is_folder + is_schedule và reset form

            #### Cấu trúc dữ liệu:
                Các thành phần chính có liên quan trong 3 bảng lesson, lessontag
                - lesson:
                    - id: primary key integer
                    - lesson: string (VD: 'Toán', 'Lý') - Tên môn học bao gồm cả thư mục cho cloud và tiết học cho thời khóa biểu
                    - grade_id: foreign key integer (VD: 1, 2) - link với bảng grade
                - lessontag:
                    - id: primary key integer
                    - lesson_id: foreign key integer (VD: 1, 2) - link với lesson
                    - is_visible: Boolean (True/False) - Để thể hiện môn học chính có giáo viên cụ thể và điểm số
                    - is_folder: Boolean (True/False) - Để thể hiện là thư mục cho danh sách cloud
                    - is_schedule: Boolean (True/False) - Để thể hiện là tiết học để add cho thời khóa biểu

                # Mối liên kết giữa bảng:
                    grade.id  → lesson.grade_id
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
                    payload = {lesson: 'Toán', grade_id: 1, is_visible: true, is_folder: true, is_schedule: true}
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
                    - Check grade_id có tồn tại không

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
                1. Frontend gởi payload với data đã được sàng lọc thay đổi
                                           {lesson: 'Toán',
                                            lesson_id: 1, 
                                            grade_id: 1, 
                                            year_id: 1, 
                                            is_visible: true, 
                                            is_folder: true, 
                                            is_schedule: true}

                    - kiểm tra lesson_id: nếu không có sẽ raise 404 {'msg': 'Không tìm thấy ID môn học!'}
                    - kiểm tra year_id: nếu không có sẽ raise 404 {'msg': 'Chưa thiết lập niên khóa!'}

                    - Nếu đổi tag: 
                        - is_folder: sẽ chuyển True/Fasle ở cột is_folder của bảng lessontag
                        - is_schedule: sẽ chuyển True/Fasle ở cột is_schedule của bảng lessontag
                        - is_visible: sẽ nằm ở lien kết với grade_id vì còn liên quan đến bảng teach_class

                    - Nếu đổi grade_id:
                        - check grade_id: nếu id ko hợp lệ sẽ raise 400 {'msg': 'Không tìm thấy grade ID!'}
                        - Nếu chỉ đổi grade_id:
                                - is_visible == False: chỉ đổi grade_id trong lesson
                                - is_visible == True: 
                                    - đổi grade_id trong lesson
                                    - xóa tất cả cả row có year_id và lesson_id tương ứng và sau đó add lại đúng với class_room_id từ grade_id và lesson_id, year_id trong teach_class

                        - Nếu chỉ đổi is_visible:
                                - is_visible to True: 
                                    - đổi is_visible thành True trong lessontag
                                    - add class_room_id tương ứng với grade_id và lesson_id, year_id trong teach_class
                                - is_visible to False: 
                                    - đổi is_visible thành False trong lessontag
                                    - Xóa tất cả các row có year_id và lesson_id tương ứng trong teach_class

                        - Đổi grade_id và is_visible:
                                - is_visible từ False sang True: 
                                    - đổi grade_id trong lesson
                                    - đổi is_visible thành True trong lessontag
                                    - add class_room_id tương ứng với grade_id và lesson_id, year_id trong teach_class
                                - is_visible từ True sang False:
                                    - đổi grade_id trong lesson
                                    - đổi is_visible thành False trong lessontag
                                    - xóa tất cả các row có year_id và lesson_id tương ứng trong teach_class
                        
            #### API endpoint:
                gọi với PUT /api/academic/lessons với payload = {lesson_id: 1, lesson: 'Toán', year_id: 1, grade_id: 3, 'is_folder': true, 'is_schedule': true, 'is_visible': true} 
                được response {'msg': 'Đã cập nhật môn học Toán!'} 200

            #### Validation rules: 
                Cũng tương tự tạo môn học nhưng có bổ sung thêm lesson_id
                input validation (Pydantic):
                    LessonUpdate(Lesson)
                        grade_id: int

                Check logic:
                    - lesson: không được trùng tên
                    - Check lesson_id có tồn tại không
                    - Check year_id có tồn tại không
                    - Check grade_id có tồn tại không
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
                    - với teach_class: sau khi check có lỗi, sẽ lấy mỗi teach_class với lesson_id, year_id để query, từ đó sẽ insert teacher.id vào mỗi teach_class.teacher_id tương ứng
                    - Sau khi hoàn tất commit db, thì sẽ gởi 1 email đến email của giáo viên có chứa link trong thời hạn là 7 giờ để vào set new password
                    - Backend sẽ trả về với nội dung {'msg': 'Đã thêm giáo viên Nguyễn Văn Tý'}, 201
                    - Audit_log sau khi thao tác gọi API
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
                     'year_id': 1
                    }
                    (ở đây field class_room, class_room_id, teach_class có thể None) 
                B2: Backend:
                    - Check authorization và role (chỉ quyền admin)
                    - route tiếp nhận và validate input bằng pydantic
                    - Business Logic Check
                    - update vào db theo teacher_id:
                        - trong bảng teacher với {'name': name, 'lesson_id': lesson_id}
                        - trong bảng teach_info với {'tel': tel, 'add': add, 'email': email}
                    - trong trường hợp là giáo viên chủ nhiệm, sau khi check không lỗi sẽ insert teacher.id vào class_room.teacher_id
                    - với teach_class: sau khi check có lỗi, sẽ lấy mỗi teach_class với lesson_id, year_id để query, từ đó sẽ insert teacher.id vào mỗi teach_class.teacher_id tương ứng
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
                     'year_id': 1
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
                     'grade_id': 3,
                     'year_id': 1
                     'year': "2025 - 2026"
                     'gender': 'Nam',
                     'conduct': True,
                     'absent_day': 1,
                     'note': 'Chuyển từ trường ABC'
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
                            'year_id': year_id - 1
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

                    - Record vào bảng student_year_summary ghi lại tổng kết năm trước của học sinh với
                            {'student_id': student_id,
                             'grade_id': grade_id,
                             'year_id': year_id,
                             'conduct': conduct,
                             'absent_day': absent_day,
                             'note': note,
                             'class_room_id': class_room_id
                            }

                        - từ student và year lấy tất cả điểm TB của năm trước, theo điểm số mà xếp loại:
                            if all(score >= 6.5 for score in lesson_avgs) and sum(1 for score in lesson_avgs if score >= 8) >= 6:
                                learning_status = 'Tốt'
                                
                            elif all(score >= 5 for score in lesson_avgs) and sum(1 for score in lesson_avgs if score >= 6.5) >= 6:
                                learning_status = 'Khá'

                            elif all(score >= 3.5 for score in lesson_avgs) and sum(1 for score in lesson_avgs if score < 5) <= 1 and sum(1 for score in lesson_avgs if score >= 5) >= 6:
                                learning_status = 'Trung bình'

                            elif sum(1 for score in lesson_avgs if score < 5) >= 3 or sum(1 for score in lesson_avgs if score < 3.5) >= 1:
                                learning_status = 'Không đạt'

                    - Backend sẽ trả về với nội dung {'msg': 'Đã thêm học sinh Lê Văn Tèo vào hệ thống'}, 201
                    - Audit_log sau khi thao tác gọi API

                B3: FE sẽ hiện thị thông tin với nội dung: 'Đã thêm học sinh Lê Văn Tèo vào hệ thống'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 9 bảng users, students, student_info, year, grade, period, student_lesson_period, student_lesson_annual, student_year_summary
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

                - student_year_summary:
                    - student_id: foreign key integer - link với student
                    - year_id: foreign key integer - link year
                    - grade_id: foreign key integer - link grade
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
                     'grade_id': 3,
                     'year_id': 1
                     'year': "2025 - 2026"
                     'gender': 'Nam',
                     'conduct': True,
                     'absent_day': 1,
                     'note': 'Chuyển từ trường ABC'
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
                        grade_id: int
                        conduct: bool
                        lesson: List['StudentSchemas.StudentItem']
                        note: str
                        absent_day: Optional[int]
                        
                        @field_validator('grade_id', mode='before')
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
                        - grade_id có hợp lệ không?
                        - class_room_id có hợp lệ không?
                
                Các lỗi thường gặp nếu vi phạm:
                        - pydantic:
                            {'status': 'Validation_error', 'msg': 'Họ và tên không được chứa số và ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Số điện thoại chỉ được chứa 10 chữ số'} 422
                            {'status': 'Validation_error', 'msg': 'Địa chỉ không được chứa ký tự đặc biệt!'} 422
                            {'status': 'Validation_error', 'msg': 'Chưa nhập thông tin khối lớp'} 422
                             
                            *** Tất cả các lỗi raise sẽ kèm rollback db và audit_log


        ### Xếp lớp cho học sinh:
            Cho phép admin xếp lớp cho học sinh sau khi được xét duyệt

            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'year_id': 2, 
                    'semester_id': 1, 
                    'student_assign_list': [{'class_room_id': 14, 'student_id': 139},
                                            {'class_room_id': 15, 'student_id': 141}]
                    }
                
                B2: Backend:
                    - Check authorization, role (admin) 
                    - route tiếp nhận và validate input bằng pydantic, và lấy user_id
                    - Business check logic (year_id, semester_id) từ đó lấy period_id 
                    - Vào vòng lặp để add cho từng học sinh:
                        - Business check logic (class_room_id)
                        - Get student và grade_id
                        - Bật True cho assign_status cho student_id và year_id -1 ở bảng student_ year_summary
                        - Insert dòng mới ở bảng student_year_summary với student_id, year_id, grade_id, class_room_id
                        - Lấy tất cả các id của các môn học theo grade_id
                        - Tạo liên kết học sinh và môn học theo học kỳ 1 cho năm mới
                        - Ghi lại kết quả thành công của thao tác vào bảng activity log

                B3: FE sẽ hiện thị thông tin với nội dung: 'Đã hoàn thành xếp lớp cho học sinh!' 

            #### Cấu trúc dữ liệu:
                Các thành phần chính có liên quan trong 6 bảng student, lesson, class_room, year, semester, period, student_year_summary, student_lesson_period
                    - student_year_summary:
                        - student_id: foreign key integer - link với student
                        - year_id: foreign key integer - link với year 
                        - grade_id: foreign key integer - link với grade
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
                    {'year_id': 2, 
                    'semester_id': 1, 
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

    ## Chức năng thời khóa biểu:
        ### Tạo và điều chỉnh thời khóa biểu:
            Cho phép admin tạo mới và điều chỉnh thời khóa biểu cho mỗi lớp theo từng học kỳ và niên khóa
        
            #### Luồng hoạt động
                B1: FE truyền dữ liệu gồm:
                    {'year_id': 1,
                     'class_room_id': 2,
                     'semester_id': 1,
                     'schedules': [{
                        'day_of_week': 1,
                        'lesson_time': 1,
                        'lesson_id': 10
                     }, {
                        'day_of_week': 1,
                        'lesson_time': 2,
                        'lesson_id': 3
                     }, {
                        ...
                     }...
                    ]}

                B2: Backend:
                    - Check authorization và role (admin và Teacher)
                    - route tiếp nhận và validate input bằng pydantic
                    - Business Logic Check và lấy period_id từ year_id và semester_id
                    - Trong trường hợp:
                        - Chưa có db: record vào bảng Schedule với {'period_id': period_id,
                                                                    'class_room_id': class_room_id,
                                                                    'day_of_week': day_of_week,
                                                                    'lesson_time': lesson_time,
                                                                    'lesson_id': lesson_id
                                                                    }

                        - Đã có db: 
                            - thay đổi lesson_id bằng 1 lesson_id mới chỉ cập nhật giá trị mới
                            - bỏ lesson_id sẽ xóa row đó
                            - không thay đổi gì sẽ ko làm gì

                    - Backend sẽ trả về với nội dung {'msg': 'Đã thêm thời khóa biểu HKI của lớp 10B!'}, 201
                    - Audit_log sau khi thao tác gọi API

                B3: FE sẽ hiện thị thời khóa biểu và msg với nội dung: 'Đã thêm thời khóa biểu HKI của lớp 10B!'

            #### Cấu trúc dữ liệu
                Các thành phần chính có liên quan trong 6 bảng schedule, lesson, class_room, year, semester, period
                - schedule:
                    - class_room_id: foreign key integer - link với class_room
                    - lesson_id: foreign key integer - link với lesson
                    - period_id: foreign key integer - link với period
                    *** ràng buộc unique với period_id, class_room_id, day_of_week và lesson_time:
                        __table_args__ = (UniqueConstraint('class_room_id', 'period_id', 'day_of_week', 'lesson_time', name = 'unq_cls_period'),)

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
                    POST api/academic/schedules
                Role:
                    admin
                Body: 
                    {'year_id': 1,
                     'class_room_id': 2,
                     'semester_id': 1,
                     'schedules': [{
                        'day_of_week': 1,
                        'lesson_time': 1,
                        'lesson_id': 10
                     }, {
                        'day_of_week': 1,
                        'lesson_time': 2,
                        'lesson_id': 3
                     }, {
                        ...
                     }...
                    ]}
                Response:
                    {'msg': 'Đã thêm thời khóa biểu HKI của lớp 10B!'}, 201

            #### Validation rule
                Input validation (Pydantic):
                    class ScheduleItem(BaseModel):
                        day_of_week: int
                        lesson_time: int
                        lesson_id: Optional[int] = None

                    class Schedule(YearID, SemesterID):
                        class_room_id: int
                        schedules: List["AcademicSchemas.ScheduleItem"]

                        @model_validator(mode='after')
                        def check_at_least_one_selected(self):
                            if all(item.lesson_id is None for item in self.schedules):
                                raise ValueError('Chưa có dữ liệu tiết học!')
                            return self

                    Business validation:
                        - year_id có tồn tại không?
                        - semester_id có tồn tại không?
                        - class_room_id có hợp lệ không?
                
                Các lỗi thường gặp nếu vi phạm:
                        - pydantic:
                            {'status': 'Validation_error', 'msg': 'Chưa có dữ liệu tiết học!} 422
                            {'status': 'Validation_error', 'msg': 'Chưa nhập thông tin khối lớp'} 422
                             
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
                    - Business Logic Check và lấy period_id từ year_id và semester_id, student_ids, grade_id từ year_id
                    - Từ mỗi student_id và grade_id sẽ lấy số lesson_ids tương ứng:
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
                




                