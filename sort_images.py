# dependencies
import exifread
import datetime
import glob
import shutil
import os
import tkinter

# some constants
key_date = 'Image DateTime'


def get_capture_date(file_name):
    # read the exif data from the file and report the image capture date
    file = open(file_name, 'rb')

    # Return Exif tags
    exif_tags = exifread.process_file(file)

    if key_date in exif_tags.keys():
        # print("Key: <%s>, value <%s>" % (key_date, exif_tags[key_date]))
        str_creation_date = str(exif_tags[key_date])
#        print('Creation date ', str_creation_date)
        capture_date = datetime.datetime.strptime(str_creation_date, '%Y:%m:%d %H:%M:%S')
#        print("year:%.4d" % creation_date.year)
#        print("month:%.2d" % creation_date.month)
    return capture_date



# read all jpg files from a folder
jpg_folder = 'd:\\test_source\\*.jpg'
to = 'd:\\sorted'


def parse_source_folder(src_folder):

    jpg_files = glob.glob(src_folder)

    # parse the input directory
    destination_folders = set()
    capture_dates = dict()
    for file in jpg_files:
        capture_date = get_capture_date(file)
        capture_dates[file] = capture_date
        destination = "%.4d\%.2d" % (capture_date.year, capture_date.month)
        if destination not in destination_folders:
            destination_folders.add(destination)

    print("%d files found" % len(jpg_files))
    print("%d destinations(s) " % len(destination_folders))

    return capture_dates, destination_folders


def name_output_directories(in_capture_dates):




# create output directories if needed
for folder in destination_folders:
    destination_folder = "%s\%s" % (to, folder)
    if not os.path.exists(destination_folder):
        print("Creating: %s" % destination_folder)
        os.makedirs(destination_folder)

# move files to where they belong
for file in capture_dates.keys():
    destination_folder = "%s\%.4d\%.2d" % (to, capture_dates[file].year, capture_dates[file].month)
    print(" mv %s %s" % (file, destination_folder))
    # shutil.move(file, destination_folder)

