#!/usr/bin/env python3

import time
import json
import os
import re
from scanner import downloader, imageboard_info
from scanner.config import DB_FILE, currently_downloading
import sqlite3
import subprocess
import urllib.request
import threading
import http.client

class thread_scanner:
    def __init__(self, keywords_file, output, quota_mb, wait_time, logger):
        self.keywords_file = keywords_file
        self.output = output
        self.quota_mb = quota_mb
        self.wait_time = wait_time
        self.logger = logger


    def get_catalog_json(self, board, chan):
        chan_base_url = imageboard_info.imageboard_info(chan).base_url
        catalog = urllib.request.urlopen(
                "{0}{1}/catalog.json".format(chan_base_url, board))
        try:
            catalog_data = catalog.read()
        except http.client.IncompleteRead as err:
            catalog_data = err.partial
        return json.loads(catalog_data.decode("utf8"))


    def scan_thread(self, keyword, catalog_json, subject_only):
        # Check each thread, threads who contains the keyword are returned
        matched_threads = []
        for i in range(len(catalog_json)):
            for thread in catalog_json[i]["threads"]:
                regex = r'\b{0}\b'.format(keyword)
                # Search thread subject
                if 'sub' in thread:
                    if re.search(regex, str(thread["sub"]), re.IGNORECASE):
                        matched_threads.append(thread["no"])

                if not subject_only:
                    # Search OPs post body
                    if 'com' in thread:
                        if re.search(regex, str(thread["com"]), re.IGNORECASE):
                            matched_threads.append(thread["no"])

        return matched_threads


    def download_thread(self, thread_id, chan, board, folder, output, condition, dupe_check, tag_list):
        thread_downloader = downloader.downloader(thread_id, board,chan, output, folder, True, condition, dupe_check, tag_list, self.logger)
        t = threading.Thread(target=thread_downloader.download)
        t.daemon = True
        t.start()


    def was_downloaded(self, thread_nb):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("SELECT Thread_Number FROM Downloaded_Thread WHERE Thread_Number = ?", (thread_nb,))
        result = c.fetchone()

        conn.close()

        if result:
            return True
        else:
            return False

    def dir_size_mb(self, directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / 1000000


    def check_quota(self):
        if int(self.quota_mb) < dir_size_mb(os.path.join(self.output, "downloads")):
            self.logger.info("Quota limit exceeded. Stopping 4scanner.")
            exit(0)


    def get_check_duplicate(self, search):
        if 'check_duplicate' in search:
            if search['check_duplicate']:
                return True
            else:
                return False

        # duplicate check is on by default
        return True

    def get_condition(self, search):
        condition = {}
        if 'extension' in search:
            condition["ext"] = []
            if isinstance(search['extension'], str):
                condition["ext"].append(search['extension'])
            else:
                for extension in search['extension']:
                    condition["ext"].append(extension)
        else:
            condition["ext"] = False

        if 'filename' in search:
            condition["filename"] = []
            if isinstance(search['filename'], str):
                condition["filename"].append(search['filename'])
            else:
                for extension in search['filename']:
                    condition["filename"].append(extension)
        else:
            condition["filename"] = False

        if 'width' in search:
            condition["width"] = search['width']
        else:
            condition["width"] = False

        if 'height' in search:
            condition["height"] = search['height']
        else:
            condition["height"] = False

        return condition


    def get_imageboard(self, search):
        if 'imageboard' in search:
            chan = search["imageboard"]
            # will raise error if not supported
            imageboard_info.imageboard_info(chan)
        else:
            # default
            chan = "4chan"

        return chan

    def get_tag_list(self, search):
        if 'tag' in search:
            tag = search["tag"]
        else:
            tag = None

        return tag

    
    def get_subject_only(self, search):
        if 'subject_only' in search:
            subject_only = search["subject_only"]
        else:
            subject_only = None

        return subject_only


    def get_keyword(self, search):
        if 'keywords' in search:
            keywords_array = []
            if isinstance(search['keywords'], str):
                keywords_array.append(search['keywords'])
            else:
                for keywords in search['keywords']:
                    keywords_array.append(keywords)
        else:
            self.logger.critical("Cannot scan without any keyword...")
            exit(1)

        return keywords_array


    def scan(self):
        while True:
            if self.quota_mb:
                self.check_quota()

            self.logger.info("Searching threads...")

            try:
                json_file = json.load(open(self.keywords_file))
            except ValueError:
                self.logger.critical("Your JSON file is malformed. Quitting.")
                exit(1)

            for search in json_file["searches"]:
                # Getting imageboard to search
                chan = self.get_imageboard(search)
                # Checking conditions
                condition = self.get_condition(search)
                # Check if we need to check for duplicate when downloading
                dupe_check = self.get_check_duplicate(search)
                # Getting output folder name
                folder_name = search["folder_name"]
                # Get tag list (if any)
                tag_list = self.get_tag_list(search)
                # if this is true we will search only the subject field
                subject_only = self.get_subject_only(search)
                board = search["board"]
                keywords = self.get_keyword(search)

                try:
                    catalog_json = self.get_catalog_json(board, chan)

                    for keyword in keywords:
                        threads_id = self.scan_thread(keyword, catalog_json, subject_only)

                        for thread_id in list(set(threads_id)):
                            if thread_id not in currently_downloading and not self.was_downloaded(thread_id):
                                self.download_thread(thread_id, chan, board,
                                                folder_name, self.output,
                                                condition, dupe_check,
                                                tag_list)
                            # Used to keep track of what is currently downloading
                            currently_downloading.append(thread_id)
                except urllib.error.HTTPError as err:
                    self.logger.warning("Error while opening {0} catalog page. "
                                "Retrying during next scan.".format(board))
                    pass

            active_downloads = threading.active_count()-1
            self.logger.info("{0} threads currently downloading.".format(active_downloads))
            self.logger.info("Searching again in {0} minutes!".format(str(int(self.wait_time / 60))))
            time.sleep(self.wait_time)
