#!/usr/bin/env python3


import json
import logging
import os
from scanner import imageboard_info, dupecheck
from scanner.config import DB_FILE, currently_downloading
import sqlite3
import sys
import re
import time
import urllib
import http.client
import requests
import threading
import shutil

class downloader:

    def __init__(self, thread_nb, board, imageboard, output_folder, folder, is_quiet, condition, check_duplicate, tag_list, logger):
        # Getting info about the imageboard URL
        ib_info = imageboard_info.imageboard_info(imageboard)

        base_url = ib_info.base_url
        image_url = ib_info.image_base_url
        thread_subfolder = ib_info.thread_subfolder
        image_subfolder = ib_info.image_subfolder

        # These URL are the url of the thread
        # and the base url where images are stored on the imageboard
        self.thread_url = "{0}{1}{2}{3}.json".format(base_url, board, thread_subfolder, thread_nb)
        self.image_url = "{0}{1}{2}".format(image_url, board, image_subfolder)

        self.tmp_dir = "/tmp/{0}/".format(os.getpid())
        self.curr_time = time.strftime('%d%m%Y-%H%M%S')
        self.pid = os.getpid()
        self.thread = threading.current_thread().name

        self.downloaded_log = "{0}/{1}4scanner_dld-{2}-{3}".format(self.tmp_dir, self.curr_time, self.pid, self.thread)

        self.out_dir = os.path.join(output_folder, 'downloads', imageboard, board, folder, str(thread_nb))

        self.thread_nb = thread_nb
        self.imageboard = imageboard
        self.board = board
        self.condition = condition
        self.check_duplicate = check_duplicate
        self.is_quiet = is_quiet
        self.tag_list = tag_list

        # Creating the tmp and output directory
        self.create_dir(self.tmp_dir)
        self.create_dir(self.out_dir)

        self.logger = logger


    # Main download function
    def download(self):
        self.logger.info("{}: Starting download.".format(self.thread_url))
        while True:
            # Getting the thread's json
            try:
                thread_json = json.loads(self.get_thread_json())
            except ValueError:
                self.logger.critical("{}: Problem connecting to {0}. stopping download for thread {1}".format(self.thread_url, self.imageboard, self.thread_nb))
                self.remove_thread_from_downloading()
                self.remove_tmp_files()
                exit(1)

            # Checking if thread was archived, if it is it will be removed after the download loop
            if thread_json["posts"][0].get("archived"):
                if not self.is_quiet:
                    self.logger.info("{}: Thread is archived, getting images then quitting.".format(self.thread_url))
                archived = True
            else:
                archived = False

            # Image download loop
            for post in thread_json["posts"]:
                if 'filename' in post:
                    if not self.was_downloaded(post["tim"]):
                        if self.meet_dl_condition(post):
                            tmp_pic = self.download_image(post)
                            final_pic = os.path.join(self.out_dir, tmp_pic.split('/')[-1])
                            self.add_to_downloaded_log(post["tim"])

                            if self.check_duplicate:
                                # If picture is not a duplicate copy it to out_dir
                                if not self.remove_if_duplicate(tmp_pic):
                                    shutil.move(tmp_pic, final_pic)
                                    self.add_tag_file(final_pic + ".txt")
                            else:
                                shutil.move(tmp_pic, final_pic)
                                self.add_tag_file(final_pic + ".txt")

                            time.sleep(2)

                # Some imageboards allow more than 1 picture per post
                if 'extra_files' in post:
                    for picture in post["extra_files"]:
                        if not self.was_downloaded(picture["tim"]):
                            if self.meet_dl_condition(picture):
                                tmp_pic = self.download_image(picture)
                                final_pic = os.path.join(out_dir, tmp_pic.split('/')[-1])
                                self.add_to_downloaded_log(picture["tim"])

                                if self.check_duplicate:
                                    # If picture is not a duplicate copy it to out_dir
                                    if not self.remove_if_duplicate(tmp_pic):
                                        shutil.move(tmp_pic, final_pic)
                                        self.add_tag_file(final_pic + ".txt")
                                else:
                                    shutil.move(tmp_pic, final_pic)
                                    self.add_tag_file(final_pic + ".txt")


                                time.sleep(2)
            if archived:
                self.remove_thread_from_downloading()
                self.remove_tmp_files()
                exit(0)
    
            time.sleep(20)


    def remove_thread_from_downloading(self):
        # In a try except because 4downloader do not store threads in this list
        try:
            scanner.currently_downloading.remove(self.thread_nb)
        except NameError as e:
            pass


    def add_thread_to_downloaded(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("INSERT INTO Downloaded_Thread (Thread_Number, Imageboard, Board) VALUES (?, ?, ?)",
                 (self.thread_nb, self.imageboard, self.board))

        conn.commit()
        conn.close()


    def get_thread_json(self):
        response = requests.get(self.thread_url)
        if response.status_code == 404:
            if not self.is_quiet:
                self.logger.info("{}: thread 404\'d, stopping download".format(self.thread_url))
            self.remove_thread_from_downloading()
            self.add_thread_to_downloaded()
            exit(0)
        return response.text


    def create_dir(self, directory):
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:  # folder may have been created by other threads
                if e.errno != 17:
                    self.logger.critical("{}: Cannot create {}".format(self.thread_url, directory))
                    self.remove_thread_from_downloading()
                    exit(1)
                pass


    def add_to_downloaded_log(self, img_filename):
        f = open(self.downloaded_log, "a")
        f.write("{0}\n".format(img_filename))
        f.close()


    def was_downloaded(self, img_filename):
        if os.path.isfile(self.downloaded_log):
            f = open(self.downloaded_log, "r")
            if str(img_filename) in f.read():
                f.close()
                return True
            else:
                return False
        else:
            return False


    def extension_condition(self, condition_ext, post_ext):
        if condition_ext:
            for extension in condition_ext:
                if extension == post_ext:
                    return True
        else:
            # Always return true if condition was not specified
            return True

        return False


    def filename_condition(self, condition_filename, post_filename):
        if condition_filename:
            for i in condition_filename:
                if i.lower() in post_filename.lower():
                    return True
        else:
            # Always return true if condition was not specified
            return True

        return False


    def width_condition(self, condition_width, post_width):
        if condition_width:
            if condition_width[0] == "=":
                if int(post_width) == int(condition_width.split("=")[-1]):
                    return True
            elif condition_width[0] == "<":
                if int(post_width) < int(condition_width.split("<")[-1]):
                    return True
            elif condition_width[0] == ">":
                if int(post_width) > int(condition_width.split(">")[-1]):
                    return True
            else:
                self.logger.critical("{}: width need to be in this format: >1024, <256 or =1920".format(self.thread_url))
                exit(1)
        else:
            # Always return true if condition was not specified
            return True

        return False


    def height_condition(self, condition_height, post_height):
        if condition_height:
            if condition_height[0] == "=":
                if int(post_height) == int(condition_height.split("=")[-1]):
                    return True
            elif condition_height[0] == "<":
                if int(post_height) < int(condition_height.split("<")[-1]):
                    return True
            elif condition_height[0] == ">":
                if int(post_height) > int(condition_height.split(">")[-1]):
                    return True
            else:
                self.logger.critical("{}: height need to be in this format: >1024, <256 or =1080".format(self.thread_url))
                exit(1)
        else:
            # Always return true if condition was not specified
            return True

        return False


    # Check if all condition returned true
    def all_condition_check(self, condition_list):
        for i in condition_list:
            if not i:
                return False
        return True


    # Return True if an image fit all search conditions
    def meet_dl_condition(self, post):
        condition_list = []
        condition_list.append(self.extension_condition(self.condition["ext"], post['ext']))
        condition_list.append(self.width_condition(self.condition["width"], post['w']))
        condition_list.append(self.height_condition(self.condition["height"], post['h']))
        condition_list.append(self.filename_condition(self.condition["filename"], post['filename']))
        return self.all_condition_check(condition_list)


    def remove_if_duplicate(self, img_path):
        if img_path:
            img_hash = dupecheck.hash_image(img_path)
            if dupecheck.is_duplicate(img_hash):
                os.remove(img_path)
                return True
            else:
                dupecheck.add_to_db(img_hash, self.thread_nb)
                return False


    def remove_tmp_files(self):
        if os.path.isfile(self.downloaded_log):
            os.unlink(self.downloaded_log)


    # Return downloaded picture path or false if an error occured
    def download_image(self, post_dic):
        try:
            pic_url = self.image_url + str(post_dic["tim"]) + post_dic["ext"]
            out_pic = os.path.join(self.tmp_dir, str(post_dic["tim"]) + post_dic["ext"])
            urllib.request.urlretrieve(pic_url, out_pic)
        except urllib.error.HTTPError as err:
            return False

        return out_pic

    def add_tag_file(self, tag_file):
        if self.tag_list:
            with open(tag_file, 'w') as f:
                for tag in self.tag_list:
                    f.write(tag + "\n") 
