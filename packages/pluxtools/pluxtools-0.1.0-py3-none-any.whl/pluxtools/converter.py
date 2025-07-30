import os
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

def extract_plux(plux_path):
    base_name = os.path.splitext(os.path.basename(plux_path))[0]
    output_base = os.path.dirname(plux_path)
    extract_dir = os.path.join(output_base, base_name)
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(plux_path, 'r') as z:
        z.extractall(extract_dir)

    return extract_dir

def get_image_dimensions(index_path):
    tree = ET.parse(index_path)
    root = tree.getroot()
    width = int(root.find(".//IMAGE_SIZE_X").text)
    height = int(root.find(".//IMAGE_SIZE_Y").text)
    return width, height

def get_stack_filename(index_path):
    tree = ET.parse(index_path)
    root = tree.getroot()
    filename = root.find(".//FILENAME_STACK").text
    if not filename:
        raise ValueError("FILENAME_STACK not found or empty in index.xml")
    return filename.strip()

def load_raw_image(raw_path, width, height):
    filesize = os.path.getsize(raw_path)
    expected_pixels = width * height

    if filesize == expected_pixels:
        dtype, mode = np.uint8, 'L'
    elif filesize == expected_pixels * 2:
        dtype, mode = np.uint16, 'I;16'
    elif filesize == expected_pixels * 3:
        dtype, mode = np.uint8, 'RGB'
    else:
        raise ValueError(f"Cannot match raw file size ({filesize} bytes) with expected dimensions: {width}x{height}")

    with open(raw_path, "rb") as f:
        data = np.frombuffer(f.read(), dtype=dtype)
        img_array = data.reshape((height, width) if mode != 'RGB' else (height, width, 3))
        return Image.fromarray(img_array, mode)

def process_plux_file(plux_path, output_dir=None):
    extract_dir = extract_plux(plux_path)
    base_name = os.path.splitext(os.path.basename(plux_path))[0]
    output_dir = output_dir or extract_dir

    index_path = os.path.join(extract_dir, "index.xml")
    raw_filename = get_stack_filename(index_path)
    raw_path = os.path.join(extract_dir, raw_filename)

    if not os.path.exists(index_path) or not os.path.exists(raw_path):
        raise FileNotFoundError(f"Required index.xml or {raw_filename} not found in: {extract_dir}")

    width, height = get_image_dimensions(index_path)
    img = load_raw_image(raw_path, width, height)

    os.makedirs(output_dir, exist_ok=True)
    img.save(os.path.join(output_dir, f"{base_name}.png"))
    img.save(os.path.join(output_dir, f"{base_name}.tiff"))

    return os.path.join(output_dir, f"{base_name}.png")
