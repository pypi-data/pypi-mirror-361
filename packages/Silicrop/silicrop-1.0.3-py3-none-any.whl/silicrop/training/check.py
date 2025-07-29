import os

def compare_images_and_masks(image_dir, mask_dir):
    """
    Compare image files and mask files in the given directories.
    
    Args:
        image_dir (str): Path to the directory containing image files.
        mask_dir (str): Path to the directory containing mask files.
    
    Returns:
        tuple: A tuple containing two sets:
            - Images without corresponding masks.
            - Masks without corresponding images.
    """
    # Allowed extensions for images and masks
    image_exts = [".jpg", ".jpeg", ".png"]
    mask_exts = [".png", ".jpg", ".jpeg"]

    # Helper function to list files without extensions
    def list_files_no_ext(directory, allowed_exts):
        files = []
        for f in os.listdir(directory):
            name, ext = os.path.splitext(f)
            if ext.lower() in allowed_exts:
                files.append(name)
        return set(files)

    # Get file names without extensions
    image_names = list_files_no_ext(image_dir, image_exts)
    mask_names = list_files_no_ext(mask_dir, mask_exts)

    # Compare image and mask names
    images_without_masks = image_names - mask_names
    masks_without_images = mask_names - image_names

    return images_without_masks, masks_without_images

# Example usage
if __name__ == "__main__":
    image_dir = r"C:\Users\TM273821\Desktop\Database\200\Image"
    mask_dir = r"C:\Users\TM273821\Desktop\Database\200\Masque_plat"

    images_without_masks, masks_without_images = compare_images_and_masks(image_dir, mask_dir)

    # Print results
    print("Images without corresponding masks:")
    for name in sorted(images_without_masks):
        print(f" - {name}")

    print("\nMasks without corresponding images:")
    for name in sorted(masks_without_images):
        print(f" - {name}")