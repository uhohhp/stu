from sqlalchemy import Column, Integer, String, Text, create_engine, MetaData, Table
from sqlalchemy.orm import registry
from sqlalchemy.exc import OperationalError
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)
mapper_registry = registry()
metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('tg_id', Integer, unique=True, nullable=False),
    Column('created_at', String)
)

lectures = Table(
    'lectures', metadata,
    Column('id', Integer, primary_key=True),
    Column('topic', String(128)),
    Column('name', String(256)),
    Column('drive_audio_id', String(256)),
    Column('drive_slides_id', String(256)),
    Column('summary_text', Text)
)


def init_db():
    try:
        metadata.create_all(engine)
    except OperationalError as e:
        print('DB init error:', e)


# helper для работы с сессией
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

def get_db_session():
    return Session()