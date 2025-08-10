from __future__ import annotations

import aiosqlite
from typing import AsyncIterator

DB_PATH = "data.db"


async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
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


async def fetch_all(conn: aiosqlite.Connection, query: str, params: tuple | list | dict = ()):
    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def fetch_one(conn: aiosqlite.Connection, query: str, params: tuple | list | dict = ()):
    async with conn.execute(query, params) as cursor:
        row = await cursor.fetchone()
        return dict(row) if row else None


