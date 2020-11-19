import os
import random
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
from settings import returnSettings as rs

"""
Random subreddit slideshow using downloaded subreddits.
After choosing the amount of subs to queue, click the opened window to see the slideshow

Note: Please run duplicate_finder.py and folder_remover.py before using. Subdownload.py
will run both of them for you. So its not necessary to rerun them.
"""

class SlideShow:

    def pick_subs(self, i):
        if i == 1:
            sub = random.choice(self.folders)
            print(sub)
            return self.image_loop(sub)
        sub = random.choice(self.folders)
        print(sub)
        self.image_loop(sub)
        return self.pick_subs(i-1)

    def __init__(self, num):
        self.crawler = FileCrawler()
        self.folders = self.crawler.pull_folders()
        self.settings = rs()
        self.num = num
        self.height = self.settings["slideshow_height"]
        self.width = self.settings["slideshow_width"]

        self.image_window = tk.Tk()

        self.image_window.geometry(f"900x900")
        self.image_window.bind("<Configure>", self._resize_image)
        image_frame = tk.Frame(self.image_window)
        image_frame.pack(fill="both")
        self.image_label = tk.Label(image_frame, anchor="center", width=900, height=900)
        self.image_label.pack(fill="both")

        if self.num != 0:
            thread = threading.Thread(target=self.pick_subs, args=(self.num,))
            thread.daemon = True
            thread.start()
        else:
            folder = input("Folder name: ")
            thread = threading.Thread(target=self.image_loop, args=(folder,))
            thread.daemon = True
            thread.start()

        self.image_window.focus()
        self.image_window.mainloop()

    def _resize_image(self, event):
        self.width = event.width
        self.height = event.height
        self.image_label.configure(height=self.height, width=self.width)

    def image_loop(self, folder):
        self.image_window.title(folder)
        file_list = self.crawler.file_list(folder)
        random.shuffle(file_list)

        for file in file_list:

            l = Image.open(file)

            w, h = l.size
            if w > h:
                ya = round(h / (w / self.width))
                h = ya
                w = self.width
            else:
                xa = round(w / (h / self.height))
                h = self.height
                w = xa

            l = l.resize((w, h))
            r = ImageTk.PhotoImage(l)

            self.image_label.configure(image=r)

            time.sleep(int(self.settings["slideshow_wait"]))


class FileCrawler:

    def __init__(self):
        self.folder_list = []
        directory = os.getcwd()
        self.folder_names = {}

        for root, dirs, files in os.walk(directory, followlinks=False):
            for folder in dirs:
                file_list = []
                direct = os.path.join(root, folder)

                for filename in os.listdir(direct):
                    if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                        filepath = os.path.join(direct, filename)
                        file_list.append(filepath)

                if len(file_list) != 0:
                    self.folder_names.update({direct: file_list})
                else:
                    continue

    def pull_folders(self):
        for key in self.folder_names:
            self.folder_list.append(key)
        return self.folder_list

    def file_list(self, folder):
        return self.folder_names[folder]


print("Input 0 to choose Folder.")
q = input("Number of random folders to queue?")
a = SlideShow(int(q))
