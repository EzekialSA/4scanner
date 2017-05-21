#!/usr/bin/env python3

class imageboard_info:

    def __init__(self, imageboard):
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
