import os
import datetime

class Logger: # to store what was the latest successful URL (after saved in SQL)
    def __init__(self):
        self.log_dir = "logger/logs"
        self.log_file = self.get_log_file_name()
        self.file = open(self.log_file, 'a', encoding='utf-8')


    def get_log_file_name(self):
        current_datetime = datetime.datetime.now()
        return os.path.join(self.log_dir, f"trial_{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.txt")

    def log_message(self, message):
        self.file.write(message + '\n')

    def close_log_file(self):
        self.file.close()
