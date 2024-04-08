from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./music_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class MBTIMusic(Base):
    __tablename__ = "mbti_music"

    id = Column(Integer, primary_key=True, index=True)
    mbti = Column(String, unique=True, index=True)
    song_title = Column(String, index=True)
    artist = Column(String)
    score = Column(Integer)
