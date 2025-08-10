from __future__ import annotations

import aiosqlite
from typing import AsyncIterator

from ..utils.config import DB_PATH


async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    # Improve concurrency behavior for SQLite
    await conn.execute("PRAGMA journal_mode=WAL;")
    await conn.execute("PRAGMA synchronous=NORMAL;")
    await conn.execute("PRAGMA busy_timeout=5000;")
    try:
        yield conn
    finally:
        await conn.close()


async def execute_script(conn: aiosqlite.Connection, script: str) -> None:
    await conn.executescript(script)
    await conn.commit()


async def execute(conn: aiosqlite.Connection, query: str, params: tuple | list | dict = ()) -> None:
    await conn.execute(query, params)
    await conn.commit()


async def fetch_all(conn: aiosqlite.Connection, query: str, params: tuple | list | dict = ()):  # type: ignore[valid-type]
    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def fetch_one(conn: aiosqlite.Connection, query: str, params: tuple | list | dict = ()):  # type: ignore[valid-type]
    async with conn.execute(query, params) as cursor:
        row = await cursor.fetchone()
        return dict(row) if row else None


