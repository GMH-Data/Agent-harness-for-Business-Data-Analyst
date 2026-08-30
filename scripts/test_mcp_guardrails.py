import unittest
import os
import sys

# Thêm thư mục mcp vào python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp"))

from bigquery_mcp_server import query_bigquery

class TestBigQueryMCPGuardrails(unittest.TestCase):
    
    def test_block_unfiltered_query(self):
        # Trường hợp truy vấn bảng log lớn nhưng KHÔNG có điều kiện lọc
        sql = "SELECT * FROM laplaptech_marketing.fct_user_event_tracking LIMIT 10"
        result = query_bigquery(sql)
        self.assertIn("ERROR", result)
        self.assertIn("thiếu bộ lọc tối ưu", result)
        print("Test block unfiltered query: PASSED")

    def test_allow_filtered_query(self):
        # Trường hợp truy vấn có lọc ngày
        sql = "SELECT * FROM laplaptech_marketing.fct_user_event_tracking WHERE event_date = '2026-08-21' LIMIT 10"
        result = query_bigquery(sql)
        # Vì key credentials thật có thể chưa được verify ở đây hoặc không có record, 
        # nhưng logic guardrails phải CHO PHÉP (không bị trả về lỗi "ERROR... thiếu bộ lọc")
        self.assertNotIn("ERROR: Lệnh SQL truy vấn bảng log lớn", result)
        print("Test allow filtered query: PASSED")

if __name__ == "__main__":
    unittest.main()
