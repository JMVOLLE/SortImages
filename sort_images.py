""" Photos sorting application using EXIF capture date
Copyright 2016 Jean-Marc Volle
License: Apache-2.0
"""

import exifread
import datetime
import glob
import shutil
import os
import threading
import queue
import configparser

# GUI stuff
from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from resources import R

# some constants
_KEY_DATE = 'Image DateTime'
_REVISION = "V1.0.0"
__copyright__ = "Copyright 2016 Jean-Marc Volle"

class SortImages(tk.Frame):
    """ Sort Image application top class """

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # retrieve config based information
        self.config = self.read_configuration()

        #load translations:
        self.T = R.T(self.lang)

        self.root = master
        title = "Sort Images " + _REVISION
        if self.debug:
            title += "-Debug"
        self.root.title(title)

        self.grid()
        self.create_ui()

        # Create queues for updating  STATUS_txt and LOG_txt
        self.LOG_queue = queue.Queue()
        self.STATUS_queue = queue.Queue()

        # add handler on windows closing event
        self.copymove_thread = None
        self.root.protocol("WM_DELETE_WINDOW", self.WM_DELETE_WINDOW_cb)

        # state we are running then start periodical polling on the queues
        self.do_periodic_refresh()

    def WM_DELETE_WINDOW_cb(self):
        """ Termination handler
        - ensure that any on going copy/move thread is properly stopped
        - update configuration history for next rune
        - then close
        """
        # save the src and dst for next call
        #config = configparser.ConfigParser()
        print("closing")
        # close any running thread:
        if (self.copymove_thread) and self.copymove_thread.is_alive():
            print("stopping thread")
            self.stop_thread = True
            self.copymove_thread.join(1.)
        try:
            #read again the original config
            #config.read('sort_images.ini')
            if self.config is not None:
                #create or add HISTORY section
                if self.config.has_section('HISTORY') is not True:
                    self.config.add_section('HISTORY')
                history = self.config['HISTORY']
                history['SRC'] = self.src
                history['DST'] = self.dst

                with open('sort_images.ini', 'w') as configfile:
                    self.config.write(configfile)
        except Exception as e:
            print ("failed to save ini file")
            pass

        self.root.destroy()

    def read_configuration(self):
        config = configparser.ConfigParser()
        try:
            config.read('sort_images.ini')
            setup = config['SETUP']
            self.lang = setup.get('LANG','en')
            self.debug = setup.getboolean('DEBUG', False)
            if config.has_section('HISTORY'):
                history = config['HISTORY']
                self.src = history['SRC']
                self.dst = history['DST']
            else:
                self.src = os.path.expanduser('~/.')
                self.dst = os.path.expanduser('~/.')
            return config
        except Exception as e:
            self.lang = 'en'
            self.debug = False
            print ("Error parsing config file\n")
            pass
        return None

    def do_periodic_refresh(self):
        """
            Check every 100 ms if there is something new in the queue.
        """
        self.LOG_update()
        self.STATUS_update()
        self.master.after(100, self.do_periodic_refresh)

    def log(self, val, type=''):
        if type == 'I':
            self.LOG_queue.put("I:%s" % val)
        elif type == 'W':
            self.LOG_queue.put("W:%s" %val)
        elif type == 'E':
            self.LOG_queue.put("E:%s" %val)
        else:
            self.LOG_queue.put(val)

    def LOG_update(self):
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

    def STATUS_update(self):
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


    def display_about(self):
        about_txt = """
        SortImage Revision %s
        %s
        """ % (_REVISION, __copyright__)
        messagebox.showinfo(title=self.T['about'],message=about_txt)

    def create_menubar(self):
        menubar = Menu(self.root)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label=self.T['about'], command=self.display_about)
        menubar.add_cascade(label=self.T['help'], menu=helpmenu)

        self.root.config(menu=menubar)

    def create_ui(self):
        """ Create the UI. All widgets are instanciated here"""
        self.create_menubar()
        self.SRC_bt = Button(self)

        self.SRC_bt["text"] = self.T['SRC_bt']
        self.SRC_bt["command"] = self.SRC_cb
        self.SRC_bt.grid(column = 0, row=0, sticky=tk.E+tk.W)
        self.SRC_txt = Text(self)

        self.SRC_val = StringVar()
        self.SRC_val.set(self.T['SRC_val'])

        self.SRC_entry = Entry(self, textvariable=self.SRC_val,width=64)
        self.SRC_entry.grid(column=1, row=0, sticky='EW')


        self.DST_bt = Button(self)
        self.DST_bt["text"] = self.T['DST_bt']
        self.DST_bt["command"] = self.DST_cb
        self.DST_bt.grid(column=0, row=1, sticky='EW')

        self.DST_val = StringVar()
        self.DST_val.set(self.T['DST_val'])

        self.DST_entry = Entry(self, textvariable=self.DST_val)
        self.DST_entry.grid(column=1, row=1, sticky='EW')

        # scrollbar: http://effbot.org/zone/tkinter-scrollbar-patterns.htm
        self.STATUS_txt = Text(self,height=1)
        self.STATUS_txt.grid(column=0, row=4, columnspan=2)
        self.STATUS_txt.insert("1.0",self.T['STATUS_txt'])
        #self.Status("Waiting for inputs")

        self.LOG_txt =Text(self)
        self.LOG_txt.grid(column=0, row=5,columnspan=2)
        self.LOG_txt.tag_configure('error', background='red')
        self.LOG_txt.tag_configure('warning', foreground='red')
        self.LOG_txt.tag_configure('info', foreground='green')

        self.OPTION_fr = LabelFrame(self,text="Options")
        self.OPTION_fr.grid(column=0, row=2, columnspan=2, sticky=tk.W+tk.E)

        self.ACTION_val = StringVar()
        self.ACTION_val.set('COPY')
        self.ACTION_rb_cp = Radiobutton(self.OPTION_fr, text=self.T['ACTION_rb_cp'], variable=self.ACTION_val, value='COPY')
        self.ACTION_rb_mv = Radiobutton(self.OPTION_fr, text=self.T['ACTION_rb_mv'], variable=self.ACTION_val, value='MOVE')
        self.ACTION_rb_cp["command"] = self.ACTION_cb
        self.ACTION_rb_mv["command"] = self.ACTION_cb
        self.ACTION_rb_cp.pack(side=LEFT)
        self.ACTION_rb_mv.pack(side=LEFT)


        self.COPYMOVE_bt = Button(self)
        self.COPYMOVE_bt["text"] =self.T['COPYMOVE_bt_cp']
        self.COPYMOVE_bt["command"] = self.COPYMOVE_cb
        self.COPYMOVE_bt.grid(column=0, row=3,columnspan=2, sticky=tk.E + tk.W + tk.N +tk.S)

    def ACTION_cb(self):
        #print ("action", self.ACTION_val.get())
        action = self.ACTION_val.get()
        if action == 'COPY':
            self.COPYMOVE_bt["text"] = self.T['COPYMOVE_bt_cp']
        else:
            self.COPYMOVE_bt["text"] = self.T['COPYMOVE_bt_mv']


    def SRC_cb(self):
        print("SRC callback")
        folder = filedialog.askdirectory(title=self.T['SRC_cb_dlg'],
                                           mustexist=True,
                                         initialdir=self.src
                                           )
        self.SRC_val.set(folder)
        self.src = folder

        self.log("%s: <%s>\n" % (self.T['SRC_cb_log'], self.SRC_val.get()))

    def DST_cb(self):
        folder = filedialog.askdirectory(title=self.T['DST_cb_dlg'],
                                         mustexist=True,
                                         #initialdir=os.path.expanduser('~/.')
                                         initialdir=self.dst
                                         )
        self.DST_val.set(folder)
        self.dst = folder
        self.log("%s: <%s>\n" % (self.T['DST_cb_log'], self.DST_val.get()))

    def COPYMOVE_cb(self):
        #start the worker thread
        self.stop_thread = False
        self.copymove_thread = threading.Thread(target=self.COPYMOVE_worker_thread)
        self.copymove_thread.start()


    def update_status(self, val):
        self.STATUS_queue.put(val)


    def COPYMOVE_worker_thread(self):
        try:
            src = self.SRC_val.get()
            dst = self.DST_val.get()

            # validate the arguments
            if not os.path.exists(src):
                messagebox.showerror (self.T['missing_src'], self.T['SRC_cb_dlg'])
                return
            if not os.path.exists(dst) :
                messagebox.showerror (self.T['missing_dst'], self.T['DST_cb_dlg'])
                return
            self.src = src
            self.dst = dst

            #disable the button to be sure it will not be hit while we run
            self.COPYMOVE_bt["state"] = DISABLED

            file_to_folder, unique_folders = self.parse_source_folder(src)
            self.log("%d %s" % (len(file_to_folder), self.T['log1']))
            self.log("%d %s" % (len(unique_folders), self.T['log2']))
            for folder in unique_folders:
                self.log(" - %s\n" % folder)

            self.create_destination_folders(dst, unique_folders,debug=self.debug)

            action = self.ACTION_val.get()
            if action == 'MOVE':
                move_arg = True
            else:
                move_arg = False
            self.move_copy_files(dst, file_to_folder, move=move_arg, debug=self.debug)

            #job done, let's enable the button again
            self.COPYMOVE_bt["state"] = NORMAL
        except Exception as e:
            if str(e) == "stopped":
                print("thread stopped")
                pass
        except:
            raise


    def get_capture_date(self,file_name):
        """
        :param file_name: name of a jpeg file
        :return: date a which the photo was taken
        """
        with open(file_name, 'rb') as file:
            # Return Exif tags
            exif_tags = exifread.process_file(file, stop_tag=_KEY_DATE)

            if _KEY_DATE in exif_tags.keys():
                # print("Key: <%s>, value <%s>" % (key_date, exif_tags[key_date]))
                str_creation_date = str(exif_tags[_KEY_DATE])
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
        self.update_status(self.T['status1'])
        for file in jpg_files:
            capture_date = self.get_capture_date(file)
            destination = "%.4d/%.2d" % (capture_date.year, capture_date.month)
            destination_folders[file] = destination
            if verbose:
                self.log(("%s : %.2d %.4d \n" % (os.path.basename(file),capture_date.month,capture_date.year)))
            if destination not in unique_folders:
                unique_folders.add(destination)
            cnt += 1
            self.UpdateProgress(cnt,len(jpg_files))
            if self.stop_thread:
                raise Exception("stopped")
        print("%d files found" % len(jpg_files))
        print("%d destination folders(s) " % len(unique_folders))

        return destination_folders, unique_folders

    def create_destination_folders(self,dest_root, unique_destination_folders, debug=False):
        """ create output directories if needed """

        self.update_status(self.T['status2'])
        progress_inc = round(len(unique_destination_folders) / 10)
        cnt = 0
        for folder in unique_destination_folders:
            #destination_folder = "%s\%s" % (dest_root, folder)
            destination_folder = os.path.join(dest_root,folder)
            if not os.path.exists(destination_folder):
                self.log("%s %s\n" % (destination_folder, self.T['log3']))
                if not debug:
                    os.makedirs(destination_folder)
            else:
                self.log("%s %s\n" % (destination_folder, self.T['log4']))
            cnt += 1
            self.UpdateProgress(cnt, len(unique_destination_folders))
            if self.stop_thread:
                raise Exception("stopped")

    def move_copy_files(self,dest_root, destination_folders,move=False,debug=False):
        """ move files to where they belong
        :param destination_folders: a file name ordered dict of destination folders
        :param move: boolean for moving vs copying
        :param debug: debug mode, if True, not file operation (move or copy) are performed
        """
        cnt = 0
        total = len(destination_folders)
        if move:
            self.update_status(self.T['status3'])
        else:
            self.update_status(self.T['status4'])
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
                    self.log("%s %s -> %s\n" % (self.T['log5'], os.path.basename(file), destination_folder))
                    moved.append(src_basename)

                else: #copy
                    if not debug:
                        shutil.copy(file, destination_folder)
                    self.log("%s %s -> %s\n" % (self.T['log6'], os.path.basename(file), destination_folder))
                    copied.append(src_basename)
            else:
                self.log("%s %s %s\n" % (src_basename, self.T['log7'], destination_folder), type='W')
                skipped.append(src_basename)
            cnt +=1
            self.UpdateProgress(cnt, total)
            if self.stop_thread:
                raise Exception("stopped")


        if move:
            self.log("%d %s\n" % (len(moved), self.T['log8']), type='I')
        else:
            self.log("%d %s\n" % (len(copied), self.T['log9']), type='I')

        self.log("%d %s\n" % (len(skipped), self.T['log10']), type='W')
        for file in skipped:
            self.log(" - %s\n" % file, type='W')


if __name__ == "__main__":

    root = tk.Tk()

    app = SortImages(master=root)
    app.mainloop()



