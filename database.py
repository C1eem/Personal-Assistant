from aiogram import types
import asyncpg

class UserMessagesDB:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)

    async def create_table(self):
        query = '''
                CREATE TABLE IF NOT EXISTS user_requests (
                    id SERIAL PRIMARY KEY,
                    message_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    username VARCHAR(64),
                    first_name VARCHAR(128) NOT NULL,
                    last_name VARCHAR(128),
                    chat_id BIGINT NOT NULL,
                    message_date TIMESTAMP NOT NULL,
                    message_text TEXT NOT NULL,
                    contact_info VARCHAR(255),
                    fio VARCHAR(255),
                    product_interest VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW()
                );
                '''
        async with self.pool.acquire() as conn:
            await conn.execute(query)

    async def save_message(self, message: types.Message,
                           contact_info: str = None,
                           fio: str = None,
                           product_interest: str = None):
        query = '''
        INSERT INTO user_requests (
            message_id,
            user_id,
            username,
            first_name,
            last_name,
            chat_id,
            message_date,
            message_text,
            contact_info,
            fio,
            product_interest
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        '''

        raw_date = message.date if message.date else None
        if raw_date:
            db_date = raw_date.replace(tzinfo=None)
        else:
            db_date = None

        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                message.message_id,
                message.from_user.id if message.from_user else None,
                message.from_user.username if message.from_user else None,
                message.from_user.first_name if message.from_user else None,
                message.from_user.last_name if message.from_user else None,
                message.chat.id if message.chat else None,
                db_date,
                message.text,
                contact_info,
                fio,
                product_interest
            )

    async def get_all_messages(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM user_messages ORDER BY created at DESC')
            return [dict(row) for row in rows]


