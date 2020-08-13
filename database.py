import asyncpg

MAX_PICTURES = 100
PHOTO = 1
VIDEO = 2


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
                          user_id, caption="", type_=PHOTO):
        await self.execute("INSERT INTO pictures (file_id, by_user, file_url, "
                           "caption, type) VALUES ($1, $2, $3, $4, $5)",
                           file_id, user_id,
                           file_url, caption,
                           type_, fetch_method="fetchval")

    async def get_picture(self, db_id):
        return (await self.execute("SELECT * FROM pictures WHERE id = $1", db_id))[0]

    async def remove_picture(self, db_id):
        return await self.execute("DELETE FROM pictures WHERE id = $1", db_id)

    async def get_pictures(self, user_id, max_=MAX_PICTURES,
                           caption=None):
        if caption is None:
            results = await self.execute("SELECT * FROM pictures WHERE by_user = $1 ORDER BY id DESC LIMIT $2",
                                         user_id, max_)
        else:
            results = await self.execute("SELECT * FROM pictures WHERE by_user = $1 AND "
                                         " caption LIKE CONCAT(CAST($3 as TEXT), '%')"
                                         "ORDER BY id DESC LIMIT $2",
                                         user_id, max_, caption)

        return results

    async def remove_pictures(self, user_id):
        await self.execute("DELETE FROM pictures WHERE by_user = $1", user_id)

    async def get_pictures_count(self, user_id):
        return await self.execute("SELECT count(*) FROM pictures WHERE by_user = $1",
                                  user_id, fetch_method="fetchval")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            raise

