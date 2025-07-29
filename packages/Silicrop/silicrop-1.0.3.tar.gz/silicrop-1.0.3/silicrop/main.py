# Launcher for the Silicrop application

from PyQt5.QtWidgets import QApplication
import sys
from silicrop.layout.components import ImageProcessorApp
from silicrop.layout.theme import apply_light_theme

def main():
    # Create the application instance
    app = QApplication(sys.argv)
    
    # Apply the light theme to the application
    apply_light_theme(app)
    
    # Create and display the main window
    window = ImageProcessorApp()
    window.show()

    # Execute the application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()