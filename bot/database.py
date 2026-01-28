import asyncio
import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Text, text
import aiosqlite

from bot.config import config

# Исправляем URL для SQLite
if config.DATABASE_URL.startswith('sqlite'):
    # Убираем "sqlite:///" и добавляем "sqlite+aiosqlite:///"
    db_url = config.DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
else:
    db_url = config.DATABASE_URL

engine = create_async_engine(db_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

class Game(Base):
    __tablename__ = 'games'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(300), nullable=False)
    author: Mapped[str] = mapped_column(String(100))
    size: Mapped[str] = mapped_column(String(50))
    seeds: Mapped[int] = mapped_column(Integer, default=0)
    leeches: Mapped[int] = mapped_column(Integer, default=0)
    replies: Mapped[int] = mapped_column(Integer, default=0)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    last_post_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    created_date: Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False
    )
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Дополнительная информация
    genre: Mapped[str] = mapped_column(String(200), nullable=True)
    languages: Mapped[str] = mapped_column(String(300), nullable=True)
    version: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

class Settings(Base):
    __tablename__ = 'settings'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Инициализация настроек
    async with async_session() as session:
        # Проверяем, существует ли уже запись с помощью text()
        result = await session.execute(
            text("SELECT COUNT(*) FROM settings WHERE key = 'last_topic_id'")
        )
        count = result.scalar()
        
        if count == 0:
            # Сохраняем последний проверенный topic_id
            last_topic = Settings(key='last_topic_id', value='0')
            session.add(last_topic)
            await session.commit()
        
        # Проверяем запись для last_check
        result = await session.execute(
            text("SELECT COUNT(*) FROM settings WHERE key = 'last_check'")
        )
        count = result.scalar()
        
        if count == 0:
            last_check = Settings(key='last_check', value=datetime.datetime.utcnow().isoformat())
            session.add(last_check)
            await session.commit()

async def get_session() -> AsyncSession:
    """Получение сессии базы данных"""
    async with async_session() as session:
        yield session
