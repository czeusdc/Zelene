"""Database ORM models, engine, and connection management.

Uses SQLAlchemy async with asyncpg for PostgreSQL + pgvector.
Session lifecycle is managed via FastAPI dependency injection (get_db).
"""

