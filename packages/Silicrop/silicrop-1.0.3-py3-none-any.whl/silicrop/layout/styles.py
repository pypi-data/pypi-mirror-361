def drag_drop_area_style():
    return """
        QLabel {
            border: 2px dashed #89CFF0;
            background-color: #F0F8FF;
            font-size: 16px;
            color: #3A3A3A;
            padding: 10px;
        }
    """

def list_widget_style():
    return """
        QListWidget {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            font-size: 14px;
        }
    """

def frame_style():
    return """
        QFrame {
            border: 1px solid #B0C4DE;
            background-color: #FAFAFA;
        }
    """

def button_style():
    return """
        QPushButton {
            background-color: #D0E9FF;
            color: #003366;
            padding: 10px 20px;
            border: 1px solid black;
            border-radius: 6px;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #B0D9F5;
        }
    """

def button_style_model():
    return """
        QPushButton {
            background-color: #4CAF50;
            color: black;  /* Noir comme demandé */
            padding: 10px 20px;
            border: 1px solid black;
            border-radius: 6px;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """

def toggle_button_style():
    return """
        QPushButton {
            background-color: #E6F2FF;
            color: #003366;
            padding: 8px 16px;
            border: 1px solid black;
            border-radius: 6px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #CDE7FF;
        }
        QPushButton:checked {
            background-color: #0078D7;
            color: white;
            border: 1px solid black;
        }
    """

def label_style():
    return """
        QLabel {
            font-size: 14px;
            color: #333;
        }
    """

def flat_button_style():
    return """
        QPushButton {
            background-color: #F8F8F8;
            color: #003366;
            padding: 8px 16px;
            border: 1px solid black;
            border-radius: 6px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #DCEEFF;
        }
        QPushButton:checked {
            background-color: #0078D7;
            color: white;
            border: 1px solid black;
        }
    """

def button_scale_active():
    return """
        QPushButton {
            background-color: #A8E6A1;
            color: #064B00;
            padding: 10px 20px;
            border: 1px solid black;
            border-radius: 6px;
            font-size: 15px;
        }
    """

def button_scale_inactive():
    return """
        QPushButton {
            background-color: #F8D7DA;
            color: #721C24;
            padding: 10px 20px;
            border: 1px solid black;
            border-radius: 6px;
            font-size: 15px;
        }
    """
