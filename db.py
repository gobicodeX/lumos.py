import aiosqlite
from datetime import datetime, timedelta

async def init_db():
    async with aiosqlite.connect('birthdays.db') as connection:
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS USERS ( 
            id INTEGER PRIMARY KEY  AUTOINCREMENT, 
            user_id INTEGER,
            name TEXT,
            day TEXT
            ) 
        ''')
        await connection.commit()


async def save_birthday(user_id,name,day):
    async with aiosqlite.connect('birthdays.db') as connection:
        await connection.execute('''
        INSERT INTO USERS (user_id, name, day) VALUES (?, ?, ?)''',
                       (user_id,name,day))
        await connection.commit()


async def get_birthdays(user_id):
    async with aiosqlite.connect('birthdays.db') as connection:
        cursor = await connection.execute('''
        SELECT name, day FROM USERS WHERE user_id = ?
        ''', (user_id,))
        users = await cursor.fetchall()

        formatted = "\n".join([f"{user[0]}, {user[1]}" for user in users])
        return formatted


async def get_tomorrow():
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%d.%m')
    async with aiosqlite.connect('birthdays.db') as connection:
        cursor = await connection.execute('''
        SELECT user_id, name, day FROM USERS WHERE day = ?
        ''', (tomorrow,))
        return await cursor.fetchall()