from os import getcwd, chdir, path

from django.conf import settings
from dotenv import load_dotenv


def load_settings():
    temp = getcwd()
    chdir(path.dirname(path.abspath(__file__)))
    load_dotenv(".env")
    chdir(temp)
