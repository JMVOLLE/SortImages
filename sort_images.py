# dependencies
from _ast import Str

import exifread
import datetime
import glob
from pathlib import Path
from pathlib import PurePath
import shutil
import os

# GUI stuff
from tkinter import *
import tkinter as tk
from tkinter import filedialog

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
            print("done   : %s" % destination_folder)
            os.makedirs(destination_folder)
        else:
            print("skipped: %s" % destination_folder)

def create_folders(folders):
    """ create output directories if needed
     :param folders: a list of PurePAth folders
     """
    for folder in folders:
        if not os.path.exists(str(folder)):
            print("done   : %s" % folder)
            os.makedirs(str(folder))
        else:
            print("skipped: %s" %folder)


def move_files(dest_root, destination_folders):
    """ move files to where they belong
    :param destination_folders: a file name ordered dict of destination folders
    """
    for file in destination_folders.keys():
        destination_folder = "%s\%s" % (dest_root, destination_folders[file])
        print(" mv %s %s" % (file, destination_folder))
        shutil.move(file, destination_folder)


def command_line_test():
    src_root = PurePath('d:/test_source')
    dst_root = PurePath('d:/sorted')

    print ("Source:",src_root)
    print ("Destination:",dst_root)

    #parse the source folder and retrieve le list of unique folder to create as well as the list of which
    # source file to mote to which destination folder
    file_to_folder, unique_folders = parse_source_folder(str(src_root))

    #create the destination folders
    create_destination_folders(dst_root,unique_folders)

    #move the content where it belongs
    move_files(dst_root,file_to_folder)

def gui_main():
    main_window = Tk()
    main_window.title("Image sorter V1.0");

    #label = Label(main_window, text="=== Image sorter ===")

    #label.pack()

    #http://tkinter.unpythonic.net/wiki/tkFileDialog

    # source and destination widgets are packed in their own frame
    frame_src = Frame(main_window)
    frame_src.pack()
    frame_dst = Frame(main_window)
    frame_dst.pack()

    src_root = filedialog.askdirectory(title="Please select Images source folder",
                                    mustexist = True,
                                    initialdir=os.path.expanduser('~/.')
                                   )

    src_text = Label(frame_src, text= "Source:")
    src_text.pack(side=LEFT)
    src_button = Button(frame_src, text="Select source folder")
    src_button.pack(side=LEFT)
    src_value = Label(frame_src, text= src_root)
    src_value.pack(side=LEFT)

    dst_root = filedialog.askdirectory(title="Please select Images source folder",
                                       mustexist=True,
                                       initialdir=os.path.expanduser('~/')
                                       )



    dst_text = Label(frame_dst, text="Destination:")
    dst_text.pack(side=LEFT)
    dst_value = Label(frame_dst, text=dst_root)
    dst_value.pack(side=LEFT)
    main_window.mainloop()



class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        # self.hi_there = tk.Button(self)
        # self.hi_there["text"] = "Hello World\n(click me)"
        # self.hi_there["command"] = self.say_hi
        # self.hi_there.pack(side="top")

        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                                            command=self.destroy)
        #self.QUIT.pack(side="bottom")


        self.SRC_bt = Button(self)
        self.SRC_bt["text"] = "Source:"
        self.SRC_bt["command"] = self.SRC_cb
        self.SRC_bt.grid(column = 0, row=0, sticky=tk.E+tk.W)
        self.SRC_txt = Text(self)

        self.SRC_val = StringVar()
        self.SRC_val.set("images source folder")
        self.SRC_entry = Entry(self, textvariable=self.SRC_val,width=64)
        self.SRC_entry.grid(column=1, row=0, sticky='EW')


        #self.SRC_txt["value"] = "please select source folder"
        #self.SRC_txt.pack(side="right")

#        self.DST_fr = Frame(self)
        #self.DST_fr.pack()

        self.DST_bt = Button(self)
        self.DST_bt["text"] = "Destination:"
        self.DST_bt["command"] = self.DST_cb
        self.DST_bt.grid(column=0, row=1, sticky='EW')

        self.DST_val = StringVar()
        self.DST_val.set("image destination folder")
        self.DST_entry = Entry(self, textvariable=self.DST_val)
        self.DST_entry.grid(column=1, row=1, sticky='EW')


        self.STATUS_txt = Text(self,height=1)
        self.STATUS_txt.grid(column=0, row=2, columnspan=2)
        #self.STATUS_txt.insert("0.0","Waiting for inputs")
        self.Status("Waiting for inputs")
        self.LOG_txt =Text(self)
        self.LOG_txt.grid(column=0, row=3,columnspan=2)

        self.COPY_bt = Button(self)
        self.COPY_bt["text"] = "COPY"
        self.COPY_bt["command"] = self.COPY_cb
        self.COPY_bt.grid(column=2, row=0, sticky=tk.E + tk.W,rowspan=2)

    def SRC_cb(self):
        print("SRC callback")
        folder = filedialog.askdirectory(title="Please select Images source folder",
                                           mustexist=True,
                                           initialdir=os.path.expanduser('~/.')
                                           )
        self.SRC_val.set(folder)

        self.Log("source folder:%s\n" %self.SRC_val.get())

    def DST_cb(self):
        folder = filedialog.askdirectory(title="Please select Images destination folder",
                                         mustexist=True,
                                         initialdir=os.path.expanduser('~/.')
                                         )
        self.DST_val.set(folder)
        self.Log("destination folder:%s\n" % self.DST_val.get())

    def COPY_cb(self):
        src = self.SRC_val.get()
        dst = self.DST_val.get()
        file_to_folder, unique_folders = self.parse_source_folder(src)
        self.Log("%d files found\n" % len(file_to_folder))
        self.Log("%d destination folders(s) to create\n" % len(unique_folders))

    def Log(self,val):
        self.LOG_txt.configure(state='normal')
        self.LOG_txt.insert(END,val)
        self.LOG_txt.configure(state='disabled')


    def Status(self, val):
        self.STATUS_txt.configure(state='normal')
        self.STATUS_txt.delete("0.0",END)
        self.STATUS_txt.insert("0.0", val)
        self.STATUS_txt.configure(state='disabled')
        self.status_start = len(val)
        print (self.status_start)


    def IncStatus(self):
        self.STATUS_txt.configure(state='normal')
        self.STATUS_txt.insert(END, "o")
        self.STATUS_txt.configure(state='disabled')


    def parse_source_folder(self,folder):
        """ find jpg files in the input folder
        :param folder: folder to parse
        :return: destination_folders : dict of relative destination folder (keyed by file names)
        :return: unique_folders : set of relative destination folder
        """

        # parse the input directory

        jpg_files = glob.glob(folder+"\\*.jpg")
        # windows does not care about case jpg_files = jpg_files + glob.glob(folder + "\\*.JPG")
        jpg_files = jpg_files + glob.glob(folder + "\\*.jpeg")

        # return values
        destination_folders = dict()
        unique_folders = set()

        nb_inc = round(len(jpg_files)/10)
        cnt = 0
        self.Status("analyzing source folder")
        for file in jpg_files:
            capture_date = get_capture_date(file)
            destination = "%.4d\%.2d" % (capture_date.year, capture_date.month)
            destination_folders[file] = destination
            if destination not in unique_folders:
                unique_folders.add(destination)
            cnt = cnt + 1
            if (cnt % nb_inc) == 0:
                self.IncStatus()
        print("%d files found" % len(jpg_files))
        print("%d destination folders(s) " % len(unique_folders))

        return destination_folders, unique_folders




if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sort Images V1.0")
    app = Application(master=root)
    app.mainloop()



