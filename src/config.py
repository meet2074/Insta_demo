import os

key = os.getenv("key")
algo = os.getenv("algo")
access_token_min = int(os.getenv("access_token_min"))
refresh_token_days = int(os.getenv("refresh_token_days"))
otp_exp_time_min= int(os.getenv("otp_exp_time_min"))
DATABASE_URL = os.getenv("DATABASE_URL")