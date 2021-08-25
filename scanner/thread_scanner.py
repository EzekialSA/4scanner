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
    def __init__(self, keywords_file:str, output:str, quota_mb:int, wait_time:int, logger):
        """
        Using the keyword file passed as a paramater to 4scanner,
        thread_scanner will search multiple threads and imageboards
        and launch the download of a thread if a keyword is found in first post of the thread.
        Use scan() to start the scan.

        Args:
            keywords_file: path of file containing whats imageboard to search as JSON (see README for more info)
            output: The output directory where the pictures will be downloaded
            quota_mb: stop 4scanner after quota_mb MB have been downloaded
            throttle: Time to wait, in second, between image downloads
            wait_time: number of time to wait between scans
        """

        self.keywords_file = keywords_file
        self.output = output
        self.quota_mb = quota_mb
        self.wait_time = wait_time
        self.logger = logger


    def get_catalog_json(self, board:str, chan:str):
        """
        Get the catalog of a given imageboards board as a JSON

        Return:
            catalog info as a dict
        """

        chan_base_url = imageboard_info.imageboard_info(chan).base_url
        catalog = urllib.request.urlopen(
                "{0}{1}/catalog.json".format(chan_base_url, board))
        try:
            catalog_data = catalog.read()
        except http.client.IncompleteRead as err:
            catalog_data = err.partial
        return json.loads(catalog_data.decode("utf8"))


    def scan_thread(self, keyword:str, catalog_json:str, subject_only:str, wildcard:str):
        """
        Check each thread, threads who contains the keyword are returned

        Args:
            keyword: A keyword to search for. Example: "moot"
            catalog_json: A dict of a board catalog, as returned by get_catalog_json()
            subject_only: Search only withing the subject of the thread, as oposed to searching the subject and first post

        Returns:
            a list of threads number that matched the keyword
        """

        matched_threads = []
        for i in range(len(catalog_json)):
            for thread in catalog_json[i]["threads"]:
                if not wildcard:
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
                else:
                    regex = r'{0}'.format(keyword)
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


    def download_thread(self, thread_id:int, chan:str, board:str, folder:str, output:str, condition:dict, dupe_check:bool, tag_list:list, throttle:int):
        """
        Create a downloader object with the info passed as paramater and start the download of in a new thread.
        """

        thread_downloader = downloader.downloader(thread_id, board,chan, output, folder, True, condition, dupe_check, tag_list, throttle, self.logger)
        t = threading.Thread(target=thread_downloader.download)
        t.daemon = True
        t.start()


    def dir_size_mb(self, directory):
        """
        Check the size of a directory in MB.

        Args:
            directory: the path to a directory

        Returns:
            Size of the directory in MB
        """

        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / 1000000


    def check_quota(self):
        """
        Stop 4scanner of the download quota was reached.
        """

        if int(self.quota_mb) < dir_size_mb(os.path.join(self.output, "downloads")):
            self.logger.info("Quota limit exceeded. Stopping 4scanner.")
            exit(0)


    def get_check_duplicate(self, search):
        """
        Check whether to activate the check duplicate feature

        Returns:
            True if we need to activate it, False otherwise
        """

        if 'check_duplicate' in search:
            if search['check_duplicate']:
                return True
            else:
                return False

        # duplicate check is on by default
        return True

    def get_condition(self, search:dict):
        """
        Get all search condition from a search

        Returns:
            All search conditions as a dict
        """

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


    def get_imageboard(self, search:dict):
        """
        get imageboard from a search

        Returns:
            imageboard_info object of an imageboard
        """

        if 'imageboard' in search:
            chan = search["imageboard"]
            # will raise error if not supported
            imageboard_info.imageboard_info(chan)
        else:
            # default
            chan = "4chan"

        return chan

    def get_tag_list(self, search):
        """
        get all tags from a search

        Returns:
            a list containing all tags or None
        """

        if 'tag' in search:
            tag = search["tag"]
        else:
            tag = None

        return tag


    def get_subject_only(self, search):
        """
        Check whether to search only the subject of post for a given search.

        Returns:
            True to get subject only, False otherwise
        """

        if 'subject_only' in search:
            subject_only = search["subject_only"]
        else:
            subject_only = None

        return subject_only

    def get_wildcard(self, search):
        """
        Check whether to search only the subject of post for a given search.

        Returns:
            True to get subject only, False otherwise
        """

        if 'wildcard' in search:
            wildcard = search["wildcard"]
        else:
            wildcard = None

        return wildcard


    def get_keyword(self, search):
        """
        get a list of all keywords to use in a search.

        Returns:
            list of all keywords to search for
        """

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
        """
        Start the scanning/download process.
        """
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
                # Get throttle
                throttle = int(search['throttle']) if 'throttle' in search else 2
                # if this is true we will search only the subject field
                subject_only = self.get_subject_only(search)
                wildcard = self.get_wildcard(search)
                board = search["board"]
                keywords = self.get_keyword(search)

                try:
                    catalog_json = self.get_catalog_json(board, chan)

                    for keyword in keywords:
                        threads_id = self.scan_thread(keyword, catalog_json, subject_only, wildcard)

                        for thread_id in list(set(threads_id)):
                            if thread_id not in currently_downloading:
                                self.download_thread(thread_id, chan, board,
                                                folder_name, self.output,
                                                condition, dupe_check,
                                                tag_list, throttle)
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
