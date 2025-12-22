1. Tổng quan kiến trúc
    Client (Vue) => Flask API (Route) => Service layer (Business Logic) => Repository layer (SQL/ORM) -> PostgreSQL

2. Kiến trúc Route – Service – Repository
    Route chỉ chứa:
        - Auth & Role
        - Validate input
        - Chuyển input vào đúng Service hoặc workflow nếu liên quan đến nhiều Service
        - Nhận kết quả và phản hồi
        Route là nơi tiếp nhận request, validate, authorize và điều phối (orchestrate) các service để thực thi tác vụ.

    Service chỉ chứa:
        - Xử lý nghiệp vụ logic 
        - Đảm bảo transaction
        Business rule chỉ tồn tại ở service layer, giúp tách bạch, dễ test, mở rộng và tránh phân tán, 
        Business rộng, nhiều nghiệp vụ liên đới được tập trung tại workflow nhằm giảm độ phức tạp không cần thiết ở các business riêng lẻ 

    Repository chỉ chứa:
        - thuần SQL
        - set-based query, tránh loop python

3. Transaction & Data Integrity Strategy
    - Mọi nghiệp vụ ghi DB đều phải chạy trong transaction
    - Một khi có phát sinh bất kỳ:
        - validation lỗi
        - business logic lỗi
        - db constraint lỗi
        ...
        tất cả đều phải rollback toàn bộ 

4. sử dụng set-based query, tránh loop python
    Đây là một tính năng hay cực mạnh của postgreSQL: trực tiếp, từ SQL có thể đưa về đúng dạng chuẩn cho FE render ma trận mà không cần phải xử lý bằng python làm chậm hệ thống, dễ lỗi
    Cho nên tận dụng tối đa tính năng nhiều nhất có thể
    Trong trường hợp cần có logic phức tạp để xử lý nhưng xếp loại học sinh thì mới nên để python xử lý
    Các nghiệp vụ tổng kết được thiết kế idempotent, có thể chạy lại nhiều lần mà không gây trùng dữ liệu.

5. Authorization & Role Design
    JWT dùng ở đây nhằm quản lý đăng nhập bằng access token ngắn hạn và refresh token dài hạn hơn, nhằm đảm bảo an toàn và duy trì trải nghiệm liên tục của người dùng
    Backend sử dụng JWT (access + refresh token). Thông tin role được nhúng trong access token để backend kiểm soát quyền, FE chỉ sử dụng role này để render UI, không quyết định quyền truy cập.
    Mỗi request thì role được lấy từ JWT để đảm bảo tính an toàn và check trước khi validate data bằng Pydantic

6. Audit log và Activity log
    Audit log được gọi để ghi vào lịch sử khi phát sinh lỗi trong những tác vụ quan trọng 
    Activity log được gọi để ghi vào lịch sử hoạt động khi thao tác thành công trong những tác vụ quan trọng

    ở Audit log chỉ có admin được xem để theo dõi và quản lý để biết được thao tác nào gây ra sự cố và ai là người thao tác
    ở Activity log người dùng có thể xem lại lịch sử hoạt động của chính mình, để biết những thao tác của mình trong quá khứ; admin có thể xem tất cả

7. Trade-offs & Limitations
    - Chỉ đang tập trung cho cấp 3 Trung học phổ thông
    - Chưa scale liên trường
    - Chưa có thông báo tực thời mỗi khi có cập nhật như điểm số
    - Chỉ có quản lý học vụ, chưa có thông tin, sự kiện, hình ảnh hoạt động của trường


