# XML2DCM-ECG

## Description

This repository contains a Python-based solution for converting ECG data from XML format to the DICOM (Digital Imaging
and Communications in Medicine) format. The goal of this project is to facilitate the process of transforming clinical
ECG data stored in XML files into a standardized, widely-used DICOM format, which is essential for healthcare systems,
medical imaging devices, and Electronic Health Record (EHR) systems.

The solution handles the extraction and conversion of ECG information, including patient details, acquisition context,
and waveform data, from XML files into the DICOM format. The project also integrates essential metadata such as the type
of ECG lead (e.g., Lead I, Lead II), device information (e.g., acquisition device, software versions), and patient
demographics.

## Installation
You can install XML2DCM-ECG directly from PyPI:
```bash
pip install XML2DCM-ECG
```

Alternatively, you can use `uv`, a faster Python package manager with built-in script runner:
```bash
pip install uv
```

## Usage
After installation, you can run the ECG XML-to-DICOM converter using either of the following methods.

### 1. Using standard CLI command
Run the following command: 
```bash
   xml2dcm-ecg --ecg_xml_path /path/to/xml_files --output_dir /path/to/save_dicom --debug True --debug_n 5
```

### 2. Using uvx for fast execution
With `uv` installed, you can use `uvx` for faster execution:
```bash
   uvx xml2dcm-ecg --ecg_xml_path /path/to/xml_files --output_dir /path/to/save_dicom --debug True --debug_n 5
```

### CLI Options
* `--ecg_xml_path`: Path to the directory containing the XML files to be converted.
* `--output_dir`: Path to the directory where you want the converted DICOM files to be saved. The default is `ecg_dicom`.
* `--debug`: Enable debug mode. The default is `False`.
* `--debug_n`: Number of files to process in debug mode. The default is `5`.

## Example results

The following are examples of the ECG data converted from XML to DICOM format:
![ecg_dicom.png](https://raw.githubusercontent.com/MedxEng/XML2DCM-ECG/f9f461195a593d801b28f187a15c75244010c858/assets/ecg_dicom.png)
   

