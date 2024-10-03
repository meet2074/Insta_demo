import os

class env:
    key = os.getenv("key")
    algo = os.getenv("algo")
    DATABASE_URL = os.getenv("DATABASE_URL")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    
    
    