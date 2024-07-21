import asyncpg

class AsyncDBClient:
    def __init__(self, user, password, host, port, database):
        self.dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.pool = None

    async def connect(self):
        if self.pool is not None:
            await self.pool.close()
        self.pool = await asyncpg.create_pool(self.dsn)

    async def execute(self, query, params=None):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *params)

    async def fetchall(self, query, params=None):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *params)

    async def commit(self):
        # `asyncpg` automatically commits on successful execute, so this may not be needed
        pass

    async def close(self):
        await self.pool.close()

    async def rollover(self):
        await self.connect()
