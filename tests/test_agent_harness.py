import os
import sys
import json
import re
import pytest

# Add paths
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent_core"))
from langgraph_agent import app

def load_golden_dataset():
    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.mark.parametrize("item", load_golden_dataset())
def test_agent_intent_routing_and_emoji_rule(item):
    """Kiểm thử tự động LangGraph Agent với Golden Dataset:
    1. Tỷ lệ chính xác của Tool / Intent Routing.
    2. Quy tắc nghiêm ngặt: Tuyệt đối KHÔNG chứa Emoji trong câu trả lời cuối cùng.
    """
    question = item["question"]
    expected_intent = item["expected_intent"]
    
    # Run Agent
    initial_state = {"query": question, "trace_log": []}
    result = app.invoke(initial_state)
    
    # 1. Check Intent Accuracy
    actual_intent = result.get("intent")
    assert actual_intent == expected_intent, f"Intent sai! Kỳ vọng: {expected_intent}, Thực tế: {actual_intent}"
    
    # 2. Strict Emoji Check (Regex check all Unicode Emoji ranges)
    final_answer = result.get("final_answer", "")
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    
    found_emojis = emoji_pattern.findall(final_answer)
    assert len(found_emojis) == 0, f"Phát hiện Emoji vi phạm quy tắc nghiêm ngặt của hệ thống: {found_emojis}"
