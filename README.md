
# Offline Signature Verification System

## Overview

This project implements an offline signature verification system that analyzes handwritten signatures for identity verification. The system segments each signature into 64 cells and extracts various features, including centroids, black-to-white transitions, aspect ratios, skew, and slant angles. This functionality is useful for applications in banking, identity verification, and forensic analysis.

## Features

- **Signature Segmentation**: Divides each signature into 64 distinct segments.
- **Feature Extraction**:
  - Calculates centroids for each segment.
  - Counts black-to-white transitions.
  - Computes aspect ratios of segments.
  - Analyzes skew and slant angles of signatures.
- **File Organization**: Saves extracted features into structured folders for easy access.
- **Stable Cell Identification**: Compares transitions across signatures to identify stable cells.

## Libraries Used

- **PIL (Pillow)**: For image processing and manipulation.
- **NumPy**: For numerical operations and array manipulations.
- **SciPy**: For statistical calculations, including linear regression.

## Getting Started

### Prerequisites

- Python 3.x
- Required libraries: Pillow, NumPy, SciPy

### Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/SignatureVerification.git
   ```
2. Navigate to the project directory:
   ```bash
   cd SignatureVerification
   ```
3. Install the required libraries:
   ```bash
   pip install pillow numpy scipy
   ```

### Usage

1. Place the signature images in the specified folder (e.g., `H:/Lab ML/Reference`).
2. Run the main processing script:
   ```bash
   python signature_verification.py
   ```
3. Check the `Processed` folder for extracted features.
