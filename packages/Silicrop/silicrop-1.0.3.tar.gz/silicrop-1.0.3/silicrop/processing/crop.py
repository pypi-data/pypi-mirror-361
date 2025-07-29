"""
Manage ellipse fitting and cropping.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Ellipse, Polygon
import matplotlib.pyplot as plt
import cv2
from PyQt5.QtCore import Qt
import numpy as np
from silicrop.processing.rotate import Rotate
from silicrop.processing.utils import MouseNavigationHandler

class FitAndCrop(QWidget):
    def __init__(self, processed_label, width=800, height=800, filter_200_button=None, filter_150_button=None,
                 header=False):
        super().__init__()
        self.header = header  # 👈 ajout
        self.processed_widget = processed_label
        self.filter_200_button = filter_200_button
        self.filter_150_button = filter_150_button

                # Initialize attributes
        self.image = None
        self.points = []
        self.ellipse_params = None
        self.mask_image = None
        self.processed_ellipse = None
        self.shift_pressed = False
        self.max_points = 5
        self.tolerance_px = 300
        self.scale = 1.0
        self.press_event = None
        self.panning = False

        # Connect filter buttons to the image processing function
        if self.filter_150_button and hasattr(self.filter_150_button, "clicked"):
            self.filter_150_button.clicked.connect(self.process_and_display_corrected_image)

        if self.filter_200_button and hasattr(self.filter_200_button, "clicked"):
            self.filter_200_button.clicked.connect(self.process_and_display_corrected_image)

        if self.header:
            # Set up the layout and canvas only if not headless
            layout = QVBoxLayout(self)
            self.fig, self.ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
            self.canvas = FigureCanvas(self.fig)
            layout.addWidget(self.canvas)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)


            # Mouse navigation handler
            self.mouse_nav = MouseNavigationHandler(self.canvas, self.ax)

            # Configure the axis and connect events
            self.ax.axis('off')
            self.canvas.mpl_connect('button_press_event', self.on_click)
        else:
            # Placeholder attributes to avoid attribute errors
            self.fig = None
            self.ax = None
            self.canvas = None
            self.mouse_nav = None
    
    def is_checked(self, button):
        if hasattr(button, "isChecked"):
            return button.isChecked()
        return bool(button)

    def set_image(self, cv_img):
        """Set the input image and reset points and ellipse parameters."""
        self.image = cv_img
        self.points = []
        self.ellipse_params = None
        self.mask_image = None
        self.processed_ellipse = None

        if self.header and self.ax is not None:
            self.ax.clear()
            self.ax.axis("off")
            if self.image is not None:
                from cv2 import cvtColor, COLOR_BGR2RGB
                img_rgb = cvtColor(self.image, COLOR_BGR2RGB)
                self.ax.imshow(img_rgb)

                # Force the axis limits to match the image dimensions
                height, width = self.image.shape[:2]
                self.ax.set_xlim(0, width)
                self.ax.set_ylim(height, 0)  # Invert y-axis for correct display

            self.canvas.draw()

    def draw_points_and_ellipse(self):
        """Draw points and the fitted ellipse on the canvas."""
        if self.header is None or self.ax is None:
            return  # Do nothing if headless

        self.ax.clear()
        self.ax.axis('off')
        if self.image is not None:
            img_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.ax.imshow(img_rgb)

            # Keep the axis limits fixed to the image dimensions
            height, width = self.image.shape[:2]
            self.ax.set_xlim(0, width)
            self.ax.set_ylim(height, 0)  # Invert y-axis for correct display

        if self.points:
            pts = np.array(self.points)
            self.ax.plot(pts[:, 0], pts[:, 1], 'ro')

        if self.ellipse_params is not None:
            center, axes, angle = self.ellipse_params
            ellipse = Ellipse(center, axes[0], axes[1], angle=angle, edgecolor='b', facecolor='none', linewidth=2)
            self.ax.add_patch(ellipse)

            box_params = (center, (axes[0], axes[1]), angle)
            box_points = cv2.boxPoints(box_params).astype(np.float32)
            polygon = Polygon(box_points, closed=True, edgecolor='g', facecolor='none', linewidth=2)
            self.ax.add_patch(polygon)

        self.canvas.draw()

    def on_click(self, event=None):
        """Handle mouse click events for adding, moving, or removing points."""
        if event is None:
            print("Button clicked - on_click called without event")
            return

        if getattr(self, 'panning', False) or event.inaxes != self.ax:
            return
        
        if self.header is None or self.ax is None:
            return  # ✅ ne fait rien si headless

        ctrl_pressed = hasattr(event, 'guiEvent') and event.guiEvent.modifiers() & Qt.ControlModifier
        if ctrl_pressed:
            return

        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        click_pos = np.array([x, y])

        # Right-click to remove a point
        if event.button == 3:
            for i, pt in enumerate(self.points):
                if np.linalg.norm(click_pos - np.array(pt)) < self.tolerance_px:
                    del self.points[i]
                    self.ellipse_params = None
                    if self.processed_widget:
                        self.processed_widget.clear()
                    self.draw_points_and_ellipse()
                    return

        # Move an existing point
        for i, pt in enumerate(self.points):
            if np.linalg.norm(click_pos - np.array(pt)) < self.tolerance_px:
                self.points[i] = (x, y)
                self.draw_points_and_ellipse()
                if len(self.points) == self.max_points:
                    pts = np.array(self.points, dtype=np.float32)
                    self.ellipse_params = cv2.fitEllipse(pts)
                    self.process_and_display_corrected_image()
                return

        # Add a new point
        if len(self.points) < self.max_points:
            self.points.append((x, y))

        # Fit the ellipse if enough points are added
        if len(self.points) == self.max_points:
            pts = np.array(self.points, dtype=np.float32)
            self.ellipse_params = cv2.fitEllipse(pts)
            self.process_and_display_corrected_image()
        else:
            self.ellipse_params = None
            if self.processed_widget:
                self.processed_widget.clear()

        self.draw_points_and_ellipse()

    def process_and_display_corrected_image(self, points=None):
        """Process the image and display the corrected version."""
        if self.ellipse_params is None or self.image is None:
            return

        if not isinstance(points, (list, np.ndarray)):
            points = self.points

        used_points = points
        (cx, cy), (MA, ma), angle = self.ellipse_params
        mask = np.zeros(self.image.shape[:2], np.uint8)
        cv2.ellipse(mask, (int(cx), int(cy)), (int(MA / 2), int(ma / 2)), angle, 0, 360, 255, -1)

        if len(used_points) == 5 and self.is_checked(self.filter_150_button):
            p1 = tuple(map(int, used_points[0]))
            p5 = tuple(map(int, used_points[4]))
            mask = self.split_ellipse_mask(mask, p1, p5)

        self.mask_image = mask.copy()

        # Perspective transformation
        diameter = int(max(MA, ma))
        pts1 = cv2.boxPoints(self.ellipse_params).astype(np.float32)
        pts2 = np.array([
            [0, 0],
            [diameter - 1, 0],
            [diameter - 1, diameter - 1],
            [0, diameter - 1]
        ], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(self.image, matrix, (diameter, diameter))
        warped_mask = cv2.warpPerspective(mask, matrix, (diameter, diameter))

        # Apply the final mask to the transformed image
        white_bg = np.ones_like(warped, dtype=np.uint8) * 255
        for c in range(3):
            white_bg[:, :, c] = np.where(warped_mask == 255, warped[:, :, c], 255)

        if self.processed_widget:
            self.processed_widget.set_image(white_bg)

        # Draw points on the processed image
        if len(used_points) == 5:
            orig_points = np.array(used_points, dtype=np.float32).reshape(-1, 1, 2)
            projected_points = cv2.perspectiveTransform(orig_points, matrix).reshape(-1, 2)

            self.processed_widget.ax.clear()
            self.processed_widget.ax.axis('off')
            img_rgb = cv2.cvtColor(white_bg, cv2.COLOR_BGR2RGB)
            self.processed_widget.ax.imshow(img_rgb)

            # Draw red points
            xs, ys = projected_points[:, 0], projected_points[:, 1]
            self.processed_widget.ax.plot(xs, ys, 'ro', markersize=7)

            for idx, (xp, yp) in enumerate(projected_points):
                self.processed_widget.ax.text(xp + 2, yp - 2, f'{idx + 1}', color='black', fontsize=12, fontweight='bold')

            self.processed_widget.canvas.draw()
            self.processed_ellipse = white_bg
        else:
            self.processed_widget.set_image(white_bg)
            self.processed_ellipse = white_bg


        # Rotation (optional, only if processed_widget supports it)
        if isinstance(self.processed_widget, Rotate):
            if self.is_checked(self.filter_150_button) and len(used_points) >= 2:
                print("✅ Rotation 150 déclenchée54554")
                orig_pts = np.array([used_points[0], used_points[4]], dtype=np.float32).reshape(-1, 1, 2)
                projected = cv2.perspectiveTransform(orig_pts, matrix).reshape(-1, 2)
                self.processed_widget.rotation_points = [tuple(projected[0]), tuple(projected[1])]
                self.processed_widget.rotate_line_to_horizontal()
                self.processed_widget.draw()

            elif self.is_checked(self.filter_200_button) and len(used_points) >= 1:
                orig_pt = np.array([used_points[0]], dtype=np.float32).reshape(-1, 1, 2)
                projected = cv2.perspectiveTransform(orig_pt, matrix).reshape(-1, 2)
                self.processed_widget.rotation_point = tuple(projected[0])
                self.processed_widget.rotate_image_point_to_bottom_center()
                self.processed_widget.draw()
        else:
            print("processed_widget is not a Rotate instance:", type(self.processed_widget))

    def save_mask(self):
        """Save the mask image to a file."""
        if self.mask_image is None:
            if self.image is None:
                return  # Can't create a mask if we don't know the image size
            height, width = self.image.shape[:2]
            self.mask_image = np.zeros((height, width), dtype=np.uint8)

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Mask", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            cv2.imwrite(file_path, self.mask_image)

    def split_ellipse_mask(self, mask, p1, p5):
        """Split the ellipse mask along the line [p1, p5] and keep the larger part."""
        h, w = mask.shape
        Y, X = np.ogrid[:h, :w]
        x1, y1 = p1
        x2, y2 = p5
        a = y2 - y1
        b = x1 - x2
        c = x2 * y1 - x1 * y2

        side1 = (a * X + b * Y + c) > 0
        side2 = ~side1

        mask1 = np.zeros_like(mask)
        mask2 = np.zeros_like(mask)
        mask1[side1 & (mask > 0)] = 255
        mask2[side2 & (mask > 0)] = 255

        return mask1 if cv2.countNonZero(mask1) > cv2.countNonZero(mask2) else mask2
