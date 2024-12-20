import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QListWidget, QLineEdit, QTextEdit, QDialog,
    QFormLayout, QComboBox, QSpinBox, QCalendarWidget, QFileDialog, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


# База данных
class CinemaDatabase:
    def __init__(self, db_name="cinema.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    poster_path TEXT,
                    trailer_url TEXT,
                    duration INTEGER,
                    show_date TEXT,
                    price REAL,
                    hall TEXT
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY,
                    movie_id INTEGER,
                    user_name TEXT NOT NULL,
                    FOREIGN KEY(movie_id) REFERENCES movies(id)
                )
            """)

    def add_movie(self, title, poster_path, trailer_url, duration, show_date, price, hall):
        with self.conn:
            self.conn.execute("""
                INSERT INTO movies (title, poster_path, trailer_url, duration, show_date, price, hall)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, poster_path, trailer_url, duration, show_date, price, hall))

    def get_movies(self):
        with self.conn:
            return self.conn.execute("SELECT * FROM movies").fetchall()

    def delete_movie(self, movie_id):
        with self.conn:
            self.conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))

    def update_movie(self, movie_id, title, poster_path, trailer_url, duration, show_date, price, hall):
        with self.conn:
            self.conn.execute("""
                UPDATE movies
                SET title = ?, poster_path = ?, trailer_url = ?, duration = ?, show_date = ?, price = ?, hall = ?
                WHERE id = ?
            """, (title, poster_path, trailer_url, duration, show_date, price, hall, movie_id))

    def add_ticket(self, movie_id, user_name):
        with self.conn:
            self.conn.execute("""
                INSERT INTO tickets (movie_id, user_name)
                VALUES (?, ?)
            """, (movie_id, user_name))

    def get_tickets(self, user_name):
        with self.conn:
            return self.conn.execute("""
                SELECT movies.title, movies.show_date, movies.hall, movies.price
                FROM tickets
                JOIN movies ON tickets.movie_id = movies.id
                WHERE tickets.user_name = ?
            """, (user_name,)).fetchall()


# Основное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кинотеатр")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(open("style.css").read())

        self.db = CinemaDatabase()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.movie_list = QListWidget()
        self.layout.addWidget(self.movie_list)
        self.load_movies()

        self.details_button = QPushButton("Просмотр фильма")
        self.details_button.clicked.connect(self.show_movie_details)
        self.layout.addWidget(self.details_button)

        self.add_movie_button = QPushButton("Добавить фильм (админ)")
        self.add_movie_button.clicked.connect(self.add_movie)
        self.layout.addWidget(self.add_movie_button)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def load_movies(self):
        self.movie_list.clear()
        movies = self.db.get_movies()
        for movie in movies:
            self.movie_list.addItem(f"{movie[1]} - {movie[5]}")

    def show_movie_details(self):
        selected_item = self.movie_list.currentItem()
        if selected_item:
            title = selected_item.text().split(" - ")[0]
            movie = next((m for m in self.db.get_movies() if m[1] == title), None)
            if movie:
                details = MovieDetailsDialog(movie, self.db)
                details.exec()

    def add_movie(self):
        dialog = AddMovieDialog(self.db, self.load_movies)
        dialog.exec()


# Окно деталей фильма
class MovieDetailsDialog(QDialog):
    def __init__(self, movie, db):
        super().__init__()
        self.movie = movie
        self.db = db

        self.setWindowTitle(movie[1])
        self.setLayout(QVBoxLayout())

        poster_label = QLabel()
        pixmap = QPixmap(movie[2])
        poster_label.setPixmap(pixmap.scaled(200, 300, Qt.AspectRatioMode.KeepAspectRatio))
        self.layout().addWidget(poster_label)

        details = f"""
            <b>Название:</b> {movie[1]}<br>
            <b>Длительность:</b> {movie[4]} мин.<br>
            <b>Дата показа:</b> {movie[5]}<br>
            <b>Зал:</b> {movie[7]}<br>
            <b>Цена:</b> {movie[6]} руб.<br>
        """
        details_label = QLabel(details)
        details_label.setWordWrap(True)
        self.layout().addWidget(details_label)

        buy_button = QPushButton("Купить билет")
        buy_button.clicked.connect(self.buy_ticket)
        self.layout().addWidget(buy_button)

    def buy_ticket(self):
        name, ok = QInputDialog.getText(self, "Имя пользователя", "Введите ваше имя:")
        if ok and name:
            self.db.add_ticket(self.movie[0], name)
            QMessageBox.information(self, "Билет куплен", "Ваш билет успешно сохранен!")


# Окно добавления фильма
class AddMovieDialog(QDialog):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Добавить фильм")
        self.setLayout(QFormLayout())

        self.title_input = QLineEdit()
        self.layout().addRow("Название:", self.title_input)

        self.poster_input = QLineEdit()
        self.poster_button = QPushButton("Выбрать файл")
        self.poster_button.clicked.connect(self.select_poster)
        self.layout().addRow("Постер:", self.poster_input)
        self.layout().addWidget(self.poster_button)

        self.trailer_input = QLineEdit()
        self.layout().addRow("URL трейлера:", self.trailer_input)

        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 500)
        self.layout().addRow("Длительность (мин):", self.duration_input)

        self.date_input = QCalendarWidget()
        self.layout().addRow("Дата показа:", self.date_input)

        self.price_input = QSpinBox()
        self.price_input.setRange(1, 5000)
        self.layout().addRow("Цена билета:", self.price_input)

        self.hall_input = QComboBox()
        self.hall_input.addItems(["Зал 1", "Зал 2", "Зал 3"])
        self.layout().addRow("Зал:", self.hall_input)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_movie)
        self.layout().addWidget(self.add_button)

    def select_poster(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.poster_input.setText(file_path)

    def add_movie(self):
        title = self.title_input.text()
        poster = self.poster_input.text()
        trailer = self.trailer_input.text()
        duration = self.duration_input.value()
        show_date = self.date_input.selectedDate().toString("yyyy-MM-dd")
        price = self.price_input.value()
        hall = self.hall_input.currentText()

        if title and poster:
            self.db.add_movie(title, poster, trailer, duration, show_date, price, hall)
            self.refresh_callback()
            self.accept()


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
