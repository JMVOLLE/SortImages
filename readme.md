# Sort Images
Python based application sorting (copy/move) images based on their exif capture date
Written by Jean-Marc Volle

![ui overview][ui]

# Installation
Copy the files listed in Files section and run using your favorite python environment

# Dependencies

- [exifread 2.1.2]

# Files
 - `sort_image.py` : main for the application
 - `resources.py` : resource file (localization)
 - `sort_images.ini` : configuration file
    - language selection (en/fr):
    - Debug mode: In debug mode no file operations (copy/move) are performed

# Tested with
  - python 3.4.4 (32bits/Windows)


[exifread 2.1.2]: https://pypi.python.org/pypi/ExifRead/2.1.2
[ui]: ./capture.png
