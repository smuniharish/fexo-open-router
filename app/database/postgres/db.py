# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# from app.helpers.utilities.envVar import envConfig

# DATABASE_URL: str = f"postgresql+asyncpg://{envConfig.postgres_db_user}:{envConfig.postgres_db_password}@{envConfig.postgres_db_uri}/{envConfig.postgres_db_name}"

# # Create an async engine
# engine = create_async_engine(DATABASE_URL, echo=True)

# # Create a session factory
# async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
