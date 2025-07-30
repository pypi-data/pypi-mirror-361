[![CI](https://github.com/ResearchBureau/dicomdiff/actions/workflows/build.yml/badge.svg)](https://github.com/ResearchBureau/dicomdiff/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/dicomdiff)](https://pypi.org/project/dicomdiff/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dicomdiff)](https://pypi.org/project/dicomdiff/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Dicomdiff
A comprehensive Python module for analyzing DICOM file pseudonymization and de-identification processes. Dicomdiff enables researchers and healthcare professionals to evaluate, compare, and validate different pseudonymization methods by providing detailed analysis of how DICOM tags are transformed during de-identification.

## What Dicomdiff Does

**Core Functionality:**
- **Individual File Comparison**: Compare original DICOM files with their de-identified versions to detect specific changes
- **Pseudonymization Method Analysis**: Evaluate and compare different pseudonymization approaches across multiple files
- **Cross-Method Comparison**: Analyze how different pseudonymization tools handle the same source data
- **Consistency Validation**: Check whether pseudonymization methods behave consistently across datasets
- **Tag Transformation Tracking**: Monitor how specific DICOM tags are modified, removed, or preserved during pseudonymization


## Installation
Install the module using pip

```bash
  pip install dicomdiff
```

## Usage


### Compare two DICOM files in Python
```python
from dicomdiff.main import compare_dicom_files, print_differences

original_file = "path to original dcm file"
deidentified_file = "path to de-identified dcm file"

result = compare_dicom_files(original_file, deidentified_file) # compare the files
print_differences(result) # print the results
```

### Compare two pseudonymization methods
```python
import os
import glob
import pandas as pd

# Import the pseudonymizers you'll be comparing
from dicomdiff.pseudonymizer import IDISPseudonymizer, DicomRakePseudonymizer, InferredPseudonymizer
from dicomdiff.summary import generate_pseudonymization_summary

# Define the paths
input_dir = "path/to/input/data"
mapping_csv = "path/to/mapping"
idisoutput_dir = "/path/to/output/data/" # Note: this is needed if you use InferredPseudonymizer

# Find all files 
dicom_files = glob.glob(os.path.join(input_dir, "**", "*.dcm"), recursive=True)

# Define the pseudonymizers you want to use
dicomrake_pseudonymizer = DicomRakePseudonymizer()
idis_pseudonymizer = InferredPseudonymizer.from_csv(mapping_csv, idisoutput_dir)

# Generate comparison summary between the two pseudonymization methods
summary_df = generate_pseudonymization_summary(
    file_paths=dicom_files,
    pseudonymizer_a=dicomrake_pseudonymizer,
    pseudonymizer_b=idis_pseudonymizer,
    pseudonymizer_a_name="DICOMRake", # If you want to change the name of the pseudonymizers
    pseudonymizer_b_name="IDISPseudonymizer",
)

# Define helper function to identify private DICOM tags (odd group numbers)
def is_private_tag(tag_str):
    try:
        group = int(tag_str.split(",")[0], 16)
        return group % 2 != 0  
    except (ValueError, IndexError):
        return False

# Filter results to show only public tags (even group numbers)
public_tags_df = summary_df[~summary_df["tag"].apply(is_private_tag)]

# Display overall comparison statistics for public tags
print("\nComparison results (public tags only):")
print(public_tags_df["comparison"].value_counts().to_string())

# Configure pandas display options for better output formatting
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.colheader_justify", "center")

# Show detailed differences in public tags where pseudonymizers behaved differently
different_public_tags = public_tags_df[public_tags_df["comparison"] != "Both Unchanged"]
print(f"\nDifferences in public tags ({len(different_public_tags)}):")
print(different_public_tags)

# OPTIONAL: If private tags exist, you can show differences in private tags as well
if len(summary_df) > len(public_tags_df):
    private_tags_df = summary_df[summary_df["tag"].apply(is_private_tag)]
    different_private_tags = private_tags_df[
        private_tags_df["comparison"] != "Both Unchanged"
    ]
    print(f"\nDifferences in private tags ({len(different_private_tags)}):")
    print(different_private_tags)

```

### Compare two DICOM files using CLI
```bash
# Compare two DICOM files
dicomdiff compare file1.dcm file2.dcm

# Filter results
dicomdiff compare file1.dcm file.dcm --changed
```

#### CLI Flags
| Flag | Description |
|------|-------------|
| `--changed` | Show only tags that have different values between files |
| `--removed` | Show only tags that exist in original but not in de-identified file |
| `--added` | Show only tags that exist in de-identified but not in original file |
| `--unchanged` | Show only tags that have identical values in both files |
