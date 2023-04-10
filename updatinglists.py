import asyncio
import aiosqlite
import pickle


async def update_list():
    conn = await aiosqlite.connect('j.db')
    c = await conn.cursor()
    await c.execute('SELECT user_id FROM bansuser')
    rows = await c.fetchall()
    await conn.close()
    list1 = [row[0] for row in rows]
    return list1


async def main():
    while True:
        bans_list = await update_list()
        print('Список значений:', bans_list)
        # Сохранение списка значений в файл для последующего импорта в другую программу
        with open('files/ban_user.pkl', 'wb') as f:
            pickle.dump(bans_list, f)
        await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())
