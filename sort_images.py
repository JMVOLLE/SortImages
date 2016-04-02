# dependencies
import exifread
import datetime
import glob
import shutil
import os
import tkinter

# some constants

KEY_DATE = 'Image DateTime'

def get_capture_date(file_name):
    """
    :param file_name: name of a jpeg file
    :return: date a which the photo was taken
    """
    with open(file_name, 'rb') as _file:

        # Return Exif tags
        exif_tags = exifread.process_file(file)

        if KEY_DATE in exif_tags.keys():
            # print("Key: <%s>, value <%s>" % (key_date, exif_tags[key_date]))
            str_creation_date = str(exif_tags[KEY_DATE])
    #        print('Creation date ', str_creation_date)
            capture_date = datetime.datetime.strptime(str_creation_date, '%Y:%m:%d %H:%M:%S')
#            print("year:%.4d" % creation_date.year)
#           print("month:%.2d" % creation_date.month)
    return capture_date



# read all jpg files from a folder
src_folder = 'd:\\test_source\\*.jpg'
dst_folder = 'd:\\sorted'


def parse_source_folder(folder):

    jpg_files = glob.glob(folder)

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


def create_destination_folders(dest_root, destination_folders):
    """ create output directories if needed """
    for folder in destination_folders:
        destination_folder = "%s\%s" % (dest_root, folder)
        if not os.path.exists(destination_folder):
            print("Creating: %s" % destination_folder)
            os.makedirs(destination_folder)


# move files to where they belong
for file in capture_dates.keys():
    destination_folder = "%s\%.4d\%.2d" % (to, capture_dates[file].year, capture_dates[file].month)
    print(" mv %s %s" % (file, destination_folder))
    # shutil.move(file, destination_folder)

