import os

# --- LLM 模型配置 ---
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "deepseek-chat")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "qwen-turbo")
PRIMARY_API_KEY = os.getenv("PRIMARY_API_KEY", "")
FALLBACK_API_KEY = os.getenv("FALLBACK_API_KEY", "")
PRIMARY_BASE_URL = os.getenv("PRIMARY_BASE_URL", "https://api.deepseek.com/v1")
FALLBACK_BASE_URL = os.getenv("FALLBACK_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# --- Chroma 配置 ---
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "resume_data")

# --- 检索配置 ---
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
