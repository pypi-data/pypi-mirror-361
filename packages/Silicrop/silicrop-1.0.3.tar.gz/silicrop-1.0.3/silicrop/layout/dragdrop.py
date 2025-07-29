import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt


class FileDropListWidget(QListWidget):
    def __init__(self, on_files_dropped=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.on_files_dropped = on_files_dropped
        self.placeholder_item = None
        self.show_placeholder()

    def show_placeholder(self):
        self.clear()
        self.placeholder_item = QListWidgetItem("🡇 Drag and Drop Images Below 🡇")
        self.placeholder_item.setFlags(Qt.NoItemFlags)
        self.placeholder_item.setForeground(Qt.gray)
        self.addItem(self.placeholder_item)

    def hide_placeholder(self):
        if self.placeholder_item:
            self.takeItem(self.row(self.placeholder_item))
            self.placeholder_item = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        added = False
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path) and file_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")):
                    file_name = os.path.basename(file_path)
                    item = QListWidgetItem(file_name)
                    item.setData(Qt.UserRole, file_path)
                    self.hide_placeholder()
                    self.addItem(item)
                    if self.on_files_dropped:
                        self.on_files_dropped(file_path)
                    added = True
        if not added and self.count() == 0:
            self.show_placeholder()
        event.acceptProposedAction()


class FileDropListPanel(QWidget):
    def __init__(self, on_files_dropped=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 📘 Instruction message
        self.hint_label = QLabel("📂 Drag and drop images here (.jpg, .png...)")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("color: #555; font-style: italic;")

        # 📋 List widget
        self.list_widget = FileDropListWidget(on_files_dropped)
        self.list_widget.setStyleSheet("font-size: 13px;")

        # 🧹 Action buttons
        button_layout = QHBoxLayout()
        delete_selected_btn = QPushButton("🗑 Delete Selected")
        delete_all_btn = QPushButton("🧹 Delete All")

        delete_selected_btn.clicked.connect(self.remove_selected)
        delete_all_btn.clicked.connect(self.remove_all)

        button_layout.addWidget(delete_selected_btn)
        button_layout.addWidget(delete_all_btn)

        # 📦 Add to layout
        layout.addWidget(self.hint_label)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

    def remove_selected(self):
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))
        if self.list_widget.count() == 0:
            self.list_widget.show_placeholder()

    def remove_all(self):
        self.list_widget.clear()
        self.list_widget.show_placeholder()

    def get_list_widget(self):
        return self.list_widget
