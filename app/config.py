import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    embedding_provider: str = field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "local"))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    chroma_dir: str = field(default_factory=lambda: os.getenv("CHROMA_DIR", "./chroma_db"))
    collection_name: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION", "support_docs"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "600"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "80"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    fetch_k: int = int(os.getenv("FETCH_K", "12"))
    escalation_threshold: float = float(os.getenv("ESCALATION_THRESHOLD", "0.62"))
    offline_escalation_threshold: float = float(os.getenv("OFFLINE_ESCALATION_THRESHOLD", "0.2"))
    use_hybrid: bool = os.getenv("USE_HYBRID", "1") == "1"


settings = Settings()