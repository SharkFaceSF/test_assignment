from src import config
from src.config import settings
from src.models.base import Base


target_metadata = Base.metadata


config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
