from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QLabel, QListWidget, QFrame, QGridLayout
)
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import cv2
import time
import numpy as np
import os
from PIL import Image, ImageOps
from silicrop.layout.dragdrop import FileDropListPanel
from silicrop.processing.prediction import EllipsePredictor
from silicrop.processing.crop import FitAndCrop
from silicrop.processing.rotate import Rotate
from silicrop.layout.styles import (
    drag_drop_area_style,
    list_widget_style,
    frame_style,
    button_style,
    button_scale_active,
    button_scale_inactive,
    button_style_model
)

class ImageProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Silicrop")
        self.resize(900, 520)
        self.move(0, 0) 

        # Initialize attributes
        self.image_paths = []
        self.filter_150_button = None
        self.filter_200_button = None

        # Set up the main layout
        self.global_layout = QGridLayout(self)
        self.setLayout(self.global_layout)

        # Initialize UI components
        self.scale()
        self.init_left_panel()
        self.init_right_panel()
        self.init_controls()
        self.init_controls_batch()
        self.model_button()

        # Set default model path
        # self.model_path = r"C:\Users\TM273821\Desktop\Silicrop - model\model_200.pth"
        self.model_path = None
       


    def model_button(self):
        self.select_model_button = QPushButton("Sélectionner un modèle")
        self.select_model_button.setStyleSheet(button_style_model())
        self.select_model_button.clicked.connect(self.select_model_path)
        self.global_layout.addWidget(self.select_model_button, 4, 0, alignment=Qt.AlignTop)

    def select_model_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un modèle", "", "Fichiers PyTorch (*.pth *.pt)")
        if path:
            self.model_path = path
            print(f"Modèle sélectionné : {self.model_path}")


    def on_file_dropped(self, path):
        print(f"Fichier ajouté à la liste : {path}")

    def init_left_panel(self):
        self.drop_panel = FileDropListPanel(on_files_dropped=self.on_file_dropped)
        self.list_widget = self.drop_panel.get_list_widget()
        self.list_widget.itemSelectionChanged.connect(self.display_selected_image)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.drop_panel)

        container = QWidget()
        container.setLayout(left_layout)
        self.global_layout.addWidget(container, 0, 0, 2, 1)

    def init_right_panel(self):
        """Initialize the right panel with original and processed image frames."""
        # Original image frame
        self.original_frame = QFrame()
        self.original_frame.setStyleSheet(frame_style())
        self.original_frame.setFixedSize(700, 700)
        original_layout = QVBoxLayout()
        self.original_frame.setLayout(original_layout)

        # Processed image frame
        self.processed_frame = QFrame()
        self.processed_frame.setStyleSheet(frame_style())
        self.processed_frame.setFixedSize(700, 700)
        processed_layout = QVBoxLayout()
        self.processed_frame.setLayout(processed_layout)

        # Set layout margins and spacing
        original_layout.setContentsMargins(0, 0, 0, 0)
        original_layout.setSpacing(0)
        processed_layout.setContentsMargins(0, 0, 0, 0)
        processed_layout.setSpacing(0)

        # Initialize widgets
        self.processed_widget = Rotate(700, 700, filter_200_button=self.filter_200_button, filter_150_button=self.filter_150_button)
        processed_layout.addWidget(self.processed_widget)

        self.original_widget = FitAndCrop(self.processed_widget, 700, 700, filter_200_button=self.filter_200_button, filter_150_button=self.filter_150_button, header=True)
        original_layout.addWidget(self.original_widget)

        # Add frames to the grid layout
        self.global_layout.addWidget(self.original_frame, 0, 1, 2, 1)
        self.global_layout.addWidget(self.processed_frame, 0, 2, 2, 1)

    def init_controls(self):
        """Initialize control buttons for saving masks and images."""
        # Save mask button

        self.IA_button = QPushButton("Run AI")
        self.IA_button.setCheckable(False)
        self.IA_button.setStyleSheet(button_style())
        self.IA_button.clicked.connect(self.run_auto_dl_process)

        self.save_mask_button = QPushButton("Save Mask")
        self.save_mask_button.setStyleSheet(button_style())
        self.save_mask_button.clicked.connect(self.original_widget.save_mask)

        # Save image button
        self.save_image_button = QPushButton("Save Image")
        self.save_image_button.setStyleSheet(button_style())
        self.save_image_button.clicked.connect(self.processed_widget.save_processed_image)

        self.global_layout.addWidget(self.IA_button, 2, 1, 1, 1, alignment=Qt.AlignTop)
        self.global_layout.addWidget(self.save_image_button, 3, 1,  1, 1, alignment=Qt.AlignTop)
        self.global_layout.addWidget(self.save_mask_button, 4, 1,  1, 1, alignment=Qt.AlignTop)
    
    def init_controls_batch(self):
        """Initialize control buttons for saving masks and images."""
        # Save mask button

        self.IA_button_batch = QPushButton("Run AI (batch)")
        self.IA_button_batch.setCheckable(False)
        self.IA_button_batch.setStyleSheet(button_style())
        self.IA_button_batch.clicked.connect(self.run_auto_dl_process_batch)
        self.IA_button_batch.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.global_layout.setRowStretch(2, 1)
        self.global_layout.setRowStretch(3, 1)
        self.global_layout.setRowStretch(4, 1)

        self.global_layout.addWidget(self.IA_button_batch, 2, 2, 3, 1)

    def add_images(self, paths):
        """Add images to the file list."""
        for path in paths:
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                if path not in self.image_paths:
                    self.image_paths.append(path)
                    self.list_widget.addItem(path)

    def display_selected_image(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            # Utilise le chemin complet stocké
            full_path = selected_item.data(Qt.UserRole)
            
            # Exemple avec OpenCV :
            import cv2
            image = cv2.imread(full_path)
            
            if image is None:
                print(f"❌ Échec de lecture : {full_path}")
            else:
                print(f"✅ Image chargée : {full_path}")
                # affiche l'image ou l'envoie à un QLabel etc.

        self.original_widget.set_image(image)
        self.processed_widget.set_image(None)

    def scale(self):
        """Initialize scale filter buttons."""
        self.filter_150_button = QPushButton("<=150")
        self.filter_150_button.setCheckable(True)
        self.filter_150_button.setStyleSheet(button_scale_inactive())
        self.filter_150_button.clicked.connect(lambda checked: self.check_scale_filters(self.filter_150_button))

        self.filter_200_button = QPushButton(">200")
        self.filter_200_button.setCheckable(True)
        self.filter_200_button.setStyleSheet(button_scale_inactive())
        self.filter_200_button.clicked.connect(lambda checked: self.check_scale_filters(self.filter_200_button))

        self.global_layout.addWidget(self.filter_150_button, 2, 0, alignment=Qt.AlignTop)
        self.global_layout.addWidget(self.filter_200_button, 3, 0, alignment=Qt.AlignTop)

    def run_auto_dl_process(self):
        """Run the deep learning process for image prediction and transformation."""
        if not self.model_path:
            print("No model selected. Process aborted.")
            return

        if not hasattr(self, 'fit_crop_widget') or self.fit_crop_widget is None:
            print("FitAndCrop widget not initialized. Process aborted.")
            return

        # Initialize the EllipsePredictor with the model path and fit_crop_widget
        self.ellipse_predictor = EllipsePredictor(self.model_path, self.fit_crop_widget)

        # 🔁 Mode interactif (image déjà chargée depuis QListWidget)
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            print("Aucune image sélectionnée.")
            return
        path = selected_items[0].data(Qt.UserRole)
        
        # 🔮 Inference
        start_time = time.time()
        # ✏️ Fit et warp

        result_img, mask, ellipse = self.ellipse_predictor.run_inference(path, dataset_type='150', plot=False)

        elapsed = time.time() - start_time
        print(f"[{os.path.basename(path)}] Temps total : {elapsed:.3f}s")

        # 🖼️ Sinon affichage dans le widget
        if result_img is not None:
            self.processed_widget.set_image(result_img)
        else:
            print("Erreur : pas d'image résultat.")

        if mask is not None:

            # Assign the processed mask to the widget
            self.original_widget.mask_image = mask
        else:
            print("Erreur : le masque généré est vide")
        
    def run_auto_dl_process_batch(self):
        """Run the deep learning process in batch for all listed images and save the results."""

        # Sélection du dossier de sortie
        output_dir = QFileDialog.getExistingDirectory(self, "Choisir le dossier de sauvegarde")
        if not output_dir or not self.model_path:
            print("Aucun dossier sélectionné. Annulation.")
            return

        # Chargement du modèle une seule fois
        
        if not hasattr(self, "ellipse_predictor"):
            self.ellipse_predictor = EllipsePredictor(self.model_path)

        total = self.list_widget.count()
        print(f"Traitement de {total} images...")

        for i in range(total):
            item = self.list_widget.item(i)
            img_path = item.text()

            if not os.path.isfile(img_path):
                print(f"[{i+1}/{total}] Chemin invalide : {img_path}")
                continue

            img_array = cv2.imread(img_path)
            if img_array is None:
                print(f"[{i+1}/{total}] Impossible de lire : {img_path}")
                continue

            print(f"[{i+1}/{total}] Traitement : {img_path}")
            start_time = time.time()

            # Inférence
            mask = self.ellipse_predictor.predict_mask(img_array)

            # Warp
            result_img = self.ellipse_predictor.fit_and_warp(img_array, mask)
            elapsed = time.time() - start_time

            if result_img is not None:
                base_name = os.path.basename(img_path)
                name_wo_ext = os.path.splitext(base_name)[0]
                save_path = os.path.join(output_dir, f"{name_wo_ext}_processed.png")
                cv2.imwrite(save_path, result_img)
                print(f"  ✔ Enregistré : {save_path}  |  Temps : {elapsed:.2f}s")
            else:
                print(f"  ⚠ Erreur traitement : {img_path}")


    def check_scale_filters(self, clicked_button):
        """Handle scale filter button clicks."""
        if clicked_button == self.filter_150_button:
            self.filter_150_button.setChecked(True)
            self.filter_150_button.setStyleSheet(button_scale_active())

            self.filter_200_button.setChecked(False)
            self.filter_200_button.setStyleSheet(button_scale_inactive())

            print("<=150 activated")

        elif clicked_button == self.filter_200_button:
            self.filter_200_button.setChecked(True)
            self.filter_200_button.setStyleSheet(button_scale_active())

            self.filter_150_button.setChecked(False)
            self.filter_150_button.setStyleSheet(button_scale_inactive())

            print(">200 activated")

        self.fit_crop_widget = FitAndCrop(processed_label=self.processed_widget)
