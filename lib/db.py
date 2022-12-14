import redis
from models.settings import Settings


settings = Settings()

redis_db = redis.from_url(settings.db_url, decode_responses= True, username  = settings.db_username, password = settings.db_password)