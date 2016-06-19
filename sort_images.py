# dependencies
import exifread
import datetime
import glob
from pathlib import Path
from pathlib import PurePath
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
    with open(file_name, 'rb') as file:

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


def parse_source_folder(folder):
    """ find jpg files in the input folder
    :param folder: folder to parse
    :return: destination_folders : dict of relative destination folder (keyed by file names)
    :return: unique_folders : set of relative destination folder
    """

    # parse the input directory
    jpg_files = glob.glob(folder+"\\*.jpg")
    jpg_files = jpg_files + glob.glob(folder + "\\*.JPG")
    jpg_files = jpg_files + glob.glob(folder + "\\*.jpeg")

    # return values
    destination_folders = dict()
    unique_folders = set()

    for file in jpg_files:
        capture_date = get_capture_date(file)
        destination = "%.4d\%.2d" % (capture_date.year, capture_date.month)
        destination_folders[file] = destination
        if destination not in unique_folders:
            unique_folders.add(destination)

    print("%d files found" % len(jpg_files))
    print("%d destination folders(s) " % len(unique_folders))

    return destination_folders, unique_folders


def create_destination_folders(dest_root, unique_destination_folders):
    """ create output directories if needed """
    for folder in unique_destination_folders:
        destination_folder = "%s\%s" % (dest_root, folder)
        if not os.path.exists(destination_folder):
            print("Creating: %s" % destination_folder)
            os.makedirs(destination_folder)


def move_files(dest_root, destination_folders):
    """ move files to where they belong
    :param destination_folders: a file name ordered list of destination folders
    """
    for file in destination_folders.keys():
        destination_folder = "%s\%s" % (dest_root, destination_folders[file])
        print(" mv %s %s" % (file, destination_folder))
        # shutil.move(file, destination_folder)



# read all jpg files from a folder
src_folder = 'd:\\test_source'
dst_folder = 'd:\\sorted'

all_folders, unique_folders = parse_source_folder(src_folder)
print("Folders to create\n")
print(unique_folders)




