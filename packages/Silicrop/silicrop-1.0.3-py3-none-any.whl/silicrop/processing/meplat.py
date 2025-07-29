import numpy as np
import cv2
import matplotlib.pyplot as plt


def meplat_detector(contour, window_size=20, error_thresh=1.5, min_length=30, top_n=1000):
    """
    Detect straight segments (meplat) in a contour.

    Args:
        contour (np.ndarray): Array of contour points (Nx2).
        window_size (int): Size of the sliding window for local straightness detection.
        error_thresh (float): Maximum mean squared error (MSE) to consider a segment straight.
        min_length (int): Minimum length of a straight segment.
        top_n (int): Maximum number of segments to return, sorted by length.

    Returns:
        list: List of tuples representing the start and end indices of straight segments.
    """
    is_straight = np.zeros(len(contour), dtype=bool)

    # Mark locally straight points using a sliding window
    for i in range(len(contour) - window_size):
        window = contour[i:i + window_size]
        x = window[:, 0]
        y = window[:, 1]

        # Fit a line to the points in the window
        A = np.vstack([x, np.ones_like(x)]).T
        m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        y_fit = m * x + c
        mse = np.mean((y - y_fit) ** 2)

        # Mark points as straight if the error is below the threshold
        if mse < error_thresh:
            is_straight[i:i + window_size] = True

    # Extract consecutive straight segments
    segments = []
    start = None
    for i, val in enumerate(is_straight):
        if val and start is None:
            start = i
        elif not val and start is not None:
            end = i
            if (end - start) >= min_length:
                segments.append((start, end))
            start = None
    if start is not None and (len(contour) - start) >= min_length:
        segments.append((start, len(contour)))

    # Sort segments by descending length
    segments = sorted(segments, key=lambda s: s[1] - s[0], reverse=True)

    # Keep only the top N segments
    return segments[:top_n]


def find_connected_flat_block(segments, gap_tolerance=5):
    """
    Find the largest connected block of straight segments.

    Args:
        segments (list): List of tuples representing straight segments.
        gap_tolerance (int): Maximum gap allowed between consecutive segments.

    Returns:
        tuple: Start index, end index, and the largest connected block of segments.
    """
    if not segments:
        return None, None, []

    segments = sorted(segments)
    blocks = []
    current_block = [segments[0]]

    for i in range(1, len(segments)):
        prev_end = current_block[-1][1]
        curr_start, curr_end = segments[i]
        if abs(curr_start - prev_end) <= gap_tolerance:
            current_block.append((curr_start, curr_end))
        else:
            blocks.append(current_block)
            current_block = [segments[i]]
    blocks.append(current_block)

    def block_length(block):
        return block[-1][1] - block[0][0]

    largest_block = max(blocks, key=block_length)

    # Expand the largest block by connecting adjacent blocks
    i = blocks.index(largest_block)
    start_idx = i
    end_idx = i

    while start_idx > 0:
        prev_block = blocks[start_idx - 1]
        if abs(prev_block[-1][1] - largest_block[0][0]) <= gap_tolerance:
            largest_block = prev_block + largest_block
            start_idx -= 1
        else:
            break

    while end_idx < len(blocks) - 1:
        next_block = blocks[end_idx + 1]
        if abs(largest_block[-1][1] - next_block[0][0]) <= gap_tolerance:
            largest_block = largest_block + next_block
            end_idx += 1
        else:
            break

    global_start = largest_block[0][0]
    global_end = largest_block[-1][1]
    return global_start, global_end, largest_block


def extract_meplat_parts(contour, window_size=20, error_thresh=1.5, min_length=30, gap_tolerance=5, top_n=20):
    """
    Extract flat and curved parts of a contour.

    Args:
        contour (np.ndarray): Array of contour points (Nx2).
        window_size (int): Size of the sliding window for local straightness detection.
        error_thresh (float): Maximum mean squared error (MSE) to consider a segment straight.
        min_length (int): Minimum length of a straight segment.
        gap_tolerance (int): Maximum gap allowed between consecutive segments.
        top_n (int): Maximum number of segments to return, sorted by length.

    Returns:
        tuple: Binary mask for flat parts, flat part points, and curved part points.
    """
    segments = meplat_detector(
        contour, window_size=window_size, error_thresh=error_thresh,
        min_length=min_length, top_n=top_n
    )
    flat_start, flat_end, _ = find_connected_flat_block(segments, gap_tolerance=gap_tolerance)

    mask_flat = np.zeros(len(contour), dtype=bool)
    mask_flat[flat_start:flat_end] = True

    flat_part = contour[mask_flat]
    curved_part = contour[~mask_flat]

    return mask_flat, flat_part, curved_part


if __name__ == "__main__":
    import os

    image_path = r"C:\Users\TM273821\Desktop\Database\mask.png"
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    mask = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError("Unable to read the image")

    _, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if not contours:
        raise ValueError("No contours found in the image")

    contour = max(contours, key=cv2.contourArea)[:, 0, :]

    # === Detect flat and curved parts
    mask_flat, flat_part, curved_part = extract_meplat_parts(contour)

    # === Visualization
    plt.figure(figsize=(10, 5))
    plt.imshow(mask, cmap='gray')
    plt.plot(curved_part[:, 0], curved_part[:, 1], 'blue', linewidth=1.5, label='Curved')
    plt.plot(flat_part[:, 0], flat_part[:, 1], 'yellow', linewidth=3, label='Flat (Meplat)')
    plt.legend()
    plt.title("Flat vs Curved Parts")
    plt.axis('off')
    plt.tight_layout()
    plt.show()