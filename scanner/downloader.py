#!/usr/bin/env python3

import argparse
from scanner import chan_info, dupecheck
import json
import logging
import os
import sys
import re
import time
import urllib
import http.client
import requests
import threading
import shutil

class downloader:

    def __init__(self, thread_nb, board, chan, output_folder, folder, is_quiet, condition, check_duplicate):
        # Getting info about the chan URL
        chan_url_info = chan_info.get_chan_info(chan)
        if not chan_url_info:
            print("{0} does not exist or is not supported.".format(chan))
            exit(1)
        base_url = chan_url_info[0]
        image_url = chan_url_info[3]
        thread_subfolder = chan_url_info[1]
        image_subfolder = chan_url_info[2]

        # These URL are the url of the thread
        # and the base url where images are stored on the imageboard
        self.thread_url = "{0}{1}{2}{3}.json".format(base_url, board, thread_subfolder, thread_nb)
        self.image_url = "{0}{1}{2}".format(image_url, board, image_subfolder)

        self.tmp_dir = "/tmp/{0}/".format(os.getpid())
        self.curr_time = time.strftime('%d%m%Y-%H%M%S')
        self.pid = os.getpid()
        self.thread = threading.current_thread().name

        self.downloaded_log = "{0}/{1}4scanner_dld-{2}-{3}".format(self.tmp_dir, self.curr_time, self.pid, self.thread)
        self.img_hash_log = "{0}/{1}4scanner_hash-{2}-{3}".format(self.tmp_dir, self.curr_time, self.pid, self.thread)

        self.out_dir = os.path.join(output_folder, 'downloads', chan, board, folder)

        self.thread_nb = thread_nb
        self.chan = chan
        self.condition = condition
        self.check_duplicate = check_duplicate
        self.is_quiet = is_quiet


    # Main download function
    def download(self):

        # Creating the tmp and output directory
        self.create_dir(self.tmp_dir)
        self.create_dir(self.out_dir)

        # Fill the hash_log file with hash from image already in the dir
        dupecheck.hash_img_in_folder(self.out_dir, self.img_hash_log, self.check_duplicate)

        while True:
            # Getting the thread's json
            try:
                thread_json = json.loads(self.get_thread_json())
            except ValueError:
                print("Problem connecting to {0}. stopping download for thread {1}".format(self.chan, self.thread_nb))
                self.remove_tmp_files()
                exit(1)

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
                            else:
                                shutil.move(tmp_pic, final_pic)

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
                                else:
                                    shutil.move(tmp_pic, final_pic)


                                time.sleep(2)
            if not self.is_quiet:
                print('.')
            time.sleep(20)


    def get_thread_json(self):
        response = requests.get(self.thread_url)
        if response.status_code == 404:
            if not self.is_quiet:
                print('thread 404\'d')
            self.remove_tmp_files()
            exit(0)
        return response.text


    def create_dir(self, directory):
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:  # folder may have been created by other threads
                if e.errno != 17:
                    print("Cannot create {0}".format(directory))
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
                print("width need to be in this format:")
                print(">1024, <256 or =1920")
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
                print("height need to be in this format:")
                print(">1024, <256 or =1080")
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
            if dupecheck.is_duplicate(self.img_hash_log, img_hash):
                os.remove(img_path)
                return True
            else:
                dupecheck.add_to_file(self.img_hash_log, img_hash)
                return False


    def remove_tmp_files(self):
        if os.path.isfile(self.img_hash_log):
            os.unlink(self.img_hash_log)

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
