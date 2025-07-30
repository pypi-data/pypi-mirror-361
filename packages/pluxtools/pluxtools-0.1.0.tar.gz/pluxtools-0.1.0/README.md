# PLUXTools
**PLUXTools** – A utility for converting `.plux` surface metrology archives and calculating quantitative heterogeneity metrics  
***

A Python-based module for automated conversion of Sensofar `.plux` topography data into usable image formats (PNG and TIFF), followed by optional surface texture analysis using image-derived metrics.

- [Basic usage](#basic-usage)  
- [Heterogeneity metrics](#heterogeneity-metrics)  
- [Installation instructions](#installation-instructions)
- [Dependencies](#dependencies)
- [Output and structure](#output-and-structure)  
- [Notes](#notes)  
- [License](#license)  

---

## Basic usage

PLUXTools supports `.plux` files containing metrology information and structured surface maps. It extracts the core data using `index.xml` and `.raw` layers, and converts it into common image formats for downstream analysis or publication.

### Conversion only

```bash
python -m pluxtools.convert [input_file.plux]
```
This will:
 1) Extract the .plux archive
 2) Parse image dimensions from `index.xml`
 3) Convert the raw topography (`LAYER_0_stack.raw`) to `.png` and `.tiff` formats

## Heterogeneity metrics

PLUXTools can calculate basic surface texture metrics from extracted images. These metrics provide a summary of spatial heterogeneity and surface roughness.
Metrics calculated

* Laplacian Variance – measure of surface sharpness and detail
* Shannon Entropy – texture randomness and complexity
* Sobel Mean Gradient – average spatial edge strength

### Metric calculation usage

```
python -m pluxtools.metrics [directory_of_images]
```

All supported image formats in the specified directory will be processed, including: `.png`, `.jpg`, `.jpeg`, `.tif`, and `.tiff`

### Example output 
| filename       | laplacian\_variance | entropy | sobel\_mean |
| -------------- | ------------------- | ------- | ----------- |
| sample\_1.png  | 54.23               | 6.22    | 0.0452      |
| sample\_2.tiff | 48.14               | 6.12    | 0.0385      |

## Installation instructions

We recommend using a virtual environment.

### Install via PyPI

```
pip3 install pluxtools

```

### Install from source

```
git clone https://github.com/yourgroup/pluxtools.git
cd pluxtools
pip install -e .

```

## Dependencies

PLUXTools requires the following packages:
* `numpy`
* `pillow`
* `opencv-python`
* `scikit-image`
* `pandas`
* `tqdm`

## Output and structure

All converted image files are saved to the same directory as the input `.plux` archive. Metric outputs are saved as a single `.csv` file summarising calculated features per image.

## Notes
* `.plux` files are ZIP-compressed archives with metadata and binary topography data
* Image dimensions are parsed from `index.xml`
* Bit depth and format are inferred from the size of the `.raw` file
* Only `LAYER_0_stack.raw` is processed
* No manual configuration of dimensions is required

## License

MIT License © DrATedder 2025
