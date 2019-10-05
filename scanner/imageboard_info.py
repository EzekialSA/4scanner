#!/usr/bin/env python3

class imageboard_info:

    def __init__(self, imageboard):
        """
        Used to get info about the differents supported imageboards.
        self.base_url is the URL of the image board
        self.image_base_url is the URL where the pictures are hosted (sometime the same as base_url)
        self.thread_picture is the url path where the pictures are hosted
        self.thread_subfolder is the url path where the threads are hosted
        """

        if imageboard == "4chan":
            self.base_url = "http://a.4cdn.org/"
            self.image_base_url = "http://i.4cdn.org/"
            self.thread_subfolder = "/thread/"
            self.image_subfolder = "/"
        elif imageboard == "lainchan":
            self.base_url = "https://lainchan.org/"
            self.image_base_url = "https://lainchan.org/"
            self.thread_subfolder = "/res/"
            self.image_subfolder = "/src/"
        elif imageboard == "uboachan":
            self.base_url = "https://uboachan.net/"
            self.image_base_url = "https://uboachan.net/"
            self.thread_subfolder = "/res/"
            self.image_subfolder = "/src/"
        else:
            raise ValueError("Imageboard {0} is not supported.".format(imageboard))
