# Ghi chú chuẩn bị dữ liệu

**Dữ liệu:** `train.parquet`, 4.500.000 dòng, 19 cột, từ 28/03/2024 đến 25/06/2024; mỗi dòng là một quan sát sản phẩm–cửa hàng–thành phố–ngày. File gốc được giữ nguyên; biến mới lưu ở `data/processed/train_prepared.parquet`.

| Kiểm tra | Kết quả | Xử lý và lý do |
|---|---|---|
| Thiếu/empty | 0 thiếu trong scalar đã kiểm tra; 0 list giờ rỗng | Giữ; không cần nội suy. |
| Trùng khóa | 0 trùng theo city/store/product/date | Giữ; đây là grain sản phẩm–cửa hàng–ngày. |
| Ngày | 0 ngày không hợp lệ | Giữ; không cần loại dòng. |
| Discount | 34 dòng ngoài [0, 1], max 1.088 | Giữ nguồn, đánh dấu; `discount = 1` là không giảm. Tạo `DiscountPercent = (1 - discount) × 100`; chỉ so sánh giá trị hợp lệ. |
| Thời tiết | Không phát hiện mưa/gió âm hoặc độ ẩm ngoài [0, 100]; nhiệt độ 12.06–30.88 | Giữ; cực trị thống kê không tự động là lỗi. |
| IQR 1.5× | Trên fence: sale 395.451 (>2.150), mưa 441.643 (>9.061), gió 69.942 (>2.700); nhiệt độ 0. Độ ẩm: 245.388 dưới 57.985, 3 trên 94.345 | Đánh dấu, giữ nguyên. IQR báo điểm xa phân phối, không xác nhận lỗi. |
| Trạng thái tồn kho | 4.500.000 dòng có 24 giá trị nhị phân; 0 mismatch ở slot [6:22] | Giữ. Quy ước 1 = hết hàng, 0 = còn hàng được suy ra từ đối chiếu với số giờ hết hàng. |

**Biến tạo thêm:** `HasStockout`, `StockoutRate` (giờ hết hàng / 16 giờ), `DiscountOutOfRange`, `DiscountPercent`, `DayOfWeek`, `WeekendFlag`.

**Giả định:** `StockoutRate = stock_hour6_22_cnt / 16`, dùng slot [6:22]; IQR là sàng lọc cấp dòng; thời tiết có thể lặp giữa các quan sát. `sale_amount` đã chuẩn hóa, không nhất thiết là tiền. Doanh số quan sát có thể thấp hơn nhu cầu khi hết hàng. Không xóa dữ liệu gốc; discount lỗi và cực trị được giữ/đánh dấu.
