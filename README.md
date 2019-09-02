# Route Clearance

This repository contains script to extract the route clearance table text from the Network Rail (NR) Network Rail National Electronic Sectional Appendix (NESA) data downloaded as embedded text PDF and converted to a TSV (Tab Seperated Value) format

## High-level process

To extract the files on a Linux or similar OS system, the process to create the NESA files is then:

### Download the Sectional Appendix 

Download the PDF files from [here](https://www.networkrail.co.uk/industry-and-commercial/information-for-operators/national-electronic-sectional-appendix/) in to the 'download' subdirectory . For June 2019 these consist of the following files:

* 'Anglia Sectional Appendix June 2019.pdf'
* 'Kent, Sussex, Wessex Sectional Appendix June 2019.pdf'
* 'London North Eastern Sectional Appendix June 2019.pdf'
* 'London North Western North Sectional Appendix June 2019.pdf'
* 'London North Western South Sectional Appendix June 2019.pdf'
* 'Scotland Sectional Appendix June 2019.pdf'
* 'Western and Wales Sectional Appendix June 2019.pdf'

### Run the 'run.sh' script

The following activities:
1. Download the 'tabula-java' PDF text-extraction tool, 
2. Create subdirectories for each region,
3. Extract the associated route-clearance table pages as individual PDF files,
4. Extract segmented TSV data from each pages, and
5. Combine, clean and recombine the data with a TSV page-file for each page table in the 'report' directory

Are completed by executing the `run.sh` script:
```
   $ ./run.sh
```

## Data notes

Following processing the data extracted into TSV page-files is written to the *report* sub-directory. The files are named by route and PDF file number. For example, table data from page 449 of the Anglia route is contained in `report/Anglia_0449.tsv`

To extract and process data PNG image files are then contained in the `<route>/work` directory. For example, the image file for page 1056 of *London-North-Eastern* route is contained in the `London-North-Eastern/work/pg_1056.png`

The corresponding extracted reference PDF files are in the `<route>/pdf` directory whereas the complete monolithic route PDF file is in the `<route>/download` directory

### Issues and exceptions

Due to issues with page registration and layout, the combination and processing script the `generate-report.py` is rather experimental and significantly more complex than ideal

### Errata

On certain pages initial-letter are ommitted as these overlap with table-lines and cannot be extracted

Due to missing *RA* and *Loco Gauge* data on page 544 of the *London-North-Western-South* route these values are replaced with a `-`

## Pre-requisites

The following pre-requisites are required to run the scripts in the toolchain:

### ImageMagick

ImageMagick is a free and open-source software suite for displaying, converting, and editing raster image and vector image files. More details are available here [here](https://imagemagick.org/)

ImageMagick is installed on a Debian (`apt`) based Linux system by:

```
   $ sudo apt install imagemagick
```

#### Note: 
Due to security vulnerability which includes possible remote code execution and ability to render files on the local system ImageMagick does not render PDF files by default. 

As the ability to render PDF files is required to run this process, the ImageMagick security `policy.xml` for PDF file-processing has to be modified from `rights="none"` to `rights="read|write"`:

For example, modify the policy.xml file for PDF as below:
```
   $ sudo vi /etc/ImageMagick-6/policy.xml 
```

```
   <!-- enable ghostscript format types -->
      <policy domain="coder" rights="none" pattern="PS" />
      <policy domain="coder" rights="none" pattern="EPS" />
      <policy domain="coder" rights="read|write" pattern="PDF" />
      <policy domain="coder" rights="none" pattern="XPS" />
   </policymap>
```

### pdfgrep

`pdfgrep` is an open-source software component for searcing text PDF files and is used to identify the location of the route-clearance data.

`pdfgrep` is installed on a Debian (`apt`) based Linux system by:

```
   $ sudo apt install pdfgrep
```

### pdfseperate

`pdfseparate` is an open-source software component from the `poppler-utils` suite used for rendering PDF files.

`pdfseparate` is installed on a Debian (`apt`) based Linux system by:

$ sudo apt install poppler-utils

### tabula-java

Tabula is a `java` application developed in for extracting data tables from inside PDF files. As this is a `java` application it is assumed that a current version of `java` is installed. The `run.sh` script takes a local install of  version `1.0.3` of the `tabula-java` application. More information about [here](https://tabula.technology)
 
# Data Acknowledgement and Thanks

The authors of this would like to thank [Network Rail](https://networkrail.co.uk) for making this data available and for the creators and maintainers of all of the software used to create this workflow

The TSV representation is derived from the National Sectional Appendix PDF data whose copyright rests wholely with 2019 Network Rail


