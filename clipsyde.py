import sys
import os
import json
import sqlite3
import shutil
import ctypes
from datetime import datetime

from PySide6.QtCore import (
    Qt,
    QPoint,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    Property,
    QByteArray,
    QRect,
    QEvent,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QLinearGradient,
    QPen,
    QIcon,
    QPixmap,
    QKeySequence,
    QAction,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QFrame,
    QMenu,
    QTextEdit,
    QDialog,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QShortcut,
    QGraphicsOpacityEffect,
)

ACCENT = "#451ca3"
DB_FILE = "clipsyde.db"
BACKUP_DIR = "backups"
BACKUP_RETENTION = 7

CATEGORIES = [
    "Other",
    "Code",
    "Links",
    "Commands",
    "Personal",
]

LUCIDE_ICONS = {
    "settings": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6h.01A1.65 1.65 0 0 0 10 3.09V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9v.01A1.65 1.65 0 0 0 20.91 10H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>
        </svg>
    """,
    "pin": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <path d="M12 17v5"/>
            <path d="M9 3h6"/>
            <path d="M10 3v6l-4 4v2h12v-2l-4-4V3"/>
        </svg>
    """,
    "copy": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
        </svg>
    """,
    "edit": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <path d="M12 20h9"/>
            <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>
        </svg>
    """,
    "delete": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <path d="M3 6h18"/>
            <path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2"/>
            <path d="M19 6v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6"/>
            <path d="M10 11v6"/>
            <path d="M14 11v6"/>
        </svg>
    """,
    "plus": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <path d="M5 12h14"/>
            <path d="M12 5v14"/>
        </svg>
    """,
    "back": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
        </svg>
    """,
    "menu": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round">
            <circle cx="12" cy="12" r="1"/>
            <circle cx="19" cy="12" r="1"/>
            <circle cx="5" cy="12" r="1"/>
        </svg>
    """,
}


def make_icon(name, size=20):
    svg = LUCIDE_ICONS[name]

    renderer = QSvgRenderer(
        QByteArray(svg.encode("utf-8"))
    )

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                pinned INTEGER DEFAULT 0,
                category TEXT DEFAULT 'Other'
            )
        """)

        columns = [
            row[1]
            for row in self.conn.execute(
                "PRAGMA table_info(clips)"
            )
        ]

        if "title" not in columns:
            self.conn.execute(
                "ALTER TABLE clips ADD COLUMN title TEXT DEFAULT 'Untitled'"
            )

        if "pinned" not in columns:
            self.conn.execute(
                "ALTER TABLE clips ADD COLUMN pinned INTEGER DEFAULT 0"
            )

        if "category" not in columns:
            self.conn.execute(
                "ALTER TABLE clips ADD COLUMN category TEXT DEFAULT 'Other'"
            )

        self.conn.commit()

    def get(self, search=""):
        if search:
            return self.conn.execute(
                """
                SELECT id, title, content, pinned, category
                FROM clips
                WHERE title LIKE ?
                   OR content LIKE ?
                   OR category LIKE ?
                ORDER BY pinned DESC, id DESC
                """,
                (
                    f"%{search}%",
                    f"%{search}%",
                    f"%{search}%",
                ),
            ).fetchall()

        return self.conn.execute(
            """
            SELECT id, title, content, pinned, category
            FROM clips
            ORDER BY pinned DESC, id DESC
            """
        ).fetchall()

    def get_by_id(self, clip_id):
        return self.conn.execute(
            """
            SELECT id, title, content, pinned, category
            FROM clips
            WHERE id = ?
            """,
            (clip_id,),
        ).fetchone()

    def add(self, title, content, category):
        self.conn.execute(
            """
            INSERT INTO clips
            (title, content, category)
            VALUES (?, ?, ?)
            """,
            (title, content, category),
        )
        self.conn.commit()

    def update(self, clip_id, title, content, category):
        self.conn.execute(
            """
            UPDATE clips
            SET title = ?, content = ?, category = ?
            WHERE id = ?
            """,
            (
                title,
                content,
                category,
                clip_id,
            ),
        )
        self.conn.commit()

    def delete(self, clip_id):
        self.conn.execute(
            "DELETE FROM clips WHERE id = ?",
            (clip_id,),
        )
        self.conn.commit()

    def toggle_pin(self, clip_id):
        self.conn.execute(
            """
            UPDATE clips
            SET pinned = CASE
                WHEN pinned = 1 THEN 0
                ELSE 1
            END
            WHERE id = ?
            """,
            (clip_id,),
        )
        self.conn.commit()

    def clear(self):
        self.conn.execute(
            "DELETE FROM clips"
        )
        self.conn.commit()

    def count(self):
        return self.conn.execute(
            "SELECT COUNT(*) FROM clips"
        ).fetchone()[0]

    def export_all(self):
        clips = self.conn.execute(
            """
            SELECT id, title, content, pinned, category
            FROM clips
            ORDER BY id ASC
            """
        ).fetchall()

        return [
            {
                "id": clip[0],
                "title": clip[1],
                "content": clip[2],
                "pinned": bool(clip[3]),
                "category": clip[4] or "Other",
            }
            for clip in clips
        ]

    def import_all(self, clips):
        imported = 0

        for clip in clips:
            if not isinstance(clip, dict):
                continue

            title = str(
                clip.get("title", "Untitled")
            ).strip() or "Untitled"

            content = str(
                clip.get("content", "")
            )

            if not content:
                continue

            category = str(
                clip.get("category", "Other")
            ).strip() or "Other"

            pinned = 1 if clip.get(
                "pinned",
                False
            ) else 0

            self.conn.execute(
                """
                INSERT INTO clips
                (title, content, pinned, category)
                VALUES (?, ?, ?, ?)
                """,
                (
                    title,
                    content,
                    pinned,
                    category,
                ),
            )

            imported += 1

        self.conn.commit()

        return imported


class VectorIcon(QWidget):
    def __init__(
        self,
        icon,
        parent=None,
        size=22,
        colour="#ffffff",
    ):
        super().__init__(parent)

        self.icon = icon
        self.colour = colour

        self.setFixedSize(
            size,
            size
        )

    def paintEvent(self, event):
        svg = LUCIDE_ICONS.get(
            self.icon
        )

        if not svg:
            return

        svg = svg.replace(
            'stroke="#ffffff"',
            f'stroke="{self.colour}"'
        )

        renderer = QSvgRenderer(
            QByteArray(svg.encode("utf-8"))
        )

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        renderer.render(
            painter,
            self.rect()
        )

        painter.end()


class IconButton(QPushButton):
    def __init__(
        self,
        icon,
        parent=None,
        size=32,
    ):
        super().__init__(parent)

        self.icon_name = icon

        self.setFixedSize(
            size,
            size
        )

        self.setIcon(
            make_icon(
                icon,
                min(size - 10, 20)
            )
        )

        self.setIconSize(
            self.iconSize()
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 7px;
                padding: 0;
            }

            QPushButton:hover {
                background: #29292c;
            }

            QPushButton:pressed {
                background: #333336;
            }
        """)


class WindowButton(QWidget):
    def __init__(
        self,
        symbol,
        parent=None
    ):
        super().__init__(parent)

        self.symbol = symbol

        self.setFixedSize(
            20,
            20
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_Hover
        )

        self._hover_amount = 0.0

        self.animation = QPropertyAnimation(
            self,
            b"hoverAmount"
        )

        self.animation.setDuration(
            150
        )

        self.animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

    def get_hover_amount(self):
        return self._hover_amount

    def set_hover_amount(self, value):
        self._hover_amount = value
        self.update()

    hoverAmount = Property(
        float,
        get_hover_amount,
        set_hover_amount
    )

    def enterEvent(self, event):
        self.animation.stop()

        self.animation.setStartValue(
            self._hover_amount
        )

        self.animation.setEndValue(
            1.0
        )

        self.animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()

        self.animation.setStartValue(
            self._hover_amount
        )

        self.animation.setEndValue(
            0.0
        )

        self.animation.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            window = self.window()

            if hasattr(
                window,
                "window_button_clicked"
            ):
                window.window_button_clicked(
                    self.symbol
                )

            event.accept()
            return

        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        colours = {
            "close": "#ff5f57",
            "minimise": "#febc2e",
            "maximise": "#28c840",
        }

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(colours[self.symbol])
        )

        centre = self.rect().center()

        radius = (
            7.5
            + self._hover_amount
        )

        painter.drawEllipse(
            centre,
            radius,
            radius
        )

        if self._hover_amount > 0.01:
            pen = QPen(
                QColor("#333333")
            )

            pen.setWidthF(1.5)

            pen.setCapStyle(
                Qt.PenCapStyle.RoundCap
            )

            pen.setJoinStyle(
                Qt.PenJoinStyle.RoundJoin
            )

            painter.setPen(pen)
            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            if self.symbol == "close":
                painter.drawLine(
                    centre.x() - 3,
                    centre.y() - 3,
                    centre.x() + 3,
                    centre.y() + 3
                )

                painter.drawLine(
                    centre.x() + 3,
                    centre.y() - 3,
                    centre.x() - 3,
                    centre.y() + 3
                )

            elif self.symbol == "minimise":
                painter.drawLine(
                    centre.x() - 3,
                    centre.y(),
                    centre.x() + 3,
                    centre.y()
                )

            elif self.symbol == "maximise":
                painter.drawRect(
                    centre.x() - 3,
                    centre.y() - 3,
                    6,
                    6
                )

        painter.end()


class Toast(QWidget):
    def __init__(
        self,
        parent,
        message
    ):
        super().__init__(parent)

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            14,
            10,
            14,
            10
        )

        layout.setSpacing(8)

        icon = QLabel("✓")

        icon.setStyleSheet("""
            QLabel {
                color: #b9a1ff;
                font-size: 14px;
                font-weight: 700;
            }
        """)

        label = QLabel(message)

        label.setStyleSheet("""
            QLabel {
                color: #eeeeef;
                font-size: 12px;
                font-weight: 500;
            }
        """)

        layout.addWidget(icon)
        layout.addWidget(label)

        self.setStyleSheet("""
            Toast {
                background: #1c1c1e;
                border: 1px solid #3c3c3f;
                border-radius: 8px;
            }
        """)

        self.adjustSize()

        self.effect = QGraphicsOpacityEffect(
            self
        )

        self.setGraphicsEffect(
            self.effect
        )

        self.effect.setOpacity(0.0)

        self.animation = QPropertyAnimation(
            self.effect,
            b"opacity"
        )

        self.animation.setDuration(
            180
        )

        self.animation.setEasingCurve(
            QEasingCurve.Type.OutCubic

        )

    def show_toast(self):
        parent = self.parentWidget()

        if not parent:
            return

        self.adjustSize()

        x = (
            parent.width()
            - self.width()
            - 18
        )

        y = (
            parent.height()
            - self.height()
            - 28
        )

        self.move(
            x,
            y
        )

        self.show()
        self.raise_()

        self.animation.stop()

        self.animation.setStartValue(
            0.0
        )

        self.animation.setEndValue(
            1.0
        )

        self.animation.start()

        QTimer.singleShot(
            1500,
            self.hide_toast
        )

    def hide_toast(self):
        self.animation.stop()

        self.animation.setStartValue(
            self.effect.opacity()
        )

        self.animation.setEndValue(
            0.0
        )

        self.animation.finished.connect(
            self.deleteLater
        )

        self.animation.start()


class ClipDialog(QDialog):
    def __init__(
        self,
        parent=None,
        clip=None
    ):
        super().__init__(parent)

        self.clip = clip
        self.drag_position = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(
            520,
            470
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        panel = QFrame()

        panel.setObjectName(
            "dialogPanel"
        )

        panel_layout = QVBoxLayout(
            panel
        )

        panel_layout.setContentsMargins(
            22,
            20,
            22,
            22
        )

        panel_layout.setSpacing(
            12
        )

        title = QLabel(
            "Edit Clip"
            if clip
            else "Add Clip"
        )

        title.setStyleSheet("""
            QLabel {
                color: #f5f5f5;
                font-size: 16px;
                font-weight: 600;
            }
        """)

        panel_layout.addWidget(
            title
        )

        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "Title"
        )

        self.title_input.setFixedHeight(
            38
        )

        panel_layout.addWidget(
            self.title_input
        )

        self.category_input = QComboBox()

        self.category_input.setEditable(
            True
        )

        self.category_input.addItems(
            CATEGORIES
        )

        self.category_input.setCurrentText(
            "Other"
        )

        self.category_input.setFixedHeight(
            38
        )

        panel_layout.addWidget(
            self.category_input
        )

        self.content_input = QTextEdit()

        self.content_input.setPlaceholderText(
            "Paste or type your clip here..."
        )

        self.content_input.setAcceptRichText(
            False
        )

        panel_layout.addWidget(
            self.content_input
        )

        self.counter = QLabel(
            "0 characters · 0 words"
        )

        self.counter.setStyleSheet("""
            QLabel {
                color: #77777b;
                font-size: 11px;
            }
        """)

        panel_layout.addWidget(
            self.counter
        )

        self.content_input.textChanged.connect(
            self.update_counter
        )

        buttons = QHBoxLayout()

        buttons.addStretch()

        cancel = QPushButton(
            "Cancel"
        )

        cancel.setFixedHeight(
            36
        )

        cancel.clicked.connect(
            self.reject
        )

        save = QPushButton(
            "Save"
        )

        save.setObjectName(
            "saveButton"
        )

        save.setFixedHeight(
            36
        )

        save.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            save
        )

        panel_layout.addLayout(
            buttons
        )

        layout.addWidget(
            panel
        )

        self.setStyleSheet("""
            QFrame#dialogPanel {
                background: #1c1c1e;
                border: 1px solid #3c3c3f;
                border-radius: 11px;
            }

            QLineEdit,
            QTextEdit,
            QComboBox {
                background: #111113;
                border: 1px solid #37373a;
                border-radius: 7px;
                color: #eeeeef;
                padding: 8px 10px;
                font-size: 13px;
            }

            QLineEdit:focus,
            QTextEdit:focus,
            QComboBox:focus {
                border: 1px solid #451ca3;
            }

            QComboBox::drop-down {
                border: none;
                width: 28px;
            }

            QComboBox QAbstractItemView {
                background: #1c1c1e;
                border: 1px solid #3a3a3d;
                color: #eeeeef;
                selection-background-color: #451ca3;
            }

            QPushButton {
                background: #2a2a2d;
                border: 1px solid #3a3a3d;
                border-radius: 7px;
                color: #eeeeef;
                padding: 0 15px;
                font-size: 12px;
                font-weight: 500;
            }

            QPushButton:hover {
                background: #333336;
            }

            QPushButton#saveButton {
                background: #451ca3;
                border: 1px solid #451ca3;
                color: white;
            }

            QPushButton#saveButton:hover {
                background: #5124b5;
            }
        """)

        if clip:
            self.title_input.setText(
                clip[1]
            )

            self.content_input.setPlainText(
                clip[2]
            )

            self.category_input.setCurrentText(
                clip[4] or "Other"
            )

        self.update_counter()

    def update_counter(self):
        text = self.content_input.toPlainText()

        characters = len(text)

        words = len(
            text.split()
        )

        self.counter.setText(
            f"{characters} characters · {words} words"
        )

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and event.position().y() <= 65
        ):
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        super().mouseReleaseEvent(event)

    def get_values(self):
        return (
            self.title_input.text().strip()
            or "Untitled",
            self.content_input.toPlainText(),
            self.category_input.currentText().strip()
            or "Other",
        )


class ConfirmDialog(QDialog):
    def __init__(
        self,
        parent=None,
        title="Confirm",
        message="Are you sure?"
    ):
        super().__init__(parent)

        self.drag_position = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(
            450,
            235
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        panel = QFrame()

        panel.setObjectName(
            "dialogPanel"
        )

        panel_layout = QVBoxLayout(
            panel
        )

        panel_layout.setContentsMargins(
            22,
            18,
            22,
            22
        )

        panel_layout.setSpacing(
            12
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "dialogTitle"
        )

        panel_layout.addWidget(
            title_label
        )

        message_label = QLabel(
            message
        )

        message_label.setObjectName(
            "dialogMessage"
        )

        message_label.setWordWrap(
            True
        )

        panel_layout.addWidget(
            message_label
        )

        panel_layout.addStretch()

        buttons = QHBoxLayout()

        buttons.addStretch()

        cancel = QPushButton(
            "Cancel"
        )

        cancel.setFixedHeight(
            36
        )

        cancel.clicked.connect(
            self.reject
        )

        confirm = QPushButton(
            "Clear All"
        )

        confirm.setObjectName(
            "confirmButton"
        )

        confirm.setFixedHeight(
            36
        )

        confirm.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            confirm
        )

        panel_layout.addLayout(
            buttons
        )

        layout.addWidget(
            panel
        )

        self.setStyleSheet("""
            QFrame#dialogPanel {
                background: #1c1c1e;
                border: 1px solid #3c3c3f;
                border-radius: 11px;
            }

            QLabel#dialogTitle {
                color: #f5f5f5;
                font-size: 16px;
                font-weight: 600;
            }

            QLabel#dialogMessage {
                color: #929296;
                font-size: 12px;
            }

            QPushButton {
                background: #2a2a2d;
                border: 1px solid #3a3a3d;
                border-radius: 7px;
                color: #eeeeef;
                padding: 0 15px;
                font-size: 12px;
                font-weight: 500;
            }

            QPushButton:hover {
                background: #333336;
            }

            QPushButton#confirmButton {
                background: #451ca3;
                border: 1px solid #451ca3;
                color: white;
            }

            QPushButton#confirmButton:hover {
                background: #5124b5;
            }
        """)

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and event.position().y() <= 65
        ):
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        super().mouseReleaseEvent(event)


class ClipItem(QFrame):
    def __init__(
        self,
        app,
        clip
    ):
        super().__init__()

        self.app = app
        self.clip = clip

        self.setObjectName(
            "clipItem"
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            15,
            10,
            9,
            10
        )

        layout.setSpacing(
            12
        )

        text_layout = QVBoxLayout()

        text_layout.setSpacing(
            4
        )

        title_layout = QHBoxLayout()

        title_layout.setSpacing(
            6
        )

        title = QLabel(
            clip[1]
        )

        title.setStyleSheet("""
            QLabel {
                color: #f2f2f3;
                font-size: 13px;
                font-weight: 600;
            }
        """)

        title_layout.addWidget(
            title
        )

        if clip[3]:
            pin = VectorIcon(
                "pin",
                self,
                17,
                "#bba5ff"
            )

            pin.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )

            title_layout.addWidget(
                pin
            )

        title_layout.addStretch()

        preview_text = clip[2].replace(
            "\n",
            " "
        )

        if len(preview_text) > 115:
            preview_text = (
                preview_text[:115]
                + "…"
            )

        preview = QLabel(
            preview_text
        )

        preview.setStyleSheet("""
            QLabel {
                color: #929296;
                font-size: 11px;
            }
        """)

        text_layout.addLayout(
            title_layout
        )

        text_layout.addWidget(
            preview
        )

        category = QLabel(
            clip[4] or "Other"
        )

        category.setStyleSheet("""
            QLabel {
                color: #bba5ff;
                background: #24184a;
                border: 1px solid #39256e;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 9px;
                font-weight: 600;
            }
        """)

        category.setSizePolicy(
            category.sizePolicy().horizontalPolicy(),
            category.sizePolicy().verticalPolicy()
        )

        text_layout.addWidget(
            category,
            0,
            Qt.AlignmentFlag.AlignLeft
        )

        layout.addLayout(
            text_layout,
            1
        )

        menu_button = IconButton(
            "menu",
            self,
            34
        )

        menu_button.clicked.connect(
            self.show_menu
        )

        layout.addWidget(
            menu_button
        )

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.app.select_clip(
                self.clip[0]
            )

            QApplication.clipboard().setText(
                self.clip[2]
            )

            self.app.show_toast(
                "Copied to clipboard"
            )

        elif (
            event.button()
            == Qt.MouseButton.RightButton
        ):
            self.app.select_clip(
                self.clip[0]
            )

            self.show_menu(
                event.globalPosition().toPoint()
            )

            event.accept()
            return

        super().mousePressEvent(event)

    def show_menu(self, position=None):
        menu = QMenu(self)

        menu.setStyleSheet("""
            QMenu {
                background: #1c1c1e;
                border: 1px solid #3a3a3d;
                border-radius: 7px;
                padding: 5px;
                color: #eeeeef;
            }

            QMenu::item {
                padding: 7px 25px 7px 10px;
                border-radius: 5px;
            }

            QMenu::item:selected {
                background: #451ca3;
            }

            QMenu::separator {
                height: 1px;
                background: #353538;
                margin: 5px 8px;
            }
        """)

        copy_action = menu.addAction(
            "Copy"
        )

        copy_title_action = menu.addAction(
            "Copy Title"
        )

        copy_content_action = menu.addAction(
            "Copy Content"
        )

        menu.addSeparator()

        edit_action = menu.addAction(
            "Edit"
        )

        pin_action = menu.addAction(
            "Unpin"
            if self.clip[3]
            else "Pin"
        )

        menu.addSeparator()

        delete_action = menu.addAction(
            "Delete"
        )

        if position is None:
            position = self.mapToGlobal(
                QPoint(
                    self.width() - 20,
                    self.height()
                )
            )

        action = menu.exec(
            position
        )

        if action == copy_action:
            self.copy_content()

        elif action == copy_title_action:
            QApplication.clipboard().setText(
                self.clip[1]
            )

            self.app.show_toast(
                "Title copied"
            )

        elif action == copy_content_action:
            self.copy_content()

        elif action == edit_action:
            self.app.edit_clip(
                self.clip
            )

        elif action == pin_action:
            self.app.db.toggle_pin(
                self.clip[0]
            )

            self.app.refresh()

            self.app.show_toast(
                "Clip pinned"
                if not self.clip[3]
                else "Clip unpinned"
            )

        elif action == delete_action:
            self.app.delete_clip(
                self.clip
            )

    def copy_content(self):
        QApplication.clipboard().setText(
            self.clip[2]
        )

        self.app.show_toast(
            "Copied to clipboard"
        )


class ClipPicker(QDialog):
    def __init__(
        self,
        app
    ):
        super().__init__(app)

        self.app = app
        self.drag_position = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(
            560,
            430
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        panel = QFrame()

        panel.setObjectName(
            "pickerPanel"
        )

        panel_layout = QVBoxLayout(
            panel
        )

        panel_layout.setContentsMargins(
            18,
            16,
            18,
            18
        )

        panel_layout.setSpacing(
            10
        )

        title = QLabel(
            "Select a Clip"
        )

        title.setStyleSheet("""
            QLabel {
                color: #f5f5f5;
                font-size: 16px;
                font-weight: 600;
            }
        """)

        panel_layout.addWidget(
            title
        )

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search clips..."
        )

        self.search.setFixedHeight(
            38
        )

        self.search.textChanged.connect(
            self.refresh
        )

        panel_layout.addWidget(
            self.search
        )

        self.list = QListWidget()

        self.list.setSpacing(
            5
        )

        self.list.itemDoubleClicked.connect(
            self.activate_clip
        )

        panel_layout.addWidget(
            self.list
        )

        hint = QLabel(
            "↑ ↓ Navigate   ·   Enter Select   ·   Esc Close"
        )

        hint.setStyleSheet("""
            QLabel {
                color: #68686c;
                font-size: 10px;
            }
        """)

        panel_layout.addWidget(
            hint
        )

        layout.addWidget(
            panel
        )

        self.setStyleSheet("""
            QFrame#pickerPanel {
                background: #1c1c1e;
                border: 1px solid #3c3c3f;
                border-radius: 11px;
            }

            QLineEdit {
                background: #111113;
                border: 1px solid #37373a;
                border-radius: 7px;
                color: #eeeeef;
                padding: 0 11px;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #451ca3;
            }

            QListWidget {
                background: #111113;
                border: 1px solid #353538;
                border-radius: 7px;
                color: #eeeeef;
                outline: none;
                padding: 5px;
            }

            QListWidget::item {
                background: transparent;
                border-radius: 6px;
                padding: 9px;
            }

            QListWidget::item:selected {
                background: #451ca3;
            }

            QListWidget::item:hover {
                background: #29292c;
            }
        """)

        self.refresh()

    def refresh(self):
        self.list.clear()

        clips = self.app.db.get(
            self.search.text().strip()
        )

        for clip in clips:
            item = QListWidgetItem(
                f"{clip[1]}  ·  {clip[4] or 'Other'}"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                clip[0]
            )

            item.setToolTip(
                clip[2]
            )

            self.list.addItem(
                item
            )

        if self.list.count():
            self.list.setCurrentRow(
                0
            )

    def showEvent(self, event):
        super().showEvent(event)

        self.search.setFocus()

        self.refresh()

    def keyPressEvent(self, event):
        if event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            self.activate_clip()

            event.accept()
            return

        super().keyPressEvent(event)

    def activate_clip(self):
        item = self.list.currentItem()

        if not item:
            return

        clip_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        clip = self.app.db.get_by_id(
            clip_id
        )

        if not clip:
            return

        QApplication.clipboard().setText(
            clip[2]
        )

        self.app.select_clip(
            clip[0]
        )

        self.app.show_toast(
            "Copied to clipboard"
        )

        self.accept()

        self.app.paste_clip()

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and event.position().y() <= 55
        ):
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        super().mouseReleaseEvent(event)


class SettingsWindow(QWidget):
    def __init__(
        self,
        app
    ):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
        )

        self.app = app
        self.drag_position = None

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(
            520,
            560
        )

        self.setWindowTitle(
            "Clipsyde Settings"
        )

        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

        container = QFrame()

        container.setObjectName(
            "settingsContainer"
        )

        layout = QVBoxLayout(
            container
        )

        layout.setContentsMargins(
            18,
            12,
            18,
            18
        )

        layout.setSpacing(0)

        titlebar = QWidget()

        titlebar.setFixedHeight(
            32
        )

        titlebar_layout = QHBoxLayout(
            titlebar
        )

        titlebar_layout.setContentsMargins(
            1,
            0,
            0,
            0
        )

        titlebar_layout.setSpacing(
            7
        )

        close = WindowButton(
            "close",
            titlebar
        )

        titlebar_layout.addWidget(
            close
        )

        title = QLabel(
            "Settings"
        )

        title.setStyleSheet("""
            QLabel {
                color: #f3f3f4;
                font-size: 13px;
                font-weight: 600;
            }
        """)

        titlebar_layout.addWidget(
            title
        )

        titlebar_layout.addStretch()

        layout.addWidget(
            titlebar
        )

        layout.addSpacing(
            16
        )

        danger = QFrame()

        danger.setObjectName(
            "settingsCard"
        )

        danger_layout = QVBoxLayout(
            danger
        )

        danger_layout.setContentsMargins(
            16,
            15,
            16,
            15
        )

        danger_layout.setSpacing(
            10
        )

        danger_title = QLabel(
            "Danger Zone"
        )

        danger_title.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 600;
            }
        """)

        self.confirm_delete = QCheckBox(
            "Require confirmation before clearing all clips"
        )

        self.confirm_delete.setChecked(
            True
        )

        clear = QPushButton(
            "Clear All Clips"
        )

        clear.setFixedHeight(
            36
        )

        clear.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        clear.clicked.connect(
            self.clear_clips
        )

        danger_layout.addWidget(
            danger_title
        )

        danger_layout.addWidget(
            self.confirm_delete
        )

        danger_layout.addWidget(
            clear
        )

        layout.addWidget(
            danger
        )

        layout.addSpacing(
            12
        )

        backup = QFrame()

        backup.setObjectName(
            "settingsCard"
        )

        backup_layout = QVBoxLayout(
            backup
        )

        backup_layout.setContentsMargins(
            16,
            15,
            16,
            15
        )

        backup_layout.setSpacing(
            9
        )

        backup_title = QLabel(
            "Backups"
        )

        backup_title.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 600;
            }
        """)

        self.auto_backup = QCheckBox(
            "Automatically backup database"
        )

        self.auto_backup.setChecked(
            True
        )

        export_button = QPushButton(
            "Export Clips"
        )

        export_button.setFixedHeight(
            36
        )

        export_button.clicked.connect(
            self.app.export_clips
        )

        import_button = QPushButton(
            "Import Clips"
        )

        import_button.setFixedHeight(
            36
        )

        import_button.clicked.connect(
            self.app.import_clips
        )

        backup_layout.addWidget(
            backup_title
        )

        backup_layout.addWidget(
            self.auto_backup
        )

        backup_buttons = QHBoxLayout()

        backup_buttons.setSpacing(
            8
        )

        backup_buttons.addWidget(
            export_button
        )

        backup_buttons.addWidget(
            import_button
        )

        backup_layout.addLayout(
            backup_buttons
        )

        layout.addWidget(
            backup
        )

        layout.addSpacing(
            12
        )

        info = QFrame()

        info.setObjectName(
            "settingsCard"
        )

        info_layout = QVBoxLayout(
            info
        )

        info_layout.setContentsMargins(
            16,
            15,
            16,
            15
        )

        info_layout.setSpacing(
            7
        )

        about = QLabel(
            "About Clipsyde"
        )

        about.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 600;
            }
        """)

        description = QLabel(
            "A simple manual text and snippet manager."
        )

        description.setStyleSheet("""
            QLabel {
                color: #909094;
                font-size: 12px;
            }
        """)

        self.count_label = QLabel()

        self.count_label.setStyleSheet("""
            QLabel {
                color: #77777b;
                font-size: 11px;
            }
        """)

        info_layout.addWidget(
            about
        )

        info_layout.addWidget(
            description
        )

        info_layout.addSpacing(
            4
        )

        info_layout.addWidget(
            self.count_label
        )

        layout.addWidget(
            info
        )

        layout.addStretch()

        root.addWidget(
            container
        )

        self.setStyleSheet("""
            QFrame#settingsContainer {
                background: transparent;
                border: 1px solid #454548;
                border-radius: 10px;
            }

            QFrame#settingsCard {
                background: rgba(28, 28, 30, 245);
                border: 1px solid #353538;
                border-radius: 8px;
            }

            QPushButton {
                background: #252528;
                border: 1px solid #39393c;
                border-radius: 7px;
                color: #eeeeef;
                padding: 0 13px;
                font-size: 12px;
            }

            QPushButton:hover {
                background: #303033;
            }

            QCheckBox {
                color: #bcbcc0;
                font-size: 12px;
            }

            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }

            QCheckBox::indicator:checked {
                background: #451ca3;
                border: 1px solid #451ca3;
                border-radius: 4px;
            }

            QCheckBox::indicator:unchecked {
                background: #202023;
                border: 1px solid #444448;
                border-radius: 4px;
            }
        """)

    def update_count(self):
        count = self.app.db.count()

        self.count_label.setText(
            f"{count} clip"
            f"{'s' if count != 1 else ''} saved"
        )

    def clear_clips(self):
        count = self.app.db.count()

        if count == 0:
            self.app.show_toast(
                "There are no clips to clear"
            )
            return

        if self.confirm_delete.isChecked():
            dialog = ConfirmDialog(
                self,
                "Clear All Clips",
                f"Are you sure you want to delete all {count} "
                f"clip{'s' if count != 1 else ''}?\n\n"
                "This action cannot be undone."
            )

            dialog.move(
                self.geometry().center()
                - dialog.rect().center()
            )

            if (
                dialog.exec()
                != QDialog.DialogCode.Accepted
            ):
                return

        self.app.db.clear()

        self.app.selected_clip_id = None

        self.app.refresh()

        self.update_count()

        self.app.show_toast(
            "All clips cleared"
        )

    def window_button_clicked(
        self,
        symbol
    ):
        if symbol == "close":
            self.close()

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and event.position().y() <= 45
        ):
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#3a3a3d")
        )

        gradient.setColorAt(
            0.35,
            QColor("#242426")
        )

        gradient.setColorAt(
            0.7,
            QColor("#151517")
        )

        gradient.setColorAt(
            1.0,
            QColor("#09090b")
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            gradient
        )

        painter.drawRoundedRect(
            self.rect().adjusted(
                0,
                0,
                -1,
                -1
            ),
            10,
            10
        )

        painter.end()


class AddClipButton(QPushButton):
    def __init__(
        self,
        parent=None
    ):
        super().__init__(parent)

        self.setText(
            "Add Clip"
        )

        self.setIcon(
            make_icon(
                "plus",
                17
            )
        )

        self.setIconSize(
            self.iconSize()
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setObjectName(
            "addButton"
        )

        self.setMinimumHeight(
            36
        )

        self.setMinimumWidth(
            102
        )

        self.setStyleSheet("""
            QPushButton#addButton {
                background: #451ca3;
                border: 1px solid #451ca3;
                border-radius: 7px;
                color: white;
                font-size: 12px;
                font-weight: 600;
                padding: 0 14px 0 10px;
            }

            QPushButton#addButton:hover {
                background: #5124b5;
                border-color: #5124b5;
            }

            QPushButton#addButton:pressed {
                background: #3b178d;
                border-color: #3b178d;
            }
        """)


class Clipsyde(QWidget):
    def __init__(self):
        super().__init__()

        self.db = Database()

        self.drag_position = None
        self.restore_geometry = None
        self.selected_clip_id = None
        self.settings_window = None
        self.picker = None

        self.is_maximised = False
        self.was_minimised = False
        self.animating_window = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Window
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.resize(
            820,
            620
        )

        self.setMinimumSize(
            700,
            520
        )

        self.setWindowTitle(
            "Clipsyde"
        )

        self.build_ui()
        self.setup_shortcuts()
        self.register_global_hotkey()

        self.fade_animation = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        self.fade_animation.setDuration(
            180
        )

        self.fade_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self.close_animation = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        self.close_animation.setDuration(
            180
        )

        self.close_animation.setEasingCurve(
            QEasingCurve.Type.InCubic
        )

        self.close_animation.finished.connect(
            self.finish_close
        )

        self.minimise_opacity = QPropertyAnimation(
            self,
            b"windowOpacity"
        )

        self.minimise_opacity.setDuration(
            120
        )

        self.minimise_opacity.setEasingCurve(
            QEasingCurve.Type.InCubic
        )

        self.minimise_opacity.finished.connect(
            self.finish_minimise
        )

        self.maximise_animation = QPropertyAnimation(
            self,
            b"geometry"
        )

        self.maximise_animation.setDuration(
            280
        )

        self.maximise_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self.maximise_animation.finished.connect(
            self.finish_maximise
        )

        self.restore_animation = QPropertyAnimation(
            self,
            b"geometry"
        )

        self.restore_animation.setDuration(
            280
        )

        self.restore_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self.restore_animation.finished.connect(
            self.finish_restore
        )

        self.show()

        self.center_window()

        self.setWindowOpacity(
            0.0
        )

        QTimer.singleShot(
            20,
            self.animate_open
        )

        QTimer.singleShot(
            250,
            self.make_backup
        )

    def build_ui(self):
        root = QVBoxLayout(self)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

        self.container = QFrame()

        self.container.setObjectName(
            "container"
        )

        container_layout = QVBoxLayout(
            self.container
        )

        container_layout.setContentsMargins(
            18,
            13,
            18,
            16
        )

        container_layout.setSpacing(0)

        titlebar = QWidget()

        titlebar.setFixedHeight(
            30
        )

        titlebar_layout = QHBoxLayout(
            titlebar
        )

        titlebar_layout.setContentsMargins(
            1,
            0,
            1,
            0
        )

        titlebar_layout.setSpacing(4)

        self.close_button = WindowButton(
            "close",
            titlebar
        )

        self.min_button = WindowButton(
            "minimise",
            titlebar
        )

        self.max_button = WindowButton(
            "maximise",
            titlebar
        )

        titlebar_layout.addWidget(
            self.close_button
        )

        titlebar_layout.addWidget(
            self.min_button
        )

        titlebar_layout.addWidget(
            self.max_button
        )

        titlebar_layout.addStretch()

        settings = IconButton(
            "settings",
            titlebar,
            30
        )

        settings.clicked.connect(
            self.open_settings
        )

        titlebar_layout.addWidget(
            settings
        )

        container_layout.addWidget(
            titlebar
        )

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            8,
            0,
            14
        )

        title_container = QHBoxLayout()

        title_container.setSpacing(
            8
        )

        clips_label = QLabel(
            "Clips"
        )

        clips_label.setStyleSheet("""
            QLabel {
                color: #f5f5f5;
                font-size: 23px;
                font-weight: 650;
            }
        """)

        title_container.addWidget(
            clips_label
        )

        self.count_label = QLabel()

        self.count_label.setStyleSheet("""
            QLabel {
                color: #77777b;
                font-size: 11px;
                padding-top: 6px;
            }
        """)

        title_container.addWidget(
            self.count_label
        )

        header.addLayout(
            title_container
        )

        header.addStretch()

        add_button = AddClipButton()

        add_button.clicked.connect(
            self.add_clip
        )

        header.addWidget(
            add_button
        )

        container_layout.addLayout(
            header
        )

        search_layout = QHBoxLayout()

        search_layout.setSpacing(8)

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search clips..."
        )

        self.search.textChanged.connect(
            self.refresh
        )

        search_layout.addWidget(
            self.search
        )

        container_layout.addLayout(
            search_layout
        )

        container_layout.addSpacing(
            12
        )

        main_page = QWidget()

        main_layout = QVBoxLayout(
            main_page
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(0)

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_content = QWidget()

        self.clips_layout = QVBoxLayout(
            self.scroll_content
        )

        self.clips_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.clips_layout.setSpacing(
            7
        )

        self.clips_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll.setWidget(
            self.scroll_content
        )

        main_layout.addWidget(
            self.scroll
        )

        self.status = QLabel()

        self.status.setFixedHeight(
            20
        )

        self.status.setStyleSheet("""
            QLabel {
                color: #77777b;
                font-size: 11px;
                padding-left: 2px;
            }
        """)

        main_layout.addWidget(
            self.status
        )

        container_layout.addWidget(
            main_page,
            1
        )

        root.addWidget(
            self.container
        )

        self.setStyleSheet("""
            QFrame#container {
                background: transparent;
                border: 1px solid #454548;
                border-radius: 10px;
            }

            QLineEdit {
                background: rgba(30, 30, 32, 235);
                border: 1px solid #353538;
                border-radius: 7px;
                padding: 0 13px;
                color: #eeeeef;
                font-size: 13px;
                min-height: 36px;
            }

            QLineEdit:focus {
                border: 1px solid #451ca3;
            }

            QFrame#clipItem {
                background: rgba(28, 28, 30, 245);
                border: 1px solid #343437;
                border-radius: 7px;
                min-height: 72px;
            }

            QFrame#clipItem:hover {
                background: rgba(35, 35, 38, 250);
                border: 1px solid #424246;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 2px 0;
            }

            QScrollBar::handle:vertical {
                background: #3a3a3d;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #4a4a4d;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.refresh()

    def setup_shortcuts(self):
        shortcut = QShortcut(
            QKeySequence("Ctrl+N"),
            self
        )

        shortcut.activated.connect(
            self.add_clip
        )

        shortcut = QShortcut(
            QKeySequence("Ctrl+F"),
            self
        )

        shortcut.activated.connect(
            self.focus_search
        )

        shortcut = QShortcut(
            QKeySequence("Ctrl+,"),
            self
        )

        shortcut.activated.connect(
            self.open_settings
        )

        shortcut = QShortcut(
            QKeySequence("Ctrl+Shift+C"),
            self
        )

        shortcut.activated.connect(
            self.copy_selected
        )

    def focus_search(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.search.setFocus()
        self.search.selectAll()

    def select_clip(self, clip_id):
        self.selected_clip_id = clip_id

        for i in range(
            self.clips_layout.count()
        ):
            widget = (
                self.clips_layout
                .itemAt(i)
                .widget()
            )

            if isinstance(
                widget,
                ClipItem
            ):
                if widget.clip[0] == clip_id:
                    widget.setStyleSheet("""
                        QFrame#clipItem {
                            background: rgba(35, 35, 38, 250);
                            border: 1px solid #451ca3;
                            border-radius: 7px;
                            min-height: 72px;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QFrame#clipItem {
                            background: rgba(28, 28, 30, 245);
                            border: 1px solid #343437;
                            border-radius: 7px;
                            min-height: 72px;
                        }

                        QFrame#clipItem:hover {
                            background: rgba(35, 35, 38, 250);
                            border: 1px solid #424246;
                        }
                    """)

    def copy_selected(self):
        if self.selected_clip_id is None:
            self.show_toast(
                "No clip selected"
            )
            return

        clip = self.db.get_by_id(
            self.selected_clip_id
        )

        if not clip:
            self.selected_clip_id = None
            return

        QApplication.clipboard().setText(
            clip[2]
        )

        self.show_toast(
            "Copied to clipboard"
        )

    def show_toast(self, message):
        toast = Toast(
            self,
            message
        )

        toast.show_toast()

    def open_settings(self):
        if (
            self.settings_window is not None
            and self.settings_window.isVisible()
        ):
            self.settings_window.activateWindow()
            self.settings_window.raise_()
            return

        self.settings_window = SettingsWindow(
            self
        )

        self.settings_window.update_count()

        parent_geometry = self.geometry()

        x = (
            parent_geometry.center().x()
            - self.settings_window.width() // 2
        )

        y = (
            parent_geometry.center().y()
            - self.settings_window.height() // 2
        )

        self.settings_window.move(
            x,
            y
        )

        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def center_window(self):
        screen = self.screen()

        if not screen:
            return

        available = screen.availableGeometry()

        self.move(
            available.x()
            + (
                available.width()
                - self.width()
            ) // 2,
            available.y()
            + (
                available.height()
                - self.height()
            ) // 2
        )

    def animate_open(self):
        self.fade_animation.stop()

        self.fade_animation.setStartValue(
            self.windowOpacity()
        )

        self.fade_animation.setEndValue(
            1.0
        )

        self.fade_animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        rect = self.rect().adjusted(
            0,
            0,
            -1,
            -1
        )

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(
            0.0,
            QColor("#3a3a3d")
        )

        gradient.setColorAt(
            0.35,
            QColor("#242426")
        )

        gradient.setColorAt(
            0.7,
            QColor("#151517")
        )

        gradient.setColorAt(
            1.0,
            QColor("#09090b")
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            gradient
        )

        painter.drawRoundedRect(
            rect,
            10,
            10
        )

        painter.end()

    def mousePressEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and event.position().y() <= 55
        ):
            child = self.childAt(
                event.position().toPoint()
            )

            if isinstance(
                child,
                WindowButton
            ):
                return

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            if not self.is_maximised:
                self.move(
                    event.globalPosition().toPoint()
                    - self.drag_position
                )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and event.position().y() <= 55
        ):
            self.window_button_clicked(
                "maximise"
            )

        super().mouseDoubleClickEvent(event)

    def window_button_clicked(
        self,
        symbol
    ):
        if self.animating_window:
            return

        if symbol == "close":
            self.animate_close()

        elif symbol == "minimise":
            self.animate_minimise()

        elif symbol == "maximise":
            if self.is_maximised:
                self.animate_restore()
            else:
                self.animate_maximise()

    def animate_close(self):
        if self.animating_window:
            return

        self.animating_window = True

        self.close_animation.stop()

        self.close_animation.setStartValue(
            self.windowOpacity()
        )

        self.close_animation.setEndValue(
            0.0
        )

        self.close_animation.start()

    def finish_close(self):
        self.close()

    def animate_minimise(self):
        if self.animating_window:
            return

        self.animating_window = True

        if self.is_maximised:
            self.restore_geometry = (
                self.restore_geometry
                or self.geometry()
            )
        else:
            self.restore_geometry = (
                self.geometry()
            )

        self.minimise_opacity.stop()

        self.minimise_opacity.setStartValue(
            self.windowOpacity()
        )

        self.minimise_opacity.setEndValue(
            0.15
        )

        self.minimise_opacity.start()

    def finish_minimise(self):
        self.showMinimized()

        self.setWindowOpacity(
            1.0
        )

        self.is_maximised = False
        self.was_minimised = True
        self.animating_window = False

    def showEvent(self, event):
        super().showEvent(event)

        if self.was_minimised:
            self.was_minimised = False

            self.setWindowOpacity(
                1.0
            )

            if self.restore_geometry:
                self.setGeometry(
                    self.restore_geometry
                )

    def animate_maximise(self):
        if self.animating_window:
            return

        screen = self.screen()

        if not screen:
            return

        self.animating_window = True

        self.restore_geometry = (
            self.geometry()
        )

        self.maximise_animation.stop()

        self.maximise_animation.setStartValue(
            self.geometry()
        )

        self.maximise_animation.setEndValue(
            screen.availableGeometry()
        )

        self.maximise_animation.start()

    def finish_maximise(self):
        self.is_maximised = True
        self.animating_window = False

    def animate_restore(self):
        if self.animating_window:
            return

        if not self.restore_geometry:
            return

        self.animating_window = True

        self.restore_animation.stop()

        self.restore_animation.setStartValue(
            self.geometry()
        )

        self.restore_animation.setEndValue(
            self.restore_geometry
        )

        self.restore_animation.start()

    def finish_restore(self):
        self.is_maximised = False
        self.animating_window = False

    def add_clip(self):
        dialog = ClipDialog(
            self
        )

        dialog.move(
            self.geometry().center()
            - dialog.rect().center()
        )

        if (
            dialog.exec()
            == QDialog.DialogCode.Accepted
        ):
            title, content, category = (
                dialog.get_values()
            )

            if not content.strip():
                return

            self.db.add(
                title,
                content,
                category
            )

            self.make_backup()
            self.refresh()

            self.show_toast(
                "Clip saved"
            )

    def edit_clip(self, clip):
        dialog = ClipDialog(
            self,
            clip
        )

        dialog.move(
            self.geometry().center()
            - dialog.rect().center()
        )

        if (
            dialog.exec()
            == QDialog.DialogCode.Accepted
        ):
            title, content, category = (
                dialog.get_values()
            )

            if not content.strip():
                return

            self.db.update(
                clip[0],
                title,
                content,
                category
            )

            self.make_backup()
            self.refresh()

            self.show_toast(
                "Clip updated"
            )

    def delete_clip(self, clip):
        count = self.db.count()

        dialog = ConfirmDialog(
            self,
            "Delete Clip",
            f"Are you sure you want to delete "
            f"“{clip[1]}”?\n\n"
            "This action cannot be undone."
        )

        dialog.findChild(
            QPushButton,
            "confirmButton"
        ).setText(
            "Delete"
        )

        dialog.move(
            self.geometry().center()
            - dialog.rect().center()
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        self.db.delete(
            clip[0]
        )

        if self.selected_clip_id == clip[0]:
            self.selected_clip_id = None

        self.make_backup()
        self.refresh()

        self.show_toast(
            "Clip deleted"
        )

    def refresh(self):
        while self.clips_layout.count():
            item = (
                self.clips_layout.takeAt(0)
            )

            if item.widget():
                item.widget().deleteLater()

        clips = self.db.get(
            self.search.text().strip()
        )

        self.count_label.setText(
            f"{self.db.count()} clip"
            f"{'s' if self.db.count() != 1 else ''}"
        )

        for clip in clips:
            self.clips_layout.addWidget(
                ClipItem(
                    self,
                    clip
                )
            )

        if not clips:
            empty_container = QWidget()

            empty_layout = QVBoxLayout(
                empty_container
            )

            empty_layout.setContentsMargins(
                0,
                70,
                0,
                70
            )

            empty_layout.setSpacing(
                7
            )

            empty_title = QLabel(
                "No clips yet"
                if not self.search.text().strip()
                else "No clips found"
            )

            empty_title.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty_title.setStyleSheet("""
                QLabel {
                    color: #dddddf;
                    font-size: 15px;
                    font-weight: 600;
                }
            """)

            empty_description = QLabel(
                "Add your first clip to get started."
                if not self.search.text().strip()
                else "Try a different search."
            )

            empty_description.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty_description.setStyleSheet("""
                QLabel {
                    color: #68686c;
                    font-size: 12px;
                }
            """)

            empty_layout.addWidget(
                empty_title
            )

            empty_layout.addWidget(
                empty_description
            )

            self.clips_layout.addWidget(
                empty_container
            )

        if self.selected_clip_id is not None:
            self.select_clip(
                self.selected_clip_id
            )

        if (
            self.settings_window is not None
            and self.settings_window.isVisible()
        ):
            self.settings_window.update_count()

    def export_clips(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Clips",
            "clipsyde-clips.json",
            "JSON Files (*.json)"
        )

        if not filename:
            return

        data = {
            "version": 1,
            "clips": self.db.export_all(),
        }

        try:
            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            self.show_toast(
                "Clips exported"
            )

        except Exception:
            self.show_toast(
                "Export failed"
            )

    def import_clips(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Clips",
            "",
            "JSON Files (*.json)"
        )

        if not filename:
            return

        try:
            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if isinstance(
                data,
                dict
            ):
                clips = data.get(
                    "clips",
                    []
                )
            elif isinstance(
                data,
                list
            ):
                clips = data
            else:
                clips = []

            imported = self.db.import_all(
                clips
            )

            self.make_backup()
            self.refresh()

            self.show_toast(
                f"Imported {imported} clip"
                f"{'s' if imported != 1 else ''}"
            )

        except Exception:
            self.show_toast(
                "Import failed"
            )

    def make_backup(self):
        if (
            self.settings_window is not None
            and self.settings_window.isVisible()
            and not self.settings_window.auto_backup.isChecked()
        ):
            return

        try:
            if not os.path.exists(
                DB_FILE
            ):
                return

            os.makedirs(
                BACKUP_DIR,
                exist_ok=True
            )

            timestamp = datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )

            destination = os.path.join(
                BACKUP_DIR,
                f"clipsyde-backup-{timestamp}.db"
            )

            shutil.copy2(
                DB_FILE,
                destination
            )

            backups = sorted(
                [
                    os.path.join(
                        BACKUP_DIR,
                        file
                    )
                    for file in os.listdir(
                        BACKUP_DIR
                    )
                    if (
                        file.startswith(
                            "clipsyde-backup-"
                        )
                        and file.endswith(
                            ".db"
                        )
                    )
                ],
                key=os.path.getmtime,
                reverse=True
            )

            for old_backup in backups[
                BACKUP_RETENTION:
            ]:
                try:
                    os.remove(
                        old_backup
                    )
                except OSError:
                    pass

        except Exception:
            pass

    def paste_clip(self):
        if sys.platform != "win32":
            return

        try:
            user32 = ctypes.windll.user32

            VK_CONTROL = 0x11
            VK_V = 0x56
            KEYEVENTF_KEYUP = 0x0002

            user32.keybd_event(
                VK_CONTROL,
                0,
                0,
                0
            )

            user32.keybd_event(
                VK_V,
                0,
                0,
                0
            )

            user32.keybd_event(
                VK_V,
                0,
                KEYEVENTF_KEYUP,
                0
            )

            user32.keybd_event(
                VK_CONTROL,
                0,
                KEYEVENTF_KEYUP,
                0
            )

        except Exception:
            pass

    def register_global_hotkey(self):
        if sys.platform != "win32":
            return

        try:
            self.global_hotkey_id = 0x434C4950

            MOD_CONTROL = 0x0002
            MOD_SHIFT = 0x0004
            VK_V = 0x56

            ctypes.windll.user32.RegisterHotKey(
                int(self.winId()),
                self.global_hotkey_id,
                MOD_CONTROL | MOD_SHIFT,
                VK_V
            )

        except Exception:
            self.global_hotkey_id = None

    def unregister_global_hotkey(self):
        if (
            sys.platform != "win32"
            or not hasattr(
                self,
                "global_hotkey_id"
            )
            or self.global_hotkey_id is None
        ):
            return

        try:
            ctypes.windll.user32.UnregisterHotKey(
                int(self.winId()),
                self.global_hotkey_id
            )
        except Exception:
            pass

    def nativeEvent(
        self,
        eventType,
        message
    ):
        if sys.platform == "win32":
            try:
                msg = ctypes.wintypes.MSG.from_address(
                    int(message)
                )

                WM_HOTKEY = 0x0312

                if (
                    msg.message == WM_HOTKEY
                    and msg.wParam
                    == self.global_hotkey_id
                ):
                    self.show_picker()

                    return True, 0

            except Exception:
                pass

        return super().nativeEvent(
            eventType,
            message
        )

    def show_picker(self):
        if (
            self.picker is not None
            and self.picker.isVisible()
        ):
            self.picker.activateWindow()
            self.picker.raise_()
            self.picker.search.setFocus()
            return

        self.picker = ClipPicker(
            self
        )

        screen = self.screen()

        if screen:
            geometry = screen.availableGeometry()

            self.picker.move(
                geometry.center()
                - self.picker.rect().center()
            )

        self.picker.show()
        self.picker.raise_()
        self.picker.activateWindow()
        self.picker.search.setFocus()

    def closeEvent(self, event):
        self.unregister_global_hotkey()

        if (
            self.settings_window is not None
            and self.settings_window.isVisible()
        ):
            self.settings_window.close()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setApplicationName(
        "Clipsyde"
    )

    window = Clipsyde()

    sys.exit(
        app.exec()
    )
