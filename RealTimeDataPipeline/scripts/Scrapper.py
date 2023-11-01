import json
import logging
from randomuser import RandomUser
from datetime import datetime
import os


def setupLogging():
    # Create a directory called 'scrapping' if it doesn't exist
    log_directory = './logs/Scrapping_Log_Files'
    
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Generate a timestamp for the log file name
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Configure the logging system
    log_file = os.path.join(log_directory, f'{current_time}_scrapping.log')

    return log_file 

def scrappUsers():
    log_file = setupLogging()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Initialize the RandomUser API
        user_api = RandomUser()
        
        user_data = user_api._data    

        log_file.info(f"{current_time} - User Scrapped Successfully")

        return user_data
    
    except ValueError as ve:
        log_file.error(f"{current_time} - JSON parsing error: {ve}")
    except IOError as ioe:
        log_file.error(f"{current_time} - IO error: {ioe}")
    except Exception as e:
        log_file.error(f"{current_time} - An unexpected error occurred: {e}")
