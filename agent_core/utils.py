import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import logging

logging.getLogger("google.genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

load_dotenv()

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Thiếu biến môi trường GEMINI_API_KEY. Vui lòng thiết lập API Key để kết nối Gemini.")
    return genai.Client(api_key=api_key)

def get_safety_settings():
    return [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
    ]

def get_qdrant_client():
    return QdrantClient(host="localhost", port=6333)

from langfuse.decorators import observe, langfuse_context

@observe(as_type="generation")
def generate_llm_content(client, model, contents, config, step_name="llm_generation", metadata=None):
    """
    Wrapper gọi Gemini API và tự động bắt Token Usage đẩy lên Langfuse.
    """
    if metadata:
        langfuse_context.update_current_observation(metadata=metadata)
        
    langfuse_context.update_current_observation(
        name=step_name,
        model=model,
        input=contents
    )
        
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )
    
    # Báo cáo Usage nếu có
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        langfuse_context.update_current_observation(
            usage={
                "input": response.usage_metadata.prompt_token_count,
                "output": response.usage_metadata.candidates_token_count
            }
        )
    
    # Thêm output để theo dõi
    langfuse_context.update_current_observation(output=response.text)
        
    return response
