from math import log
from shutil import move
import sys
import sqlite3
import db
import utils

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox,
    QVBoxLayout, QWidget, QStackedWidget, QFileDialog, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QSpinBox, QComboBox, QTextEdit, QFormLayout, QGridLayout, QLayout, QFrame, QListWidget, QListWidgetItem,
    QListView, QAbstractItemView, QHeaderView, QButtonGroup, QScrollArea
)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

from PyQt6.QtGui import QPixmap, QDesktopServices, QPixmap
from PyQt6.QtCore import QUrl, Qt


def init_base_stylesheet():
    return """
        QWidget {
            background-color: white;
            color: black;
            font-size: 14px;
            font-family: Arial, sans-serif;
        }
        QPushButton {
            background-color: yellow;
            border: none;
            color: black;
            outline: none;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #FFB02E;
        }
        QPushButton:pressed {
            background-color: #FFB02E;
        }
        QPushButton:focus {
            background-color: #FFB02E;
        }
        QPushButton:checked {
            background-color: #FFB02E;
        }
        QPushButton#destructive_button {
            background-color: transparent;
            color: red;
        }
        QPushButton#destructive_button:hover {
            background-color: white;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #888;
            border-radius: 5px;
        }
        QComboBox {
            padding: 5px;
            border: 1px solid #888;
            border-radius: 5px;
        }
        QTableWidget {
            background-color: white;
            color: white;
            font-size: 14px;
        }
        QAbstractItemView {
            background: black;
            outline: none;
            border-radius: 5px;
        }
        QAbstractItemView::item {
            padding: 5px;
            outline: none;
            color: white;
            background-color: transparent;
        }
        QAbstractItemView::item:selected {
            background-color: #FFB02E;
            color: black;
        }
        QScrollBar {
            border: none;
            outline: none;
        }
        QScrollBar:horizontal {
            background-color: gray;
            height: 10px;
            border-radius: 5px;
        }
        QScrollBar:vertical {
            background-color: gray;
            width: 10px;
            border-radius: 5px;
        }
        QSpinBox {
            padding: 5px;
            border: 1px solid #888;
            border-radius: 5px;
        }
        #logo {
            font-size: 24px;
            margin-bottom: 30px;
            font-style: italic;
            font-weight: bold;
        }
        #caption {
            color: #eee;
        }
    """


class VideoPlayer(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.media_player.setSource(video_path)
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        self.setCentralWidget(self.video_widget)
        self.media_player.play()

class CinemaApp(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Кинотеатры (Афиша)")
        self.resize(1290, 700)

        utils.center_window(self)
        self.setStyleSheet(init_base_stylesheet())
        
        self.user = user
        self.conn = db.create_connection()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.user_main_window = UserWindow(self.conn, user, self)
        self.admin_main_window = AdminWindow(self.conn, self)

        self.stack.addWidget(self.user_main_window)
        self.stack.addWidget(self.admin_main_window)

        if user[2] == 'Администратор':
            self.show_admin_main_window()
        else:
            self.show_user_main_window()
    def show_admin_main_window(self):
        self.stack.setCurrentWidget(self.admin_main_window)

    def show_user_main_window(self):
        self.stack.setCurrentWidget(self.user_main_window)


class AdminWindow(QWidget):
    def __init__(self, conn, parent):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.parent = parent

        self.setWindowTitle("Панель администратора")
        self.setGeometry(200, 100, 1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #111;
                color: #fff;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 16px;
                margin-bottom: 15px;
                color: #fff;
            }
            QPushButton {
                background-color: #FFD700;
                color: #111;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background-color: #E6C200;
            }
            QPushButton#destructive_button {
                background-color: #FF6347;
                color: white;
            }
            QPushButton#destructive_button:hover {
                background-color: #E5533E;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Кнопки управления
        manage_movies_button = QPushButton("Управление фильмами")
        manage_movies_button.clicked.connect(self.open_movies_management)
        layout.addWidget(manage_movies_button)

        manage_schedule_button = QPushButton("Управление расписанием")
        manage_schedule_button.clicked.connect(self.open_schedule_management)
        layout.addWidget(manage_schedule_button)

        logout_button = QPushButton("Выйти")
        logout_button.setObjectName("destructive_button")
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        self.setLayout(layout)

    def open_movies_management(self):
        self.movies_window = MovieManagementWindow(self.conn, self) 
        self.movies_window.show()

    def open_schedule_management(self):
        self.schedule_window = ScheduleManagementWindow(self.conn, self) 
        self.schedule_window.show()

    def logout(self):
        self.parent.close()

class MovieManagementWindow(QWidget):
    def __init__(self, conn, parent):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.parent = parent
        self.setStyleSheet(init_base_stylesheet())
        self.resize(800, 600)
        utils.center_window(self)
        self.setWindowTitle("Управление фильмами")

        layout = QVBoxLayout()

        # Поля для добавления фильма
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название фильма")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Описание фильма")

        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 500)
        self.duration_input.setSuffix(" минут")

        self.poster_button = QPushButton("Загрузить постер")
        self.poster_button.clicked.connect(self.upload_poster)
        self.poster_path = ""

        self.trailer_button = QPushButton("Загрузить трейлер")
        self.trailer_button.clicked.connect(self.upload_trailer)
        self.trailer_path = ""

        add_movie_button = QPushButton("Добавить фильм")
        add_movie_button.clicked.connect(self.add_movie)

        layout.addWidget(QLabel("Добавление фильма"))
        layout.addWidget(QLabel("Название"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Описание"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Продолжительность"))
        layout.addWidget(self.duration_input)
        layout.addWidget(self.poster_button)
        layout.addWidget(self.trailer_button)
        layout.addWidget(add_movie_button)

        self.setLayout(layout)

    def upload_poster(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите постер", "", "Изображения (*.png *.jpg *.jpeg)")
        if file_path:
            self.poster_path = file_path
            QMessageBox.information(self, "Успех", "Постер загружен!")

    def upload_trailer(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите трейлер", "", "Видео (*.mp4 *.mkv)")
        if file_path:
            self.trailer_path = file_path
            QMessageBox.information(self, "Успех", "Трейлер загружен!")

    def add_movie(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        duration = self.duration_input.value()

        if not all([title, description, self.poster_path, self.trailer_path]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля и загрузите постер и трейлер.")
            return

        self.cursor.execute("""
        INSERT INTO movies (title, description, duration, poster_path, trailer_path) 
        VALUES (?, ?, ?, ?, ?)
        """, (title, description, duration, self.poster_path, self.trailer_path))
        self.conn.commit()

        QMessageBox.information(self, "Успех", "Фильм успешно добавлен!")
        self.title_input.clear()
        self.description_input.clear()
        self.duration_input.setValue(1)
        self.poster_path = ""
        self.trailer_path = ""



class ScheduleManagementWindow(QWidget):
    def __init__(self, conn, parent):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.parent = parent
        self.setStyleSheet(init_base_stylesheet())
        self.resize(800, 600)
        utils.center_window(self)
        self.setWindowTitle("Управление расписанием")

        layout = QVBoxLayout()

        # Поля для добавления расписания
        self.movie_selector = QComboBox()
        self.load_movies()

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Дата (ГГГГ-ММ-ДД)")

        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Время (ЧЧ:ММ)")

        self.hall_input = QSpinBox()
        self.hall_input.setRange(1, 10)
        self.hall_input.setPrefix("Зал ")

        add_schedule_button = QPushButton("Добавить расписание")
        add_schedule_button.clicked.connect(self.add_schedule)

        layout.addWidget(QLabel("Добавление расписания"))
        layout.addWidget(QLabel("Выберите фильм"))
        layout.addWidget(self.movie_selector)
        layout.addWidget(QLabel("Дата"))
        layout.addWidget(self.date_input)
        layout.addWidget(QLabel("Время"))
        layout.addWidget(self.time_input)
        layout.addWidget(QLabel("Зал"))
        layout.addWidget(self.hall_input)
        layout.addWidget(add_schedule_button)

        self.setLayout(layout)

    def load_movies(self):
        """Загрузка списка фильмов для выбора."""
        self.cursor.execute("SELECT id, title FROM movies")
        movies = self.cursor.fetchall()
        self.movie_selector.clear()
        for movie in movies:
            self.movie_selector.addItem(movie[1], movie[0])

    def add_schedule(self):
        """Добавление нового расписания."""
        movie_id = self.movie_selector.currentData()
        date = self.date_input.text()
        time = self.time_input.text()
        hall = self.hall_input.value()

        if not all([movie_id, date, time]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        try:
            self.cursor.execute("""
            INSERT INTO schedules (movie_id, date, time, hall) VALUES (?, ?, ?, ?)
            """, (movie_id, date, time, hall))
            self.conn.commit()
            QMessageBox.information(self, "Успех", "Расписание успешно добавлено!")
            self.date_input.clear()
            self.time_input.clear()
        except sqlite3.Error as e:
            print(e)
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить расписание: {e}")



class Navbar(QFrame):
    def __init__(self, widgets=[]):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedWidth(200)
        self.setStyleSheet("""
            QFrame {
                background-color: black;
                padding: 0;
                color: #ffffff;
            }
            QPushButton {
                background-color: black;
                color: #ffffff;
                border: none;
                padding: 10px;
            }
            QPushButton:checked {
                background-color: #333333;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton#destructive_button {
                background-color: transparent;
                color: red;
            }
            QPushButton#destructive_button:hover {
                background-color: red;
                color: #ffffff;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 15, 0, 0)
        layout.setSpacing(0)
        for widget in widgets:
            if isinstance(widget, QWidget):
                layout.addWidget(widget)       
            elif isinstance(widget, QLayout):
                layout.addLayout(widget)
        self.setLayout(layout)     

class UserWindow(QWidget):
    def __init__(self, conn, user, parent):
        super().__init__()
        self.conn = conn
        self.user = user
        self.cursor = conn.cursor()
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(init_base_stylesheet() + """
            QPushButton {
                border-radius: 0;
            }
        """)

        self.setWindowTitle("Панель пользователя")

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.afisha = AfishaWidget(self.conn, self)
        self.stack.addWidget(self.afisha)
        self.my_tickets = MyTicketsWidget(self.conn, self.user[0], self)
        self.stack.addWidget(self.my_tickets)

        self.stack.currentChanged.connect(self.on_stacked_widget_changed)
        
        layout.addWidget(self.stack)
        logo = QLabel("КиноАфиша")
        logo.setObjectName("logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.buttons_group = QButtonGroup()
        self.buttons_group.setExclusive(True)        
       
        view_afisha_button = QPushButton("Афиша")
        view_afisha_button.setCheckable(True)
        view_afisha_button.setChecked(True)
        view_afisha_button.clicked.connect(self.open_afisha)


        my_tickets_button = QPushButton("Мои билеты")
        my_tickets_button.setCheckable(True)
        my_tickets_button.clicked.connect(self.open_my_tickets)


        self.buttons_group.addButton(view_afisha_button)
        self.buttons_group.addButton(my_tickets_button)

        logout_button = QPushButton("Выйти")
        logout_button.setObjectName("destructive_button")
        logout_button.clicked.connect(self.logout)


        navigation_layout = QVBoxLayout()
        navigation_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        navigation_layout.addWidget(logo)
        navigation_layout.addWidget(view_afisha_button)
        navigation_layout.addWidget(my_tickets_button)
        navigation_layout.addStretch()
        navigation_layout.addWidget(logout_button)

        navbar_widget = Navbar(widgets=[navigation_layout])

        main_layout.addWidget(navbar_widget)
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

    def on_stacked_widget_changed(self, index):
        if index == 1:
            self.my_tickets.refresh_tickets()

    def logout(self):
        self.parent.close()

    def open_afisha(self):
        self.stack.setCurrentIndex(0)

    def open_my_tickets(self):
        self.stack.setCurrentIndex(1)


class AfishaWidget(QFrame):
    def __init__(self, conn, parent):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.parent = parent

        self.setStyleSheet("""
            QFrame {
                background-color: white;
                color: black;  
            }                   
        """)

        self.setGeometry(300, 150, 800, 600)

        layout = QVBoxLayout()

        self.movies_list = QListWidget()
        self.movies_list.setContentsMargins(0, 0, 0, 0)
        self.movies_list.setSpacing(10)
        self.movies_list.setWrapping(True)
      

        self.movies_list.setViewMode(QListView.ViewMode.IconMode)
        self.movies_list.setResizeMode(QListView.ResizeMode.Adjust)

        self.movies_list.setDragEnabled(False)
        self.movies_list.setAcceptDrops(False)
        self.movies_list.setDropIndicatorShown(False)
        self.movies_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection) 
        movies = self.get_movies_list()

        if not movies or len(movies) == 0:
            label = QLabel("Фильмы не найдены")
            label.setObjectName("caption")
            layout.addStretch()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        else:
            for film in movies:
                self.add_movie_to_list(film)

        layout.addWidget(self.movies_list)
        self.setLayout(layout)
    
    def add_movie_to_list(self, movie):
        card = MovieCard(movie, self.parent.user[0], self)
        item = QListWidgetItem()
        item.setSizeHint(card.size())
        self.movies_list.addItem(item)
        self.movies_list.setItemWidget(item, card)

    def get_movies_list(self):
        self.cursor.execute("""
            SELECT movies.id, movies.title, movies.poster_path, movies.description FROM movies
        """)
        records = self.cursor.fetchall()
        return records


class MovieCard(QPushButton):
    def __init__(self, movie, user_id, parent):
        super().__init__() 
        self.movie = movie
        self.parent = parent
        self.user_id = user_id
        self.setFixedSize(200, 250)
        self.setContentsMargins(0, 0, 0, 5)
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #111;
                border-radius: 4px;
                background-color: #111;
            }
            QWidget {
                border: none;
            }
            QLabel {
                color: #fff; 
                font-family: Arial, sans-serif;
            }
            QLabel#poster {
                border-radius: 5px;
            }
            QLabel#title {
                font-size: 14px;
                font-weight: 600;
                margin: 5px 0;
                text-align: center;
            }
            QLabel#description {
                font-size: 13px;
                color: #aaa;
                margin: 5px 0;
            }
        """)
        
        title = QLabel(movie[1])
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(movie[2]).scaled(
            200, 149, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        image = QLabel()
        image.setPixmap(pixmap)
        image.setObjectName("poster")
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(movie[3])
        description.setObjectName("description")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(image)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.setSpacing(6)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)
        self.clicked.connect(self.open_movie_info)
    def open_movie_info(self):
        self.movie_info_window = MovieInfoWindow(self.parent.conn, self.movie[0], self.user_id)
        self.movie_info_window.show()

class MovieInfoWindow(QWidget):
    def __init__(self, conn, movie_id, user_id):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.movie_id = movie_id
        self.user_id = user_id

        utils.center_window(self)
        self.setWindowTitle("Детали фильма")
        self.setGeometry(300, 150, 800, 600)

        # Стилизация окна
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: Arial, sans-serif;
                color: #333;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #111;
                margin-bottom: 10px;
            }
            QLabel#description {
                font-size: 16px;
                line-height: 1.5;
                margin-bottom: 15px;
                color: #555;
            }
            QLabel#info {
                font-size: 14px;
                color: #777;
                margin-bottom: 5px;
            }
            QLabel#poster {
                border-radius: 8px;
            }
            QPushButton {
                font-size: 14px;
                padding: 8px 15px;
                background-color: #FFD700;
                color: #111;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
            QPushButton:pressed {
                background-color: #E6AC00;
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #888;
                border-radius: 5px;
                background-color: #fff;
                color: #333;
                font-size: 14px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.cursor.execute("""
        SELECT movies.title, movies.description, movies.duration, movies.poster_path, movies.trailer_path, 
            schedules.hall, schedules.time
        FROM movies 
        LEFT JOIN schedules ON movies.id = schedules.movie_id
        WHERE movies.id = ?
        """, (movie_id,))
        movie = self.cursor.fetchone()

        if movie:
            title, description, duration, poster, trailer, hall, time = movie

            # Заголовок
            title_label = QLabel(title)
            title_label.setObjectName("title")
            main_layout.addWidget(title_label)

            # Постер
            if poster:
                pixmap = QPixmap(poster).scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                poster_label = QLabel()
                poster_label.setPixmap(pixmap)
                poster_label.setObjectName("poster")
                main_layout.addWidget(poster_label, alignment=Qt.AlignmentFlag.AlignCenter)

            # Описание
            description_label = QLabel(description)
            description_label.setObjectName("description")
            description_label.setWordWrap(True)
            main_layout.addWidget(description_label)

            # Информация о фильме
            info_layout = QVBoxLayout()
            duration_label = QLabel(f"Продолжительность: {duration} минут")
            duration_label.setObjectName("info")
            hall_label = QLabel(f"Зал: {hall}")
            hall_label.setObjectName("info")
            time_label = QLabel(f"Время: {time}")
            time_label.setObjectName("info")
            info_layout.addWidget(duration_label)
            info_layout.addWidget(hall_label)
            info_layout.addWidget(time_label)
            main_layout.addLayout(info_layout)

            # Трейлер
            if trailer:
                trailer_button = QPushButton("Просмотреть трейлер")
                trailer_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(trailer)))
                main_layout.addWidget(trailer_button, alignment=Qt.AlignmentFlag.AlignCenter)

            # Покупка билета
            ticket_layout = QHBoxLayout()
            ticket_label = QLabel("Количество билетов:")
            self.ticket_count = QSpinBox()
            self.ticket_count.setRange(1, 10)
            buy_button = QPushButton("Купить билет")
            buy_button.clicked.connect(self.buy_ticket)

            ticket_layout.addWidget(ticket_label)
            ticket_layout.addWidget(self.ticket_count)
            ticket_layout.addWidget(buy_button)
            main_layout.addLayout(ticket_layout)

        self.setLayout(main_layout)

    def buy_ticket(self):
        """Покупка билета."""
        quantity = self.ticket_count.value()

        self.cursor.execute("""
        INSERT INTO tickets (user_id, schedule_id, quantity) VALUES (?, ?, ?)
        """, (self.user_id, self.movie_id, quantity))
        self.conn.commit()

        QMessageBox.information(self, "Успех", "Билет успешно куплен!")
        self.close()        
    def play_trailer(self, trailer_path):
        """Функция для воспроизведения трейлера"""
        if trailer_path:
            self.player = VideoPlayer(trailer_path)
            self.player.show()

class MyTicketsWidget(QWidget):
    def __init__(self, conn, user_id, parent):
        super().__init__()
        self.conn = conn
        self.cursor = conn.cursor()
        self.user_id = user_id
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
            QFrame {
                background-color: #222;
                border-radius: 8px;
                margin-bottom: 10px;
                color: white;
            }
            #ticket-title {
                font-size: 16px;
                font-weight: bold;
            }
            #ticket-info {
                font-size: 14px;
            }
        """)

        # Основной макет
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Прокручиваемая область для билетов
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidgetResizable(True)

        # Контейнер для карточек билетов
        self.tickets_container = QVBoxLayout()
        self.tickets_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        tickets_widget = QWidget()
        tickets_widget.setLayout(self.tickets_container)
        scroll_area.setWidget(tickets_widget)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Загрузка билетов
        self.load_tickets()
    def load_tickets(self):
        """Загружает список билетов пользователя и отображает их."""
        self.cursor.execute("""
        SELECT movies.title, schedules.date, schedules.time, schedules.hall, tickets.quantity
        FROM tickets
        JOIN schedules ON tickets.schedule_id = schedules.id
        JOIN movies ON schedules.movie_id = movies.id
        WHERE tickets.user_id = ?
        """, (self.user_id,))
        tickets = self.cursor.fetchall()

        # Очистка контейнера
        while self.tickets_container.count():
            child = self.tickets_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Создание карточек для каждого билета
        for ticket in tickets:
            container = QHBoxLayout()
            movie_title, date, time, hall, quantity = ticket
            ticket_card = QFrame()
            ticket_layout = QVBoxLayout()
            ticket_layout.setSpacing(5)

            # Заголовок фильма
            movie_label = QLabel(movie_title)
            movie_label.setObjectName("ticket-title")
            ticket_layout.addWidget(movie_label)

            # Дата и время
            date_label = QLabel(f"Дата: {date}")
            time_label = QLabel(f"Время: {time}")
            ticket_layout.addWidget(date_label)
            ticket_layout.addWidget(time_label)

            # Зал
            hall_label = QLabel(f"Зал: {hall}")
            ticket_layout.addWidget(hall_label)

            # Количество билетов
            quantity_label = QLabel(f"Билетов: {quantity}")
            quantity_label.setObjectName("info")
            quantity_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            container.addLayout(ticket_layout, 1)
            container.addStretch()
            container.addWidget(quantity_label)
            ticket_card.setLayout(container)
            self.tickets_container.addWidget(ticket_card)

    def refresh_tickets(self):
        """Обновление списка билетов."""
        self.load_tickets()

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = db.create_connection()
        self.setFixedSize(400, 300)
        utils.center_window(self)
        self.setWindowTitle("Авторизация и Регистрация")

        self.setStyleSheet(
            init_base_stylesheet()
            + """
            #submit_button {
                background-color: yellow;
                margin-top: 10px;
            }

            #submit_button:hover {  
                background-color: #FF8C00;
            }

            #submit_button:pressed {
                background-color: #FF8C00;
            }
            #switch_button {
                background-color: white;
                color: black;
            }
            """
        )

        self.setContentsMargins(10, 10, 10, 10)

        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(LoginFormWidget(self.conn, self))
        self.stack.addWidget(RegisterFormWidget(self.conn, self))
        
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def switch_window(self, number):
        self.stack.setCurrentIndex(number)

class LoginFormWidget(QWidget):
    def __init__(self, conn, parent):
        super().__init__()
        self.conn = conn
        self.db_cursor = conn.cursor()
        self.parent = parent

        form_layout = QFormLayout()
        fields_layout = QGridLayout()

        username_label = QLabel('Логин')
        self.username_input = QLineEdit()
        
        password_label = QLabel('Пароль')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)


        submit_button = QPushButton('Войти')
        submit_button.clicked.connect(self.login)

        submit_button.setObjectName("submit_button")

        open_register_button = QPushButton('Создать аккаунт')
        open_register_button.clicked.connect(self.open_register_window)

        open_register_button.setObjectName("switch_button")

        fields_layout.addWidget(username_label, 0, 0)
        fields_layout.addWidget(self.username_input, 0, 1)
        fields_layout.addWidget(password_label, 1, 0)
        fields_layout.addWidget(self.password_input, 1, 1)

        fields_layout.addWidget(submit_button, 2, 0, 1, 2)
        fields_layout.addWidget(open_register_button, 3, 0, 1, 2)
      

        form_layout.setLayout(1, QFormLayout.ItemRole.SpanningRole, fields_layout)
        self.setLayout(form_layout)


    def login(self):
        """Обработка авторизации."""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        self.db_cursor.execute("""
        SELECT id, username, role FROM users WHERE username = ? AND password = ?
        """, (username, password))
        user = self.db_cursor.fetchone()

        if user:
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
            self.open_main_window(user)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя, пароль или роль.")

   
    def open_main_window(self, user):
        """Открытие основного окна после авторизации."""
        self.parent.close()
        CinemaApp(user).show()

    def open_register_window(self):
        self.parent.switch_window(1)


class RegisterFormWidget(QWidget):
    def __init__(self, conn, parent):
        super().__init__()
        self.conn = conn
        self.parent = parent
        self.db_cursor = conn.cursor()

        form_layout = QFormLayout()
        fields_layout = QGridLayout()

        username_label = QLabel('Имя пользователя')
        self.username_input = QLineEdit()
        
        password_label = QLabel('Пароль')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        role_label = QLabel('Роль')
        self.role_combobox = QComboBox()
        self.role_combobox.addItems(db.roles)

        submit_button = QPushButton('Создать аккаунт')
        submit_button.clicked.connect(self.register)

        submit_button.setObjectName("submit_button")

        open_login_button = QPushButton('Войти')
        open_login_button.clicked.connect(self.open_login_window)

        open_login_button.setObjectName("switch_button")

        fields_layout.addWidget(username_label, 0, 0)
        fields_layout.addWidget(self.username_input, 0, 1)
        fields_layout.addWidget(password_label, 1, 0)
        fields_layout.addWidget(self.password_input, 1, 1)
        fields_layout.addWidget(role_label, 2, 0)
        fields_layout.addWidget(self.role_combobox, 2, 1)

        fields_layout.addWidget(submit_button, 3, 0, 1, 2)
        fields_layout.addWidget(open_login_button, 4, 0, 1, 2)

        form_layout.setLayout(1, QFormLayout.ItemRole.SpanningRole, fields_layout)

        self.setLayout(form_layout)

    def register(self):
        """Обработка регистрации."""
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combobox.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        self.db_cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if self.db_cursor.fetchone():
            QMessageBox.warning(self, "Ошибка", "Имя пользователя уже занято.")
            return

        self.db_cursor.execute("""
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
        """, (username, password, role))
        self.conn.commit()
        QMessageBox.information(self, "Успех", "Регистрация успешно завершена!")

    def open_login_window(self):
        self.parent.switch_window(0)

app = QApplication(sys.argv)
db.setup_database()
# db.seed_database()
auth_window = AuthWindow()
auth_window.show()
sys.exit(app.exec())