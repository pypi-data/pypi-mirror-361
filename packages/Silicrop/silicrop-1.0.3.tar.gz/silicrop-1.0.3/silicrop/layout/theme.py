def apply_light_theme(app):
    app.setStyleSheet("""
        QWidget {
            background-color: #f5f7fa;
            color: #2c2c2c;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 13px;
        }

        QPushButton {
            background-color: #e0ecff;
            border: 1px solid #a0c4ff;
            border-radius: 6px;
            padding: 6px 14px;
        }

        QPushButton:hover {
            background-color: #d0e4ff;
        }

        QPushButton:checked {
            background-color: #0078d7;
            color: white;
            border: 1px solid #005fa3;
        }

        QListWidget {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }

        QListWidget::item:selected {
            background-color: #cce4ff;
            color: #000;
        }

        QLabel {
            font-size: 13px;
        }

        QFrame {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 8px;
        }

        QGroupBox {
            border: 1px solid #dddddd;
            border-radius: 8px;
            margin-top: 6px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            font-weight: bold;
        }
    """)
