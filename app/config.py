import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AgriVoice"
    debug: bool = True
    
    # Models
    hf_token: str = os.getenv("HF_TOKEN", "")
    llm_model: str = "NCAIR1/N-ATLaS"
    asr_hausa: str = "NCAIR1/Hausa-ASR"
    asr_yoruba: str = "NCAIR1/Yoruba-ASR"
    asr_igbo: str = "NCAIR1/Igbo-ASR"
    asr_english: str = "NCAIR1/NigerianAccentedEnglish"
    
    # RAG
    knowledge_dir: str = "data/knowledge"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # LLM Backend: 'ollama', 'transformers', or 'api' (remote N-ATLAS server)
    llm_backend: str = os.getenv("LLM_BACKEND", "ollama")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Remote API backend (for Colab/Kaggle deployment)
    natlas_api_url: str = os.getenv("NATLAS_API_URL", "")  # e.g. https://xxxx.ngrok-free.app
    
    # WhatsApp
    whatsapp_verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "agrivoice_secret_token")
    whatsapp_api_token: str = os.getenv("WHATSAPP_API_TOKEN", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
