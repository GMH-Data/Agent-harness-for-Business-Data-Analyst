# Cập nhật luồng Report Flow (Luồng 2) với Multi-subtask Loop

Bản vẽ dưới đây mô tả chính xác luồng chạy mới nhất của **Report Flow** (Sau khi cập nhật chức năng tách tự động nhiều subtask và vòng lặp phân tích).

## 1. Biểu đồ luồng (StateGraph)

```mermaid
stateDiagram-v2
    direction TB
    
    User([User Prompt]) --> Router: Bắt đầu
    
    state "Phase 1: Lên Kế Hoạch (Planning)" as Planning {
        Router --> Planner: Route to Report Flow
        Planner --> Plan_HITL: Tạo JSON Subtasks (Macro -> Drill-down -> Micro)
    }

    state "Phase 2: Vòng Lặp Trích Xuất Dữ Liệu & Biểu Đồ (Automated Loop)" as Execution {
        Plan_HITL --> Supervisor: Approve (Bắt đầu chạy)
        
        Supervisor --> SQL_Extractor: Dispatch Subtask [i] (Nếu còn task)
        SQL_Extractor --> Chart_Visualizer: Rút trích data thành công
        Chart_Visualizer --> Supervisor: Vẽ biểu đồ & Tự động tăng index (i++)
        
        note right of SQL_Extractor: Tích luỹ Data vào "accumulated_data"
        note right of Chart_Visualizer: Tích luỹ Chart vào "accumulated_charts"
    }

    state "Phase 3: Tổng Hợp & Đánh Giá (Synthesis & QA)" as Synthesis {
        Supervisor --> Analyst_P2: Khi đã hết Subtasks
        Analyst_P2 --> QA_Agent: Tổng hợp thành Final Draft Report
        QA_Agent --> QA_HITL: Đánh giá độ chính xác (MECE)
    }
    
    QA_HITL --> Report_HITL: Approve
    QA_HITL --> Cleanup: Reject (Bỏ qua báo cáo)
    
    Report_HITL --> Cleanup: Hoàn thành / Đóng
    Report_HITL --> Supervisor: (Tuỳ chọn) Chạy thêm task mới bổ sung
    
    Cleanup --> Done([End])
```

## 2. Giải thích chi tiết sự thay đổi

### Sự khác biệt so với phiên bản cũ (One-shot):
- **Bản cũ:** Planner tạo ra duy nhất 1 task ➡️ SQL lấy 1 data ➡️ Chart vẽ 1 hình ➡️ Analyst viết 1 báo cáo ➡️ QA đánh giá. Nếu thiếu ý, QA sẽ tạo thêm 1 task mới và lặp lại cực kỳ chậm và tốn bước HITL.
- **Bản mới:** Planner phân tích toàn cảnh và tạo ra **SẴN 1 danh sách nhiều Subtask** (Ví dụ: Task 1: Data tổng quan, Task 2: Data phân bổ, Task 3: Data chi tiết). 
  - Sau đó, hệ thống bước vào vòng lặp **Supervisor ➡️ SQL ➡️ Chart ➡️ Supervisor**. 
  - Vòng lặp này chạy ngầm và tự động trích xuất toàn bộ dữ liệu, tạo nhiều biểu đồ.
  - Mỗi khi một biểu đồ được vẽ xong (Chart_Visualizer), UI frontend sẽ stream và render ngay biểu đồ đó lên giao diện cho User xem trước.
  - Khi vòng lặp hoàn thành tất cả Subtask, **Analyst P2** mới xuất hiện, đọc TẤT CẢ data được gom lại và viết một Báo cáo phân tích (Markdown) tổng hợp hoàn hảo nhất.

### Lợi ích:
- **Tốc độ:** Các agent không phải hội ý sau mỗi một tác vụ nhỏ.
- **Trải nghiệm UI:** Người dùng thấy biểu đồ được render liên tục từng khối một (Stream từng node).
- **Chất lượng báo cáo:** Analyst có cái nhìn toàn cảnh (Macro, Drill-down, Micro) để đưa ra Business Intelligence tốt hơn.
