import os
import numpy as np
import pandas as pd
import cv2
from skimage import io, filters, color
from scipy.stats import entropy
from tqdm import tqdm

VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')

def calculate_laplacian_variance(image_gray):
    laplacian = cv2.Laplacian(image_gray, cv2.CV_64F)
    return laplacian.var()

def calculate_entropy(image_gray):
    hist, _ = np.histogram(image_gray, bins=256, range=(0, 255), density=True)
    hist = hist[hist > 0]
    return entropy(hist)

def calculate_sobel_mean(image_gray):
    sobel = filters.sobel(image_gray)
    return np.mean(sobel)

def process_images(directory, output_csv="image_surface_metrics.csv"):
    records = []
    for filename in tqdm(os.listdir(directory)):
        if not filename.lower().endswith(VALID_EXTENSIONS):
            continue

        filepath = os.path.join(directory, filename)
        image = io.imread(filepath)

        if image.ndim == 3:
            image_gray = color.rgb2gray(image)
            image_gray = (image_gray * 255).astype(np.uint8)
        else:
            image_gray = image.astype(np.uint8)

        lap_var = calculate_laplacian_variance(image_gray)
        ent = calculate_entropy(image_gray)
        sobel_mean = calculate_sobel_mean(image_gray)

        records.append({
            "filename": filename,
            "laplacian_variance": lap_var,
            "entropy": ent,
            "sobel_mean": sobel_mean
        })

    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    return df
