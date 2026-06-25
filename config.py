import os
from configparser import ConfigParser
import sys

def initialize_secret_key() -> str:
    if SECRET_KEY := os.environ.get("SECRET_KEY"):
        return SECRET_KEY
    con_par = ConfigParser()
    con_par.read("config.cfg")
    file = con_par["secret-key"]["secret_key"]
    if not file:
        sys.exit(1)
    return file