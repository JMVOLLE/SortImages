# Sort Images
Python based application sorting (copy/move) images based on their exif capture date

Written by Jean-Marc Volle

![ui overview][ui]

Images from the source folder are copied/moved in the destination folder
in specific folders created according to the year and the month of the day
the image was taken (exif capture date).

Eg : An image taken on the 4th of July 2016 is moved/copied to destination/2016/07


# Installation
1. Copy the files listed in Files section
2. Choose en/fr language in [sort_images.ini]
3. Run [sort_image.py] using your favorite python environment

# Dependencies

- [exifread 2.1.2]

# Files
 - [sort_image.py] : main for the application
 - [resources.py]  : resource file (localization)
 - [sort_images.ini] : configuration file
    - language selection (en/fr):
    - Debug mode: In debug mode no file operations (copy/move) are performed

# Tested with
  - python 3.4.4 (32bits/Windows)


[exifread 2.1.2]: https://pypi.python.org/pypi/ExifRead/2.1.2
[ui]: ./capture.png
[sort_image.py]: ./sort_image.py
[resources.py]: ./resources.py
[sort_images.ini]: ./sort_images.ini
