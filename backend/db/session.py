from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

from config import settings

DATABASE_URL = settings.DATABASE_URL

class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          
    max_overflow=10,      
    pool_pre_ping=True,    
    pool_recycle=1800,     
    echo=False,            
)



# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,       
)



async def init_db():
    from models.user import User 
    from models.consultation import Consultation    
    from models.transcript import Transcript        
    from models.soap_note import SoapNote    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



#database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise