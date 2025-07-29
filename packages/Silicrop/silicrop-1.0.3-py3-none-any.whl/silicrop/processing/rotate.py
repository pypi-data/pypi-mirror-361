"""
Manages the rotation of an image based on user clicks, supporting both point and line rotations.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import cv2
import numpy as np
from silicrop.processing.utils import MouseNavigationHandler


class Rotate(QWidget):
    def __init__(self, width=500, height=500, filter_200_button=None, filter_150_button=None):
        super().__init__()
        self.setFixedSize(width, height)

        # Set up the layout and canvas
        layout = QVBoxLayout(self)
        self.fig, self.ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
        plt.close(self.fig) 
        
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Initialize attributes
        self.image = None
        self._base_image = None
        self.rotation_point = None
        self.rotation_points = []
        self.processed_ellipse = None
        self.filter_200_button = filter_200_button
        self.filter_150_button = filter_150_button

        # Configure the axis and connect events
        self.ax.axis('off')
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.mouse_nav = MouseNavigationHandler(self.canvas, self.ax)

    def set_image(self, image):
        """Set the input image and reset rotation points."""
        if image is None:
            return
        self._base_image = image.copy()
        self.image = image.copy()
        self.rotation_point = None
        self.rotation_points = []
        self.draw()

    def draw(self):
        """Draw the image and rotation points/lines on the canvas."""
        self.ax.clear()
        self.ax.axis('off')
        if self.image is not None:
            img_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.ax.imshow(img_rgb)
            self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Draw the red point if filter_200 is active
        if self.filter_200_button and self.filter_200_button.isChecked():
            if self.rotation_point:
                x, y = self.rotation_point
                self.ax.plot(x, y, 'ro')

        # Draw the line if filter_150 is active
        if self.filter_150_button and self.filter_150_button.isChecked():
            if len(self.rotation_points) == 1:
                x, y = self.rotation_points[0]
                self.ax.plot(x, y, 'ro')
            elif len(self.rotation_points) == 2:
                x_vals = [p[0] for p in self.rotation_points]
                y_vals = [p[1] for p in self.rotation_points]
                self.ax.plot(x_vals, y_vals, 'ro-')

        self.canvas.draw()

    def clear(self):
        """Clear the image and reset rotation points."""
        self.image = None
        self.rotation_point = None
        self.rotation_points = []
        self.draw()

    def on_click(self, event):
        """Handle mouse click events for rotation."""
        if event.inaxes != self.ax:
            return

        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        if self.filter_150_button and self.filter_150_button.isChecked():
            # Line mode: store up to 2 points
            if len(self.rotation_points) < 2:
                self.rotation_points.append((x, y))
            else:
                self.rotation_points = [(x, y)]  # Reset if more than 2 points

            # Apply rotation if 2 points are selected
            if len(self.rotation_points) == 2:
                self.rotate_line_to_horizontal()
        else:
            # Single point mode (filter_200)
            self.rotation_point = (x, y)
            self.rotate_image_point_to_bottom_center()

        self.draw()

    def rotate_line_to_horizontal(self):
        """
        Rotate the image so that the line joining rotation_points[0] and rotation_points[1]
        is horizontal (parallel to the X-axis), using the midpoint as the angle reference.
        """
        if self.image is None or len(self.rotation_points) != 2:
            return

        img = self.image.copy()
        h, w = img.shape[:2]
        cx, cy = w / 2, h / 2

        # Calculate the midpoint
        (x1, y1), (x2, y2) = self.rotation_points
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2

        # Vectors: center → midpoint and center → bottom-center
        dx1, dy1 = mx - cx, my - cy
        dx2, dy2 = 0, h - cy
        ang1 = np.arctan2(dy1, dx1)
        ang2 = np.arctan2(dy2, dx2)
        angle_to_rotate = np.degrees(ang1 - ang2)

        # Rotate around the center (high-quality interpolation)
        M = cv2.getRotationMatrix2D((cx, cy), angle_to_rotate, 1.0)
        rotated = cv2.warpAffine(
            img, M, (w, h),
            flags=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_REPLICATE
        )

        # Optional: Apply a circular white mask
        mask = np.zeros((h, w), dtype=np.uint8)
        radius = int(min(cx, cy))
        cv2.circle(mask, (int(cx), int(cy)), radius, 255, -1)
        white_bg = np.full_like(rotated, 255)
        mask3 = mask[:, :, None]
        result = np.where(mask3 == 255, rotated, white_bg)

        # Update the displayed image
        self.image = result
        self.processed_ellipse = result
        self.rotation_points = []

    def rotate_image_point_to_bottom_center(self):
        """
        Rotate the image so that the selected point is aligned with the bottom-center of the image.
        """
        if self.image is None or self.rotation_point is None:
            return

        img = self.image.copy()
        img_h, img_w = img.shape[:2]
        cx, cy = img_w / 2, img_h / 2
        px, py = self.rotation_point

        # Vector: center → clicked point
        dx1, dy1 = px - cx, py - cy

        # Vector: center → bottom-center
        dx2, dy2 = 0, img_h - cy

        # Calculate the angle between the two vectors
        angle1 = np.arctan2(dy1, dx1)
        angle2 = np.arctan2(dy2, dx2)
        angle_to_rotate = np.degrees(angle1 - angle2)

        # Rotate the image
        center = (int(cx), int(cy))
        M = cv2.getRotationMatrix2D(center, angle_to_rotate, 1.0)
        rotated = cv2.warpAffine(img, M, (img_w, img_h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)

        # Apply a circular white mask
        mask = np.zeros((img_h, img_w), dtype=np.uint8)
        radius = int(min(cx, cy))
        cv2.circle(mask, center, radius, 255, thickness=-1)

        white_bg = np.full_like(rotated, 255, dtype=np.uint8)
        mask_3c = mask[:, :, None]
        masked_img = np.where(mask_3c == 255, rotated, white_bg)

        self.image = masked_img
        self.processed_ellipse = masked_img

    def save_processed_image(self):
        """Save the current displayed image (processed or raw) to a file."""
        image_to_save = self.image if self.image is not None else self._base_image

        if image_to_save is None:
            return  # Nothing to save

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            cv2.imwrite(file_path, image_to_save)
            cv2.imwrite(file_path, image_to_save)