# Used to store package wide constants
import os

if os.path.isdir(os.path.expanduser("~/.4scanner")):
    DB_FILE = os.path.expanduser("~/.4scanner/4scanner.db")
elif os.getenv("XDG_DATA_HOME"):
    DB_FILE = os.path.join(os.getenv("XDG_DATA_HOME"), "4scanner", "4scanner.db")
elif os.getenv("APPDATA"):
    DB_FILE = os.path.join(os.getenv("APPDATA"), "4scanner", "4scanner.db")
else:
    DB_FILE = os.path.join(os.getenv("HOME"), ".local", "share", "4scanner", "4scanner.db")

# Global variable used to keep track of what is downloading
currently_downloading = []
