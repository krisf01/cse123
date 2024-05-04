import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
import requests
import time




COMMANDS_FILE = 'instructions.txt'
UPLOAD_FOLDER_TEXTS = '/Users/kristinaf/cse123team4/cse123'
WATCHED_FOLDER_PICTURES = '/Users/kristinaf/cse123team4/cse123/images'
WATCHED_FOLDER_TEXTS = '/Users/kristinaf/cse123team4/cse123/data'
TARGET_SERVER_URL = 'http://10.0.0.98:8080/api/upload'
command_url = 'http://10.0.0.98:8080/api/commands'
#TARGET_SERVER_URL = 'http://192.0.0.2:8080/api/receive_data'
#command_url = 'http://192.00.0.0:8080/api/commands'


# Ensure the necessary folders exist
if not os.path.exists(UPLOAD_FOLDER_TEXTS):
   os.makedirs(UPLOAD_FOLDER_TEXTS)
if not os.path.exists(WATCHED_FOLDER_PICTURES):
   os.makedirs(WATCHED_FOLDER_PICTURES)
if not os.path.exists(WATCHED_FOLDER_TEXTS):
   os.makedirs(WATCHED_FOLDER_TEXTS)


last_sent_time = datetime.min


def validate_token(auth_token):
   expected_token = "AuPvJrbUlcueojGQLNE6RA"  # This should ideally be stored securely
   return auth_token == expected_token


def send_file_to_server(file_path):
   global last_sent_time
   now = datetime.now()
   is_text_file = file_path.endswith('.txt')


   if is_text_file and now - last_sent_time < timedelta(seconds=10):
       return


   try:
       with open(file_path, 'r') as file:
           lines = file.readlines()


       for line in lines:
           files = {'file': (os.path.basename(file_path), line)}
           headers = {'Authorization': 'Bearer AuPvJrbUlcueojGQLNE6RA'}
           response = requests.post(TARGET_SERVER_URL, files=files, headers=headers, verify=True)
           print(f"Line sent to server from {file_path}, Status Code: {response.status_code}")


           if response.status_code != 200:
               raise Exception(f"Failed to send line: {line.strip()}")


       if is_text_file:
           with open(file_path, 'w') as file:
               file.truncate(0)
           print(f"Data from {file_path} cleared after successful transmission.")
           last_sent_time = now


   except requests.exceptions.SSLError as e:
       print(f"SSL Error when sending file to server: {e}")
   except Exception as e:
       print(f"Failed to send {file_path} to server: {e}")




class FileEventHandler(FileSystemEventHandler):
   def on_modified(self, event):
       if not event.is_directory and 'data.txt' == os.path.basename(event.src_path):
           print(f"Modification detected in: {event.src_path}")
           send_file_to_server(event.src_path)


   def on_created(self, event):
       if not event.is_directory and event.src_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
           print(f"New picture detected: {event.src_path}")
           send_file_to_server(event.src_path)


def start_watcher():
   observer = Observer()
   observer.schedule(FileEventHandler(), WATCHED_FOLDER_PICTURES, recursive=True)
   observer.schedule(FileEventHandler(), WATCHED_FOLDER_TEXTS, recursive=True)
   observer.start()
   try:
       observer.join()
   except Exception as e:
       print(f"Error starting observer: {e}")


def fetch_and_write_commands():
   while True:
       headers = {'Authorization': 'Bearer AuPvJrbUlcueojGQLNE6RA'}
       try:
           response = requests.get(command_url, headers=headers)
           if response.status_code == 200:
               commands = response.json().get('commands', [])
               for command in commands:
                   print(f"Executing command: {command}")
                   # Here you would add logic to act on the command
               # Clear the commands file after executing to prevent re-execution
               open(COMMANDS_FILE, 'w').close()
           else:
               print("Failed to fetch commands:", response.status_code, response.text)
       except requests.exceptions.RequestException as e:
           print(f"Error fetching commands: {e}")
       time.sleep(10)  # Polling interval






if __name__ == "__main__":
   watcher_thread = threading.Thread(target=start_watcher)
   command_fetch_thread = threading.Thread(target=fetch_and_write_commands)


   watcher_thread.start()
   command_fetch_thread.start()
