import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from torchvision import transforms
from PIL import ImageEnhance
from PIL import Image, ImageOps
import random
import time
import matplotlib.pyplot as plt
import segmentation_models_pytorch as smp
import ctypes


# Empêche la mise en veille (veille automatique + écran)
ctypes.windll.kernel32.SetThreadExecutionState(
    0x80000002  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
)


save_path = r"C:\Users\TM273821\Desktop\Silicrop - Database\Model\MoS2.pth"
# Start timer
start_time = time.time()

# Check CUDA availability
print(torch.cuda.is_available())  # True = OK
print(torch.cuda.device_count())  # Number of GPUs detected

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Dataset and DataLoader
images_dir = r'C:\Users\TM273821\Desktop\Database\200\Image'
masks_dir = r'C:\Users\TM273821\Desktop\Database\200\Masque_plat'
iou_total= 0

def iou_score(pred, target, threshold=0.5, smooth=1e-6):
    pred = torch.sigmoid(pred)
    pred = (pred > threshold).float()
    target = target.float()

    intersection = (pred * target).sum(dim=(1, 2, 3))  # somme pixel-wise
    union = pred.sum(dim=(1, 2, 3)) + target.sum(dim=(1, 2, 3)) - intersection

    iou = (intersection + smooth) / (union + smooth)
    return iou.mean().item()  # moyenne sur le batch
# ==== 1. Dataset ====# ==== 1. Dataset ====

def dice_loss(pred, target, smooth=1):
    """Calculate the Dice loss."""
    pred = torch.sigmoid(pred)
    pred = pred.view(-1)
    target = target.view(-1)
    intersection = (pred * target).sum()
    return 1 - (2. * intersection + smooth) / (pred.sum() + target.sum() + smooth)

def bce_dice_loss(pred, target):
    bce = F.binary_cross_entropy_with_logits(pred, target, pos_weight=torch.tensor([2.0]).to(pred.device))
    dice = dice_loss(pred, target)
    return bce + dice

class SegmentationDataset(Dataset):
    """Custom dataset for image segmentation."""
    def __init__(self, images_dir, masks_dir, transform=None):
        self.images = sorted([os.path.join(images_dir, f) for f in os.listdir(images_dir) if not f.startswith('.')])
        self.masks = sorted([os.path.join(masks_dir, f) for f in os.listdir(masks_dir) if not f.startswith('.')])
        self.transform = transform

    def __len__(self):
        return len(self.images)
    
    def augment(self, image, mask):
        """Apply synchronized augmentations to the image and mask."""
        # Resize both image and mask
        image = TF.resize(image, (256, 256))
        mask = TF.resize(mask, (256, 256), interpolation=Image.NEAREST)
        
        # Horizontal flip
        if random.random() > 0.5:
            image = TF.hflip(image)
            mask = TF.hflip(mask)
        # Vertical flip
        if random.random() > 0.5:
            image = TF.vflip(image)
            mask = TF.vflip(mask)
        # Random rotation
        angle = random.uniform(-20, 20)
        image = TF.rotate(image, angle)
        mask = TF.rotate(mask, angle, interpolation=Image.NEAREST)

        return image, mask

    def __getitem__(self, idx):
        """Load and preprocess an image-mask pair."""
        image = Image.open(self.images[idx])
        image = ImageOps.exif_transpose(image)
        image = image.convert('RGB')
        mask = Image.open(self.masks[idx]).convert('L')

        # Apply augmentations
        image, mask = self.augment(image, mask)

        # Convert to tensors
        image = TF.to_tensor(image)
        mask = TF.to_tensor(mask)
        mask = (mask > 0.5).float()  # Plus strict, plus clair

        return image, mask



# ==== 2. Mini U-Net ====# ==== 2. Mini U-Net ====

dataset = SegmentationDataset(images_dir, masks_dir)
loader = DataLoader(dataset, batch_size=1, shuffle=True)


class SimpleUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc1 = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.enc2 = nn.Sequential(
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.up = nn.ConvTranspose2d(64, 32, 2, stride=2)
        self.dec1 = nn.Sequential(
            nn.Conv2d(64, 32, 3, padding=1), nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1), nn.ReLU()
        )
        self.final = nn.Conv2d(32, 1, 1)

    def forward(self, x):
        x1 = self.enc1(x)
        x2 = self.enc2(x1)
        x_up = self.up(x2)
        x_cat = torch.cat([x1, x_up], dim=1)
        x3 = self.dec1(x_cat)
        out = self.final(x3)
        out = F.interpolate(out, size=(256, 256), mode='bilinear', align_corners=False)
        return out

# ==== 3. Training ====# ==== 3. Train ====

# model = SimpleUNet().to(device)

model = smp.Unet(
    encoder_name="resnet18",      # ou "efficientnet-b0", "resnet34", etc.
    encoder_weights="imagenet",   # Utilise les poids pré-entraînés sur ImageNet
    in_channels=3,                # Nombre de canaux en entrée (3 pour RGB)
    classes=1                     # 1 canal de sortie pour binaire
).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

pos_weight = torch.tensor([5.0]).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

EPOCHS = 100

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for images, masks in loader:
        images = images.to(device)
        masks = masks.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = bce_dice_loss(outputs, masks)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        iou_total += iou_score(outputs, masks)  # ✅ pas de .item()
    
    avg_loss = total_loss / len(loader)
    avg_iou = iou_total / len(loader)

    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {avg_loss:.4f} - IoU: {avg_iou:.4f}")

# Save the model
torch.save(model.state_dict(), save_path)

# ==== 4. Visualization ====# ==== 4. Visualisation sur un batch ====

model.eval()
all_images, all_masks, all_preds = [], [], []

for images, masks in loader:
    images = images.to(device)
    with torch.no_grad():
        logits = model(images)
        probs = torch.sigmoid(logits)
        preds = (probs > 0.5).float()
    all_images.append(images.cpu())
    all_masks.append(masks.cpu())
    all_preds.append(preds.cpu())

# Concatenate all batches
all_images = torch.cat(all_images, dim=0)
all_masks = torch.cat(all_masks, dim=0)
all_preds = torch.cat(all_preds, dim=0)

# End timer
end_time = time.time()
print(f"Training time: {end_time - start_time:.2f} seconds")


# ==== 5. Test sur 10 images aléatoires ====
import random

model.eval()

# Sélectionner 10 indices aléatoires
test_indices = random.sample(range(len(dataset)), 10)

# Créer une figure pour l'affichage
for i, idx in enumerate(test_indices):
    image, mask = dataset[idx]
    image_input = image.unsqueeze(0).to(device)  # Ajouter batch dimension

    with torch.no_grad():
        output = model(image_input)
        prob = torch.sigmoid(output)
        pred = (prob > 0.5).float()

    # Convertir en format affichable
    image_np = image.permute(1, 2, 0).cpu().numpy()
    mask_np = mask.squeeze().cpu().numpy()
    pred_np = pred.squeeze().cpu().numpy()

    # Affichage
    plt.figure(figsize=(10, 3))
    plt.suptitle(f"Sample #{idx}")
    
    plt.subplot(1, 3, 1)
    plt.imshow(image_np)
    plt.title("Image")
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.imshow(mask_np, cmap='gray')
    plt.title("Masque réel")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.imshow(pred_np, cmap='gray')
    plt.title("Prédiction")
    plt.axis("off")

    plt.tight_layout()
    plt.show()
