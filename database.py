import asyncpg

MAX_PICTURES = 100


class NSFWDatabase:
    def __init__(self, credentials):
        self.credentials = credentials
        self.connection = None

    async def __aenter__(self):
        self.connection = await asyncpg.connect(**self.credentials)

        return self

    async def execute(self, query, *params,
                      fetch_method='fetch'):
        prepared = await self.connection.prepare(query)

        return await getattr(prepared, fetch_method)(*params)

    async def add_picture(self, file_id, file_url,
                          user_id):
        await self.execute("INSERT INTO pictures (file_id, by_user, file_url) VALUES ($1, $2, $3)",
                           file_id, user_id,
                           file_url, fetch_method="fetchval")

    async def get_picture(self, db_id):
        return (await self.execute("SELECT * FROM pictures WHERE id = $1", db_id))[0]

    async def remove_picture(self, db_id):
        return await self.execute("DELETE FROM pictures WHERE id = $1", db_id)

    async def get_pictures(self, user_id, max_=MAX_PICTURES):
        results = await self.execute("SELECT * FROM pictures WHERE by_user = $1 ORDER BY id DESC LIMIT $2",
                                     user_id, max_)

        return results

    async def get_pictures_count(self, user_id):
        return await self.execute("SELECT count(*) FROM pictures WHERE by_user = $1",
                                  user_id, fetch_method="fetchval")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            raise
