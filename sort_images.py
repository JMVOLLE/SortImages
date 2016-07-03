# dependencies
from _ast import Str

import exifread
import datetime
import glob
from pathlib import Path
from pathlib import PurePath
import shutil
import os
import time
import threading
import queue
import configparser

# GUI stuff
from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from localisation import *

# some constants

KEY_DATE = 'Image DateTime'



class Application(tk.Frame):
    def __init__(self, master=None, lang='fr'):
        tk.Frame.__init__(self, master)
        self.lang = lang
        self.grid()
        self.createWidgets()
        # Create queues for updating contrent of STATUS_txt and LOG_txt
        self.LOG_queue = queue.Queue()
        self.STATUS_queue = queue.Queue()

        # state we are running then start periodical polling on the queues
        self.IsRunning = True
        self.PeriodicRefresh()

    def PeriodicRefresh(self):
        """
            Check every 100 ms if there is something new in the queue.
        """
        self.UpdateLog()
        self.UpdateStatus()
        if not self.IsRunning:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            exit(1)
        self.master.after(100, self.PeriodicRefresh)

    def Log(self,val, type=''):
        if type == 'I':
            self.LOG_queue.put("I:%s" % val)
        elif type == 'W':
            self.LOG_queue.put("W:%s" %val)
        elif type == 'E':
            self.LOG_queue.put("E:%s" %val)
        else:
            self.LOG_queue.put(val)

    def UpdateLog(self):
        while self.LOG_queue.qsize():
            try:
                msg = self.LOG_queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.LOG_txt.configure(state='normal')
                if msg.startswith('E:'):
                    self.LOG_txt.insert(END, msg[2:],'error')
                elif msg.startswith('W:'):
                    self.LOG_txt.insert(END, msg[2:],'warning')
                elif msg.startswith('I:'):
                    self.LOG_txt.insert(END, msg[2:],'info')
                else:
                    self.LOG_txt.insert(END, msg)

                self.LOG_txt.see(END)
                self.LOG_txt.configure(state='disabled')
            except queue.Empty:
                pass

    def UpdateProgress(self,current,max):
        if current >= max:
            self.STATUS_queue.put("f")
            return
        progress_inc = round(max / 20)
        if progress_inc == 0:
            progress_inc = 1
        if (current % progress_inc) == 0:
            self.STATUS_queue.put("+")

    def UpdateStatus(self):
        while self.STATUS_queue.qsize():
            try:
                msg = self.STATUS_queue.get(0)
                self.STATUS_txt.configure(state='normal')
                if msg == "+":
                    # increment by one the counter
                    position = self.STATUS_txt.index("progress")
                    self.STATUS_txt.delete(position)
                    self.STATUS_txt.insert(position, "O")
                    position += "+1c"
                    self.STATUS_txt.mark_set("progress", position)
                elif msg == "f" :
                    #display full counter
                    self.STATUS_txt.delete(self.STATUS_progress_start, END)
                    self.STATUS_txt.insert(END, "OOOOOOOOOOOOOOOOOOOO")
                else:
                    self.STATUS_txt.delete("0.0", END)
                    self.STATUS_txt.insert("0.0", msg+": ")
                    start = self.STATUS_txt.index("1.end")
                    self.STATUS_txt.mark_set("progress",start)
                    self.STATUS_progress_start = start
                    self.STATUS_txt.mark_gravity("progress", LEFT)
                    self.STATUS_txt.insert(END, "....................")

                self.STATUS_txt.configure(state='disabled')
            except queue.Empty:
                pass

    def createWidgets(self):
        # self.hi_there = tk.Button(self)
        # self.hi_there["text"] = "Hello World\n(click me)"
        # self.hi_there["command"] = self.say_hi
        # self.hi_there.pack(side="top")

#        self.QUIT = tk.Button(self, text="QUIT", fg="red",
       #                                     command=self.destroy)
        #self.QUIT.pack(side="bottom")


        self.SRC_bt = Button(self)

        self.SRC_bt["text"] = T['SRC_bt'][self.lang]
        self.SRC_bt["command"] = self.SRC_cb
        self.SRC_bt.grid(column = 0, row=0, sticky=tk.E+tk.W)
        self.SRC_txt = Text(self)

        self.SRC_val = StringVar()
        self.SRC_val.set(T['SRC_val'][self.lang])

        self.SRC_entry = Entry(self, textvariable=self.SRC_val,width=64)
        self.SRC_entry.grid(column=1, row=0, sticky='EW')


        #self.SRC_txt["value"] = "please select source folder"
        #self.SRC_txt.pack(side="right")

#        self.DST_fr = Frame(self)
        #self.DST_fr.pack()

        self.DST_bt = Button(self)
        self.DST_bt["text"] = T['DST_bt'][self.lang]
        self.DST_bt["command"] = self.DST_cb
        self.DST_bt.grid(column=0, row=1, sticky='EW')

        self.DST_val = StringVar()
        self.DST_val.set(T['DST_val'][self.lang])

        self.DST_entry = Entry(self, textvariable=self.DST_val)
        self.DST_entry.grid(column=1, row=1, sticky='EW')

        # scrollbar: http://effbot.org/zone/tkinter-scrollbar-patterns.htm
        self.STATUS_txt = Text(self,height=1)
        self.STATUS_txt.grid(column=0, row=4, columnspan=2)
        self.STATUS_txt.insert("1.0",T['STATUS_txt'][self.lang])
        #self.Status("Waiting for inputs")

        self.LOG_txt =Text(self)
        self.LOG_txt.grid(column=0, row=5,columnspan=2)
        self.LOG_txt.tag_configure('error', background='red')
        self.LOG_txt.tag_configure('warning', foreground='red')
        self.LOG_txt.tag_configure('info', foreground='green')

        self.OPTION_fr = LabelFrame(self,text="Options")
        self.OPTION_fr.grid(column=1, row=2, sticky=tk.W+tk.E)

        self.ACTION_val = StringVar()
        self.ACTION_val.set('COPY')
        self.ACTION_rb_cp = Radiobutton(self.OPTION_fr, text=T['ACTION_rb_cp'][self.lang], variable=self.ACTION_val, value='COPY')
        self.ACTION_rb_mv = Radiobutton(self.OPTION_fr, text=T['ACTION_rb_mv'][self.lang], variable=self.ACTION_val, value='MOVE')
        self.ACTION_rb_cp["command"] = self.ACTION_cb
        self.ACTION_rb_mv["command"] = self.ACTION_cb
        self.ACTION_rb_cp.pack(side=LEFT)
        self.ACTION_rb_mv.pack(side=LEFT)


        #self.ACTION_rb_cp.grid(column=1, row=2,sticky=tk.W)
        #self.ACTION_rb_mv.grid(column=1, row=3,sticky=tk.W)


        self.COPY_bt = Button(self)
        self.COPY_bt["text"] =T['COPY_bt_cp'][self.lang]
        self.COPY_bt["command"] = self.COPY_cb
        self.COPY_bt.grid(column=1, row=3,columnspan=2, sticky=tk.E + tk.W + tk.N +tk.S)

    def ACTION_cb(self):
        #print ("action", self.ACTION_val.get())
        action = self.ACTION_val.get()
        if action == 'COPY':
            self.COPY_bt["text"] = T['COPY_bt_cp'][self.lang]
        else:
            self.COPY_bt["text"] = T['COPY_bt_mv'][self.lang]


    def SRC_cb(self):
        print("SRC callback")
        folder = filedialog.askdirectory(title="Please select Images source folder",
                                           mustexist=True,
                                         initialdir="D:/photo_maman_2015_02 - Copie"
                                           )
        self.SRC_val.set(folder)

        self.Log("source folder: <%s>\n" %self.SRC_val.get())

    def DST_cb(self):
        folder = filedialog.askdirectory(title="Please select Images destination folder",
                                         mustexist=True,
                                         #initialdir=os.path.expanduser('~/.')
                                         initialdir='D:/sorted'
                                         )
        self.DST_val.set(folder)
        self.Log("destination folder: <%s>\n" % self.DST_val.get())

    def COPY_cb(self):
        #start the worker thread
        self.copy_thread = threading.Thread(target=self.COPY_WorkerThread)
        self.copy_thread.start()



    def Status(self, val):
        self.STATUS_queue.put(val)


    def COPY_WorkerThread(self):
        src = self.SRC_val.get()
        dst = self.DST_val.get()
        # validate the arguments
        if not os.path.exists(src):
            messagebox.showerror ("Missing Source", "Please select source folder")
            return
        if not os.path.exists(dst) :
            messagebox.showerror ("Missing destination", "Please select destination folder")
            return
        file_to_folder, unique_folders = self.parse_source_folder(src)
        self.Log("%d files found\n" % len(file_to_folder))
        self.Log("%d destination folders(s) to create\n" % len(unique_folders))
        for folder in unique_folders:
            self.Log(" - %s\n" % folder)

        self.create_destination_folders(dst, unique_folders,debug=True)

        action = self.ACTION_val.get()
        if action == 'MOVE':
            move_arg = True
        else:
            move_arg = False
        self.move_copy_files(dst, file_to_folder, move=move_arg, debug=True)

    def get_capture_date(self,file_name):
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

    def parse_source_folder(self,folder, verbose = True):
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

        cnt = 0
        self.Status("analyzing source folder")
        for file in jpg_files:
            capture_date = self.get_capture_date(file)
            destination = "%.4d/%.2d" % (capture_date.year, capture_date.month)
            destination_folders[file] = destination
            if verbose:
                self.Log(("%s : %s\n" % (os.path.basename(file),destination)))
            if destination not in unique_folders:
                unique_folders.add(destination)
            cnt += 1
            self.UpdateProgress(cnt,len(jpg_files))
        print("%d files found" % len(jpg_files))
        print("%d destination folders(s) " % len(unique_folders))

        return destination_folders, unique_folders

    def create_destination_folders(self,dest_root, unique_destination_folders, debug=False):
        """ create output directories if needed """
        self.Status("Creating destination folder(s)")
        progress_inc = round(len(unique_destination_folders) / 10)
        cnt = 0
        for folder in unique_destination_folders:
            #destination_folder = "%s\%s" % (dest_root, folder)
            destination_folder = os.path.join(dest_root,folder)
            if not os.path.exists(destination_folder):
                self.Log("%s created\n" % destination_folder)
                if not debug:
                    os.makedirs(destination_folder)
            else:
                self.Log("%s already exists\n" % destination_folder)
            cnt += 1
            self.UpdateProgress(cnt, len(unique_destination_folders))

    def move_copy_files(self,dest_root, destination_folders,move=False,debug=False):
        """ move files to where they belong
        :param destination_folders: a file name ordered dict of destination folders
        """
        cnt = 0
        total = len(destination_folders)
        if move:
            self.Status("Moving files")
        else:
            self.Status("Copying files")
        skipped = []
        moved = []
        copied = []
        for file in destination_folders.keys():
            destination_folder = os.path.join(dest_root, destination_folders[file])
            src_basename = os.path.basename(file)
            destination_file =os.path.join(destination_folder,src_basename)
            if not os.path.exists(destination_file):
                if move:
                    if not debug:
                        shutil.move(file, destination_folder)
                    self.Log("moving %s -> %s\n" % (os.path.basename(file), destination_folder))
                    moved.append(src_basename)

                else: #copy
                    if not debug:
                        shutil.copy(file, destination_folder)
                    self.Log("copying %s -> %s\n" % (os.path.basename(file), destination_folder))
                    copied.append(src_basename)
            else:
                self.Log("%s skipped : already exists in %s\n" % (src_basename,destination_folder), type='W')
                skipped.append(src_basename)
            cnt +=1
            self.UpdateProgress(cnt, total)

        if move:
            self.Log("%d files moved\n" %len(moved),type='I')
        else:
            self.Log("%d files copied\n" %len(copied),type='I')

        self.Log("%d files skipped\n" % len(skipped),type='W')
        for file in skipped:
            self.Log(" - %s\n" % file, type='W')


if __name__ == "__main__":

    #check for configuration file
    config = configparser.ConfigParser()
    try:
        config.read('sort_images.ini')
        lang = config['SETUP']['LANG']
    except configparser.Error:
        lang = 'fr'
        pass

    root = tk.Tk()
    root.title("Sort Images V1.0")
    app = Application(master=root,lang=lang)
    app.mainloop()



