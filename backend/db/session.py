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

print("DATABASE_URL =", DATABASE_URL)
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
    import models 
    from sqlalchemy import text  
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Safe column migration for existing tables in production
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS license_number VARCHAR(50);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS license_verified BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS hospital_name VARCHAR(150);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image VARCHAR(500);",
            "ALTER TABLE users ALTER COLUMN email DROP NOT NULL;",
        ]
        for query in migrations:
            try:
                await conn.execute(text(query))
            except Exception as e:
                print(f"Schema migration statement note ({query}): {e}")



#database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise