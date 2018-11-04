""" Photos sorting application using EXIF capture date
Copyright 2016 Jean-Marc Volle
License: Apache-2.0
"""

__version__='1.0.1'

import exifread
import datetime
import glob
import shutil
import os
import threading
import queue
import configparser
import re
# GUI stuff
from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from resources import R

# some constants
_KEY_DATE = 'Image DateTime'
__copyright__ = "Copyright 2016 Jean-Marc Volle"

class SortImages(tk.Frame):
    """ Sort Image application top class """

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # retrieve config based information

        #init informations expected from the user or the history
        self.mSourceFolder = None
        self.mDestinationFolder = None

        self.config = self.ReadConfigurationFile()

        #load translations:
        self.T = R.T(self.lang)

        self.root = master
        title = "Sort Images "
        if self.debug:
            title += "- Debug"
        self.root.title(title)

        self.grid()
        self.CreateUi()

        # Create queues for updating  STATUS_txt and LOG_txt
        self.mLogQueue = queue.Queue()
        self.mStatusQueue = queue.Queue()


        # add handler on windows closing event
        self.mProcessThread = None
        self.mAnalyzeThread = None


        self.root.protocol("WM_DELETE_WINDOW", self.WM_DELETE_WINDOW_cb)

        # state we are running then start periodical polling on the queues
        self.RefreshUiTask()

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
        if (self.mProcessThread) and self.mProcessThread.is_alive():
            print("stopping thread")
            self.mStopThreadRequest = True
            self.mProcessThread.join(1.)
        try:
            #read again the original config
            #config.read('sort_images.ini')
            if self.config is not None:
                #create or add HISTORY section
                if self.config.has_section('HISTORY') is not True:
                    self.config.add_section('HISTORY')
                history = self.config['HISTORY']
                history['SRC'] = self.mSourceFolder
                history['DST'] = self.mDestinationFolder

                with open('sort_images.ini', 'w') as configfile:
                    self.config.write(configfile)
        except Exception as e:
            print ("failed to save ini file")
            pass

        self.root.destroy()

    def ReadConfigurationFile(self):
        config = configparser.ConfigParser()
        try:
            config.read('sort_images.ini')
            setup = config['SETUP']
            self.lang = setup.get('LANG','en')
            self.debug = setup.getboolean('DEBUG', False)
            if config.has_section('HISTORY'):
                history = config['HISTORY']
                self.mSourceFolder = history['SRC']
                self.mDestinationFolder = history['DST']
            else:
                self.mSourceFolder = os.path.expanduser('~/.')
            return config
        except Exception as e:
            self.lang = 'en'
            self.debug = False
            print ("Error parsing config file\n")
            pass
        return None

    def RefreshUiTask(self):
        """
            Check every 100 ms if there is something new in the queue.
        """
        self.UpdateLogText()
        self.UpdateStatusText()

        # update the visibility on the process button based on informations set byt the user so far
        if self.mDestinationFolder and len(self.uiDestinationList.get(0,END)) > 0:
            self.uiProcessButton["state"] = NORMAL
        else:
            self.uiProcessButton["state"] = DISABLED

        self.master.after(100, self.RefreshUiTask)

    def Log(self, val, type=''):
        if type == 'I':
            self.mLogQueue.put("I:%s" % val)
        elif type == 'W':
            self.mLogQueue.put("W:%s" % val)
        elif type == 'E':
            self.mLogQueue.put("E:%s" % val)
        else:
            self.mLogQueue.put(val)

    def UpdateLogText(self):
        while self.mLogQueue.qsize():
            try:
                msg = self.mLogQueue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                self.uiLogText.configure(state='normal')
                if msg.startswith('E:'):
                    self.uiLogText.insert(END, msg[2:], 'error')
                elif msg.startswith('W:'):
                    self.uiLogText.insert(END, msg[2:], 'warning')
                elif msg.startswith('I:'):
                    self.uiLogText.insert(END, msg[2:], 'info')
                else:
                    self.uiLogText.insert(END, msg)

                self.uiLogText.see(END)
                self.uiLogText.configure(state='disabled')
            except queue.Empty:
                pass

    def UpdateProgress(self,current,max):
        if current >= max:
            self.mStatusQueue.put("f")
            return
        progress_inc = round(max / 20)
        if progress_inc == 0:
            progress_inc = 1
        if (current % progress_inc) == 0:
            self.mStatusQueue.put("+")

    def UpdateStatusText(self):
        while self.mStatusQueue.qsize():
            try:
                msg = self.mStatusQueue.get(0)
                self.uiStatusText.configure(state='normal')
                if msg == "+":
                    # increment by one the counter
                    position = self.uiStatusText.index("progress")
                    self.uiStatusText.delete(position)
                    self.uiStatusText.insert(position, "O")
                    position += "+1c"
                    self.uiStatusText.mark_set("progress", position)
                elif msg == "f" :
                    #display full counter
                    self.uiStatusText.delete(self.mStatusTextProgressPosition, END)
                    self.uiStatusText.insert(END, "OOOOOOOOOOOOOOOOOOOO")
                else:
                    self.uiStatusText.delete("0.0", END)
                    self.uiStatusText.insert("0.0", msg + ": ")
                    start = self.uiStatusText.index("1.end")
                    self.uiStatusText.mark_set("progress", start)
                    self.mStatusTextProgressPosition = start
                    self.uiStatusText.mark_gravity("progress", LEFT)
                    self.uiStatusText.insert(END, "....................")

                self.uiStatusText.configure(state='disabled')
            except queue.Empty:
                pass


    def display_about(self):
        about_txt = """
        Sort Images Revision %s
        %s

        You can fork me on github:
        https://github.com/JMVOLLE/SortImages

        uses fonctions from:
         - %s (%s)
        """ % (__version__, __copyright__,"exifread",'https://github.com/ianare/exif-py')
        messagebox.showinfo(title=self.T['about'],message=about_txt)

    def CreateMenuBar(self):
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label=self.T['quit'], command=self.WM_DELETE_WINDOW_cb)
        menu_bar.add_cascade(label=self.T['file'], menu=file_menu)


        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label=self.T['about'], command=self.display_about)
        menu_bar.add_cascade(label=self.T['help'], menu=help_menu)

        self.root.config(menu=menu_bar)

    def CreateUi(self):
        """ Create the UI. All widgets are instanciated here"""
        self.CreateMenuBar()

        #self.SRC_txt = Text(self)
        self.uiSourceFrame = LabelFrame(self, text=self.T['uiSourceFrame'])
        self.uiSourceFrame.grid(column=0, row=0, sticky=tk.W)

        self.uiDestinationFrame = LabelFrame(self, text=self.T['uiDestinationFrame'])
        self.uiDestinationFrame.grid(column=1, row=0, sticky=tk.W)

        self.uiSourceButton = Button(self.uiSourceFrame)
        self.uiSourceButton["text"] = self.T['uiSourceButton']
        self.uiSourceButton["command"] = self.onSourceButton
        self.uiSourceButton.grid(column=0, row=0, sticky=tk.W)

        self.uiSourceValue = StringVar()
        self.uiSourceValue.set(self.mSourceFolder)

        self.uiSourceEntry = Entry(self.uiSourceFrame, textvariable=self.uiSourceValue, width=40)
        self.uiSourceEntry.grid(column=0, row=1, columnspan=2)

        self.uiSourceList = Listbox(self.uiSourceFrame)
        self.uiSourceList["selectmode"] = EXTENDED
        self.uiSourceList.bind('<Double-1>', self.onSourceListDbClick)
        self.uiSourceList.grid(column=0, row=2, sticky='NWES', pady=5)

        self.uiDestinationButton = Button(self.uiDestinationFrame)
        self.uiDestinationButton["text"] = self.T['uiDestinationButton']
        self.uiDestinationButton["command"] = self.onDestinationButton
        self.uiDestinationButton.grid(column=0, row=0, sticky=tk.W)

        self.uiDestinationValue = StringVar()
        self.uiDestinationValue.set(self.mDestinationFolder)

        self.uiDestinationEntry = Entry(self.uiDestinationFrame, textvariable=self.uiDestinationValue, width=40)
        self.uiDestinationEntry.grid(column=0, row=1, sticky='EW')

        self.uiDestinationList = Listbox(self.uiDestinationFrame)
        self.uiDestinationList["selectmode"] = EXTENDED
        self.uiDestinationList.bind('<Double-1>', self.onDestinationListDoubleClick)
        self.uiDestinationList.grid(column=0, row=2, sticky='W', pady=5)

        self.uiOperationFrame = LabelFrame(self.uiSourceFrame, text="Operation:")
        # self.OPTION_fr.grid(column=0, row=2, columnspan=2, sticky=tk.W + tk.E)
        self.uiOperationFrame.grid(column=1, row=2, columnspan=1, sticky='NW')

        self.uiOperationValue = StringVar()
        self.uiOperationValue.set('COPY')
        self.uiOperationCopyRadioButton = Radiobutton(self.uiOperationFrame, text=self.T['ACTION_rb_cp'],
                                                      variable=self.uiOperationValue,
                                                      value='COPY')
        self.uiOperationMoveRadioButton = Radiobutton(self.uiOperationFrame, text=self.T['ACTION_rb_mv'],
                                                      variable=self.uiOperationValue,
                                                      value='MOVE')
        self.uiOperationCopyRadioButton["command"] = self.onOperationRadioButton
        self.uiOperationMoveRadioButton["command"] = self.onOperationRadioButton
        self.uiOperationCopyRadioButton.pack(side=TOP)
        self.uiOperationMoveRadioButton.pack(side=BOTTOM)

        self.uiProcessButton = Button(self)
        self.uiProcessButton["text"] = self.T['uiProcessButton']
        self.uiProcessButton["command"] = self.onProcessButton
        self.uiProcessButton.grid(column=2, row=0, sticky='EWNS')

        # scrollbar: http://effbot.org/zone/tkinter-scrollbar-patterns.htm
        self.uiStatusText = Text(self, height=1)
        self.uiStatusText.grid(column=0, row=1, columnspan=3)
        self.uiStatusText.insert("1.0", self.T['uiStatusText'])
        #self.Status("Waiting for inputs")

        self.uiLogText =Text(self)
        self.uiLogText.grid(column=0, row=2, columnspan=3)
        self.uiLogText.tag_configure('error', background='red')
        self.uiLogText.tag_configure('warning', foreground='red')
        self.uiLogText.tag_configure('info', foreground='green')






    def onSourceListDbClick(self, event):
        """ add any double click item from source to dst """

        # retrieve the selection on src side
        uiList = event.widget
        index = uiList.curselection()  # on list double-click
        label = uiList.get(index)

        # clear the selection
        uiList.selection_clear(index, END)

        #In move mode delete the entry to make it clear it will be moved
        if self.uiOperationValue.get() == 'MOVE':
            uiList.delete(index)
            label= label + " [mv]"
        else:
            label = label + " [cp]"

        # move it to the destination list after sorting again all entries
        self.AddItemToUiList(self.uiDestinationList, label)


    def onDestinationListDoubleClick(self, event):
        """ remove any double clicked item"""
        # retrieve the selection on src side
        widget_list = event.widget
        index = widget_list.curselection()  # on list double-click
        label = widget_list.get(index)


        # strip the label about any information added about copy/move
        #label = self.cleanUserSelectedItems([label])[0]
        label = label[:-5]
        widget_list.delete(index)

        #put back the selection on the source side (in copy it was never removed in the first place)
        self.AddItemToUiList(self.uiSourceList, label)



    def onOperationRadioButton(self):
        #print ("action", self.ACTION_val.get())
        operation = self.uiOperationValue.get()

        # if some folders are already selected, apply the copy/move option to them
        indexesToDelete = []
        selectedSrcFoldersIndexes = self.uiSourceList.curselection()
        for index in selectedSrcFoldersIndexes:
            label = self.uiSourceList.get(index)
            if operation == 'MOVE':
                indexesToDelete.append(index)
                label = label + " [mv]"
            elif operation == 'COPY':
                label = label + " [cp]"
            else:
                raise "Unknown operation"
            # move it to the destination list after sorting again all entries
            self.AddItemToUiList(self.uiDestinationList, label)

        # If move mode delete the entry to make it clear it will be moved
        # delete in reverse order so that removing an index does not change the
        # indexes (removing will re index)
        for index in indexesToDelete[::-1]:
            self.uiSourceList.delete(index)

        # clear the selection
        self.uiSourceList.selection_clear(0, END)

    def onSourceButton(self):

        # stop any on going analysis thread
        if (self.mAnalyzeThread) and self.mAnalyzeThread.is_alive():
            print("stopping thread")
            self.mStopThreadRequest = True
            self.mAnalyzeThread.join(1.)

        # reset the source and destination lists
        self.uiSourceList.delete(0, END)
        self.uiDestinationList.delete(0, END)

        #query user for a new source folder
        folder = filedialog.askdirectory(title=self.T['SRC_cb_dlg'],
                                           mustexist=True,
                                         initialdir=self.mSourceFolder
                                           )
        self.uiSourceValue.set(folder)
        self.mSourceFolder = folder

        self.Log("%s: <%s>\n" % (self.T['SRC_cb_log'], self.uiSourceValue.get()))


        # start the source parsing thread
        self.mStopThreadRequest = False
        self.mAnalyzeThread = threading.Thread(target=self.AnalyzeWorkerThread)
        self.mAnalyzeThread.start()


    def onDestinationButton(self):
        folder = filedialog.askdirectory(title=self.T['DST_cb_dlg'],
                                         mustexist=True,
                                         #initialdir=os.path.expanduser('~/.')
                                         initialdir=self.mDestinationFolder
                                         )
        self.uiDestinationValue.set(folder)
        self.mDestinationFolder = folder
        self.Log("%s: <%s>\n" % (self.T['DST_cb_log'], self.uiDestinationValue.get()))



    def onProcessButton(self):
        #start the worker thread
        self.mStopThreadRequest = False
        self.mProcessThread = threading.Thread(target=self.ProcessWorkerThread)
        self.mProcessThread.start()


    def update_status(self, val):
        self.mStatusQueue.put(val)


    def AnalyzeWorkerThread(self):
        try:

            src = self.uiSourceValue.get()
            #dst = self.DST_val.get()

            # validate the arguments
            if not os.path.exists(src):
                messagebox.showerror (self.T['missing_src'], self.T['SRC_cb_dlg'])
                return
            # if not os.path.exists(dst) :
            #     messagebox.showerror (self.T['missing_dst'], self.T['DST_cb_dlg'])
            #     return
            self.mSourceFolder = src

            #disable the button to be sure it will not be hit while we run
            self.uiProcessButton["state"] = DISABLED

            self.mFilesPerDestinationFolder, filescnt = self.parse_source_folder_v2(src)

            self.Log("%d %s" % (filescnt, self.T['log1']))
            self.Log("%d %s" % (len(self.mFilesPerDestinationFolder.keys()), self.T['log2']))
            for folder in self.mFilesPerDestinationFolder.keys():
                self.Log(" - %s\n" % folder)

            # We can now populate the list with what we found (folders/images per folder)
            # clean previous results:
            self.uiSourceList.delete(0, END)
            self.uiDestinationList.delete(0, END)

            sortedFolders = sorted(self.mFilesPerDestinationFolder.keys())
            for folder in sortedFolders:
                files =self.mFilesPerDestinationFolder[folder]
                # count how many files will go in this folder
                folderItem = "%s (%d)" %(folder,len(files))
                self.uiSourceList.insert(END, folderItem)


            # job done, let's enable the button again
            self.uiProcessButton["state"] = NORMAL
        except Exception as e:
            if str(e) == "stopped":
                print("thread stopped")

                pass
            else:
                print (str(e))
        except:
            raise



    def CleanUserSelectedItems(self, items):
        cleaned_items = []
        for item in items:
            m = re.search(r"(\d{4}/\d{2})", item)
            if m:
                cleaned_items.append(m.group())
            else:
                raise Exception("item does not contain a folder")
        return cleaned_items

    def ProcessWorkerThread(self):
        try:
            #disable the button to be sure it will not be hit while we run
            self.uiProcessButton["state"] = DISABLED

            # retrieve the items selected for copying/moving
            src_folders_list = self.uiSourceList.get(0, END)
            dst_folders_list = self.uiDestinationList.get(0, END)

            #clean up the list inputs (they contain some statistics about the number of
            #files found per folder. keep only stuff that matches yyyy/mm
            src_folders = self.CleanUserSelectedItems(src_folders_list)
            dst_folders = self.CleanUserSelectedItems(dst_folders_list)


            self.CreateDestinationFolders(self.mDestinationFolder, dst_folders, debug=self.debug)

            self.ProcessFiles(src_folders, dst_folders)

            #job done, let's enable the button again
            self.uiProcessButton["state"] = NORMAL
        except Exception as e:
            if str(e) == "stopped":
                print("thread stopped")
                pass
        except:
            raise


    def AddItemToUiList(self, widget, item):
        # move it to the destination list after sorting again all entries
        current_items = widget.get(0,END)

        updated_items = [item]
        for item in current_items:
            updated_items.append(item)

        updated_items.sort()

        #update widget list ensuring no dupplicates are added
        widget.delete(0,END)
        for item in updated_items:
            if widget.get(END) != item:
                widget.insert(END,item)


    def get_capture_date(self,file_name):
        """
        :param file_name: name of a jpeg file
        :return: date a which the photo was taken
        """
        # default capture date in case exif parsing fails
        capture_date = datetime.datetime.strptime("1974:10:05 00:00:00", '%Y:%m:%d %H:%M:%S')

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
            else:
                # exif parsing failed, let's try interpreting the file name itself
                #print ("exif parsing failed, scaning file name %s" %file_name)
                m = re.search(r"\D?(?P<year>\d{4})\D?(?P<month>\d{2})\D?(?P<day>\d{2})\D?",file_name)
                if m is not None:
                    strCaptureDate = "%s:%s:%s 00:00:00" %(m.group('year'),m.group('month'),m.group('day'))
                    capture_date = datetime.datetime.strptime(strCaptureDate, '%Y:%m:%d %H:%M:%S')

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

        jpg_files = jpg_files + glob.glob(folder + "\\*.mp4")

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
                self.Log(("%s : %.2d %.4d \n" % (os.path.basename(file), capture_date.month, capture_date.year)))
            if destination not in unique_folders:
                unique_folders.add(destination)
            cnt += 1
            self.UpdateProgress(cnt,len(jpg_files))
            if self.mStopThreadRequest:
                raise Exception("stopped")
        print("%d files found" % len(jpg_files))
        print("%d destination folders(s) " % len(unique_folders))

        return destination_folders, unique_folders


    def parse_source_folder_v2(self, folder, verbose=True):
        """ find jpg files in the input folder
        :param folder: folder to parse
        :return: destination_folders : dict destination_folder_to_create -> list of files to copy
        :return: number of files found
        """

        # parse the input directory

        jpg_files = glob.glob(folder + "\\*.jpg")
        # windows does not care about case jpg_files = jpg_files + glob.glob(folder + "\\*.JPG")
        jpg_files = jpg_files + glob.glob(folder + "\\*.jpeg")

        jpg_files = jpg_files + glob.glob(folder + "\\*.mp4")

        # return values
        destination_folders = dict()
        # create all entries


        cnt = 0
        self.update_status(self.T['status1'])
        for file in jpg_files:
            capture_date = self.get_capture_date(file)
            destination = "%.4d/%.2d" % (capture_date.year, capture_date.month)
            if destination not in destination_folders:
                destination_folders[destination] = [file]
            else:
                destination_folders[destination].append(file)
            if verbose:
                self.Log(("%s : %.2d %.4d \n" % (os.path.basename(file), capture_date.month, capture_date.year)))
            cnt += 1
            self.UpdateProgress(cnt, len(jpg_files))
            if self.mStopThreadRequest:
                raise Exception("stopped")
        print("%d files found" % cnt)
        print("%d destination folders(s) " % len(destination_folders.keys()))

        return destination_folders,cnt

    def CreateDestinationFolders(self, dest_root, unique_destination_folders, debug=False):
        """ create output directories if needed """

        self.update_status(self.T['status2'])
        cnt = 0
        for folder in unique_destination_folders:
            #destination_folder = "%s\%s" % (dest_root, folder)
            destination_folder = os.path.join(dest_root,folder)
            if not os.path.exists(destination_folder):
                self.Log("%s %s\n" % (destination_folder, self.T['log3']))
                if not debug:
                    os.makedirs(destination_folder)
            else:
                self.Log("%s %s\n" % (destination_folder, self.T['log4']))
            cnt += 1
            self.UpdateProgress(cnt, len(unique_destination_folders))
            if self.mStopThreadRequest:
                raise Exception("stopped")

    def ProcessFiles(self, src_folders, dst_folders):
        """ move files to where they belong
        :param destination_folders: a file name ordered dict of destination folders
        :param move: boolean for moving vs copying
        :param debug: debug mode, if True, not file operation (move or copy) are performed
        """
        dest_root = self.mDestinationFolder

        # evaluate the total number of files to process

        cnt = 0
        total = 0
        skipped = []
        moved = []
        copied = []
        not_selected = []

        # update status message
        self.update_status(self.T['status3'])
        # evaluate the total number of files to process
        for folder in self.mFilesPerDestinationFolder.keys():
            total += len(self.mFilesPerDestinationFolder[folder])

        # loop on all folders to be processed
        for year_month in self.mFilesPerDestinationFolder.keys():
            # check the status of the destination folder associated to the current file
            destination_folder = os.path.join(dest_root, year_month)

            for file in self.mFilesPerDestinationFolder[year_month]:
                src_basename = os.path.basename(file)
                destination_file =os.path.join(destination_folder,src_basename)

                # if file already exist in destination skip it
                if os.path.exists(destination_file):
                    self.Log("%s %s %s\n" % (src_basename, self.T['log7'], destination_folder), type='W')
                    skipped.append(src_basename)
                    cnt += 1
                    continue # go to next file

                #decide between copying and moving using user selected lists
                #  check status of year month vs source and destination lists
                # if     in source and dst       : copy
                # if     in source and not in dst: do nothing
                # if not in source and     in dst: move
                # if not in source and not in dst: assert

                if  year_month  in src_folders:
                    if year_month in dst_folders:
                        if not self.debug:
                            shutil.copy(file, destination_folder)
                        self.Log("%s %s -> %s\n" % (self.T['log6'], src_basename, destination_folder))
                        copied.append(src_basename)
                    else:
                        self.Log("%s %s %s\n" % (src_basename, self.T['log11'], destination_folder))
                        not_selected.append(src_basename)
                else:
                    if year_month in dst_folders:
                        if not self.debug:
                            shutil.move(file, destination_folder)
                        self.Log("%s %s -> %s\n" % (self.T['log5'], src_basename, destination_folder))
                        moved.append(src_basename)
                    else:
                        raise NameError('Inconsistent src and dst lists')

                cnt +=1
                self.UpdateProgress(cnt, total)
                if self.mStopThreadRequest:
                    raise Exception("stopped")

        #time to update a status of what we did
        self.Log("%d %s\n" % (len(moved), self.T['log8']), type='I')
        self.Log("%d %s\n" % (len(copied), self.T['log9']), type='I')
        self.Log("%d %s\n" % (len(not_selected), self.T['log11']), type='I')
        self.Log("%d %s\n" % (len(skipped), self.T['log10']), type='W')

        for file in skipped:
            self.Log(" - %s\n" % file, type='W')


if __name__ == "__main__":

    root = tk.Tk()

    app = SortImages(master=root)
    app.mainloop()



