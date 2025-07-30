from database import UserMessagesDB
from config import DSN

db = UserMessagesDB
async def main():
    db = UserMessagesDB(DSN)
    await db.connect()
    await db.delete_table()