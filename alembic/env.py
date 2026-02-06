from alembic import context
from backend.database import Base
from backend.models import *

target_metadata = Base.metadata

def run_migrations_online():
    from sqlalchemy import create_engine
    from backend.config import get_settings
    engine = create_engine(get_settings().database_url_sync)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
