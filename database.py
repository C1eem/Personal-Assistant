import asyncpg
from aiogram import types
from datetime import timezone, datetime

class UserMessagesDB:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)

    async def create_table(self):
        query = '''
                CREATE TABLE IF NOT EXISTS user_messages (
                    id SERIAL PRIMARY KEY,
                    message_id BIGINT,
                    user_id BIGINT,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    chat_id BIGINT,
                    chat_type TEXT,
                    date TIMESTAMP,
                    text TEXT,
                    created_at TIMESTAMP DEFAULT now()
                );
                '''
        async with self.pool.acquire() as conn:
            await conn.execute(query)

    async def save_message(self, message: types.Message):
        query = '''
        INSERT INTO user_messages (
            message_id,
            user_id,
            username,
            first_name,
            last_name,
            chat_id,
            chat_type,
            date,
            text
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        '''
        # Преобразуем дату в UTC и убираем временную зону (если БД без timezone)
        raw_date = message.date if message.date else None
        if raw_date:
            db_date = raw_date.isoformat() if raw_date else None
        else:
            db_date = None

        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                message.message_id,
                message.from_user.id,
                message.from_user.username if message.from_user else None,
                message.from_user.first_name,
                message.from_user.last_name,
                message.chat.id,
                message.chat.type,
                db_date,
                message.text
            )

    async def get_all_messages(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM user_messages ORDER BY created at DESC')
            return [dict(row) for row in rows]


    async  def ExampleRun(self, message: types.Message):
        '''Примерный скрипт того, как работать с классом UserMessagesDB'''
        db = UserMessagesDB(dsn="postgres://user:pass@localhost:5432/dbname")
        await db.connect()
        await db.create_table()
        await db.save_message(message)
        messages = await db.get_all_messages()

