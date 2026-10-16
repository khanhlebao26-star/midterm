# Báo cáo quản lý: FreshRetailNet

## Tóm tắt điều hành

**Track được chọn: A – Tối ưu tồn kho.** Câu hỏi quản lý là: sản phẩm nào tại cửa hàng nào nên được ưu tiên bổ sung hàng trong tháng tới? Phân tích cho thấy 44,27% quan sát sản phẩm–cửa hàng–ngày có ít nhất một giờ hết hàng. Khuyến nghị là thực hiện **một pilot bổ sung hàng có theo dõi**, bắt đầu xem xét Product 224 tại City 11, Store 602; xác nhận tồn kho hiện tại và lead time trước khi hành động. Hai cặp Product 267 có tín hiệu hết hàng cao nhưng cần xác minh doanh số bất thường trước khi đưa vào pilot.

## 1. Bài toán kinh doanh và phạm vi

`FreshRetailNet` gồm 4,5 triệu quan sát sản phẩm–cửa hàng–thành phố–ngày, từ 28/03/2024 đến 25/06/2024. `sale_amount` phản ánh doanh số quan sát đã chuẩn hóa, không nhất thiết là doanh thu tiền tệ. Khi sản phẩm hết hàng, doanh số ghi nhận có thể bị giới hạn bởi khả năng cung ứng và không đại diện đầy đủ cho nhu cầu thực.

## 2. Hiểu dữ liệu và chất lượng dữ liệu

Không phát hiện giá trị thiếu trong các cột scalar đã kiểm tra, danh sách giờ rỗng, khóa sản phẩm–cửa hàng–ngày trùng hoặc ngày không hợp lệ. Trạng thái tồn kho có 24 giá trị nhị phân trên mỗi dòng; số trạng thái hết hàng ở các slot [6:22] khớp `stock_hour6_22_cnt` trên cả 4,5 triệu dòng. Có 34 giá trị discount ngoài [0, 1]; giữ và đánh dấu, không dùng trong so sánh discount. Các điểm IQR được giữ lại vì điểm cực trị thống kê chưa chắc là lỗi. Chi tiết phép kiểm tra và biến dẫn xuất nằm trong [Ghi chú chuẩn bị dữ liệu](Data_Preparation_Notes_VI.md).

## 3. Hiệu suất bán hàng và rủi ro hết hàng

| KPI | Kết quả |
|---|---:|
| Tổng `sale_amount` | 4.493.660,787 |
| Doanh số trung bình mỗi ngày | 49.929,564 |
| Cửa hàng / sản phẩm / thành phố | 898 / 865 / 18 |
| Quan sát có ít nhất một giờ hết hàng | 44,27% |
| Tỷ lệ giờ hết hàng trên 16 slot vận hành | 19,88% |
| Thời lượng hết hàng trung bình trong các dòng có hết hàng | 7,18 giờ |
| Discount trung bình hợp lệ | 8,89% |

Hai cách tính tồn kho có mẫu số khác nhau: 44,27% là tỷ lệ dòng sản phẩm–cửa hàng–ngày có bất kỳ stockout nào; 19,88% là tỷ lệ giờ hết hàng trên tổng 16 slot vận hành của toàn bộ dòng.

### Top 10 sản phẩm theo tổng doanh số quan sát

| Hạng | Product ID | Tổng `sale_amount` | Số quan sát |
|---:|---:|---:|---:|
| 1 | 267 | 183.395,100 | 11.790 |
| 2 | 4 | 183.265,300 | 70.470 |
| 3 | 300 | 154.505,577 | 37.080 |
| 4 | 117 | 150.032,945 | 41.310 |
| 5 | 215 | 144.031,118 | 55.260 |
| 6 | 70 | 120.042,148 | 33.390 |
| 7 | 580 | 117.250,900 | 66.150 |
| 8 | 834 | 87.215,500 | 66.690 |
| 9 | 691 | 66.486,590 | 17.280 |
| 10 | 191 | 66.122,317 | 32.130 |

Product 267 và Product 4 có tổng bán gần nhau nhưng số quan sát khác đáng kể; do đó không nên dùng tổng doanh số riêng lẻ để kết luận về hiệu quả hoặc mức cần bổ sung.

### So sánh các nhóm thời gian và trạng thái tồn kho

| So sánh | Doanh số trung bình mỗi quan sát |
|---|---:|
| Ngày thường / cuối tuần | 0,921 / 1,189 |
| Không lễ / ngày lễ | 0,914 / 1,160 |
| Bình thường / activity | 0,990 / 1,013 |
| Không stockout / có stockout | 0,975 / 1,029 |

Các quan sát có stockout cũng có discount trung bình cao hơn (9,43% so với 8,46%) và activity rate cao hơn (39,75% so với 36,33%). Đây là các mối liên hệ quan sát được, không chứng minh nguyên nhân.

## 4. Khuyến mãi và yếu tố bối cảnh

Discount được chia theo các ngưỡng diễn giải: 0%, trên 0–10%, trên 10–30%, và trên 30–100%. Nhóm trên 30% có doanh số trung bình 2,064 và stockout rate 46,85%, so với 0,833 và 43,03% ở nhóm không giảm giá. Chênh lệch stockout là +3,82 điểm phần trăm. Doanh số không tăng đều qua mọi nhóm discount; thành phần sản phẩm, activity, ngày lễ và mức sẵn có có thể cùng ảnh hưởng.

Activity có doanh số trung bình cao hơn bình thường tại 9/18 thành phố và thấp hơn tại 9 thành phố còn lại. Mức thay đổi dao động từ +18,34% ở City 12 đến -36,78% ở City 4. Vì hướng liên hệ không đồng nhất, không nên áp dụng một chính sách activity chung cho mọi thành phố. Tương quan không chứng minh activity hoặc discount gây ra doanh số hay stockout.

## 5. Câu hỏi phân tích riêng

**Cuối tuần có quan trọng như nhau ở mọi thành phố nếu xét cả doanh số và stockout không?** Doanh số trung bình cuối tuần cao hơn ngày thường ở cả 18 thành phố, mức tăng 23,76%–40,39%. Tuy nhiên, tỷ lệ stockout cuối tuần tăng ở 11 thành phố và giảm ở 7. Mức tăng lớn nhất là City 7 (+7,80 điểm phần trăm), kế đến City 13 (+7,47 điểm phần trăm). Điều này gợi ý kiểm tra kế hoạch cuối tuần theo địa điểm, nhưng chưa chỉ ra sản phẩm cụ thể nào cần thêm hàng.

## 6. Bằng chứng từ dashboard

Dashboard Python có ba trang: **Executive Overview** (KPI, xu hướng ngày, so sánh thành phố/cửa hàng), **Inventory Risk** (scatter doanh số–stockout, sản phẩm ưu tiên, cửa hàng rủi ro) và **Decision Driver** (nhóm discount, activity theo thành phố). Bộ lọc ngày/thành phố và thông tin hover hỗ trợ so sánh động. Hai bằng chứng trực quan quan trọng cho quyết định là scatter sản phẩm theo doanh số–stockout và biểu đồ thay đổi stockout cuối tuần theo thành phố. Trước khi xuất báo cáo PDF, nên chèn ảnh chụp hai biểu đồ này kèm chú thích ngắn từ dashboard.

## 7. Quyết định quản lý và giới hạn

Phân loại 50.000 cặp sản phẩm–cửa hàng có ít nhất 60 quan sát bằng median cấp cặp (doanh số trung bình 0,658; stockout 42,22%); 14.132 cặp thuộc nhóm High Sales + High Stockout. Ba cặp đứng đầu theo tiêu chí đã chọn đều có 100% stockout trong 90 quan sát: Product 267–City 4–Store 11 (doanh số trung bình 17,891; 8,211 giờ hết hàng trung bình trên ngày có stockout), Product 267–City 11–Store 505 (16,652; 8,067 giờ), và Product 224–City 11–Store 602 (1,304; 4,156 giờ).

**Quyết định:** triển khai một pilot replenishment có theo dõi, bắt đầu với Product 224 tại City 11, Store 602 sau khi kiểm tra tồn kho hiện tại và lead time. Trước khi đưa hai cặp Product 267 vào pilot, hãy kiểm tra dữ liệu nguồn và ý nghĩa kinh doanh của doanh số cao. Phân tích IQR ở cấp dòng đánh dấu nhiều giá trị `sale_amount` trên 2,150; điều đó không chứng minh các cặp Product 267 sai, nhưng làm tăng nhu cầu xác minh. Theo dõi stockout rate, thời lượng stockout và doanh số quan sát trước/sau pilot.

Kết quả là phân tích mô tả, không đo trực tiếp nhu cầu bị mất hay số lượng hàng tối ưu. Stockout có thể làm doanh số quan sát thấp hơn nhu cầu thực. Ngưỡng median và mức tối thiểu 60 quan sát chỉ dùng để xếp hạng tương đối, không phải chính sách reorder. Dữ liệu không gồm chi phí tồn kho, biên lợi nhuận hoặc lead time nhà cung cấp; vì vậy stockout cao chưa đủ để chứng minh tăng tồn kho là quyết định có lợi nhất.

## 8. Phân khúc sản phẩm (phân tích mở rộng)

Phân khúc theo median doanh số, stockout, discount và Sales CV xác định 203 sản phẩm ưu tiên replenishment, 107 sản phẩm cần xem xét discount cùng stockout, và 27 sản phẩm có biến động cao kèm stockout. Đây là nhóm tương đối trong bộ dữ liệu; cần xem xét theo cửa hàng và xác minh điều kiện vận hành trước khi chuyển thành chính sách.

---

**Tài liệu phân tích:** [Notebook](analysis/StudentID_Analysis.ipynb) · [Dashboard Python](dashboard/dashboard.py) · [Ghi chú chuẩn bị dữ liệu](Data_Preparation_Notes_VI.md)
