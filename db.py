import sqlite3
import os

def create_connection() -> sqlite3.Connection:
    return sqlite3.connect('cinema.db')
        
def setup_database():
        conn =  create_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN {roles})
        )
        """)

        # Таблица фильмов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            duration INTEGER NOT NULL,
            poster_path TEXT NOT NULL,
            trailer_path TEXT NOT NULL
        )
        """)

        # Таблица расписания
        cursor.execute("""
           CREATE TABLE IF NOT EXISTS schedules (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               movie_id INTEGER NOT NULL,
               date TEXT NOT NULL,
               time TEXT NOT NULL,
               hall INTEGER NOT NULL,
               price Decimal(10, 2) NOT NULL,
               FOREIGN KEY (movie_id) REFERENCES movies (id)
           )
           """)

        # Таблица билетов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                schedule_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (schedule_id) REFERENCES schedule (id)
            )
            """)

        conn.commit()
        conn.close()

        print("База данных создана")


roles = ('Пользователь', "Администратор")


def seed_database():
    conn = create_connection()
    cursor = conn.cursor()


    users = [
        ('2', '2', 'Пользователь'),
        ('1', '1', 'Администратор')
    ]

    for user in users:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", user)


    movies = [
        ('Титаник', 'Фильм о любви', 180, os.path.join(os.getcwd(), 'posters', 'poster1.png'), os.path.join(os.getcwd(), 'trailers', 'trailer1.mp4')),
        ('Мстители', 'Фильм о супергероях', 120, os.path.join(os.getcwd(), 'posters', 'poster2.png'), os.path.join(os.getcwd(), 'trailers', 'trailer1.mp4')),
        ('Интерстеллар', 'Фильм о будущем', 150, os.path.join(os.getcwd(), 'posters', 'poster3.png'), os.path.join(os.getcwd(), 'trailers', 'trailer1.mp4')),
        ('Бойцовский клуб', 'Фильм о борьбе', 110, os.path.join(os.getcwd(), 'posters', 'poster4.png'), os.path.join(os.getcwd(), 'trailers', 'trailer1.mp4')),
        ('Джуманджи', 'Фильм о приключениях', 130, os.path.join(os.getcwd(), 'posters', 'poster5.png'), os.path.join(os.getcwd(), 'trailers', 'trailer1.mp4'))
    ]

    for movie in movies:
        cursor.execute("INSERT INTO movies (title, description, duration, poster_path, trailer_path) VALUES (?, ?, ?, ?, ?)", movie)
    


    schedules = [
        (1, '2023-05-01', '10:00:00', 1, 100),
        (2, '2023-05-02', '11:00:00', 2, 150),
        (3, '2023-05-03', '12:00:00', 3, 200),
        (4, '2023-05-04', '13:00:00', 1, 120),
        (5, '2023-05-05', '14:00:00', 2, 180),
        (6, '2023-05-06', '15:00:00', 3, 140),
        (7, '2023-05-07', '16:00:00', 1, 90),
        (8, '2023-05-08', '17:00:00', 2, 160),
        (9, '2023-05-09', '18:00:00', 3, 110),
        (10, '2023-05-10', '19:00:00', 1, 130),
        (11, '2023-05-11', '20:00:00', 2, 190),
        (12, '2023-05-12', '21:00:00', 3, 150),
        (13, '2023-05-13', '22:00:00', 1, 100),
        (14, '2023-05-14', '23:00:00', 2, 170),
        (15, '2023-05-15', '00:00:00', 3, 120),
        (16, '2023-05-16', '01:00:00', 1, 130),
        (17, '2023-05-17', '02:00:00', 2, 190),
        (18, '2023-05-18', '03:00:00', 3, 150),
        (19, '2023-05-19', '04:00:00', 1, 100),
        (20, '2023-05-20', '05:00:00', 2, 170),
        (21, '2023-05-21', '06:00:00', 3, 120),
        (22, '2023-05-22', '07:00:00', 1, 130),
        (23, '2023-05-23', '08:00:00', 2, 190),
    ]

    for schedule in schedules:
        cursor.execute("INSERT INTO schedules (movie_id, date, time, hall, price) VALUES (?, ?, ?, ?, ?)", schedule)

    conn.commit()

    conn.close()

    print("База данных заполнена")