import os

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    DATA_INGESTION_SERVICE_URL = os.getenv("DATA_INGESTION_SERVICE_URL", "http://0.0.0.0:8001")
    DATA_STORAGE_QUERY_SERVICE_URL = os.getenv("DATA_STORAGE_QUERY_SERVICE_URL", "http://0.0.0.0:8000")