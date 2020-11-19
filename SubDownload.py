import praw
import requests
import cv2
import numpy as np
import os
import pickle
import failed_downloader
import duplicate_finder as df
from settings import returnSettings as rs
import folder_remover as fr
from utilities.create_token import create_token

settings = rs()

"""
To add new subs to the download_list, add the subs to new.csv, one subreddit per line
without the r/

Example:
sub1
sub2
r/sub3 will cause errors
"""


# Create directory if it doesn't exist to save images
def create_folder(img_path):
    CHECK_FOLDER = os.path.isdir(img_path)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(img_path)


# Path to save images
dir_path = os.path.dirname(os.path.realpath(__file__))
image_path = os.path.join(dir_path, "images/")
ignore_path = os.path.join(dir_path, "ignore_images/")
create_folder(image_path)

# Get token file to log into reddit.
# You must enter your....
# client_id - client secret - user_agent - username password
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
else:
    creds = create_token()
    pickle_out = open("token.pickle", "wb")
    pickle.dump(creds, pickle_out)

reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     username=creds['username'],
                     password=creds['password'])

print("If this is your first time running, please select New.")
question = input("New, all, big, small?").lower()
if question in ["n", "new"]:
    f_final = open("new.csv", "r")
    POST_SEARCH_AMOUNT = settings["new_query_limit"]
elif question in ["b", "big"]:
    f_final = open("big_subs.csv")
    POST_SEARCH_AMOUNT = settings["big_query_limit"]
elif question in ["s", "small"]:
    f_final = open("small_subs.csv")
    POST_SEARCH_AMOUNT = settings["small_query_limit"]
else:
    f_final = open("sub_list.csv", "r")
    POST_SEARCH_AMOUNT = settings["all_query_limit"]


for line in f_final:
    sub = line.strip()
    subreddit = reddit.subreddit(sub)

    print(f"Starting {sub}!")
    try:
        for submission in subreddit.new(limit=POST_SEARCH_AMOUNT):
            if "jpg" in submission.url.lower() or "png" in submission.url.lower():
                try:
                    path = submission.url.lower()
                    resp = requests.get(path, stream=True).raw
                    image = np.asarray(bytearray(resp.read()), dtype="uint8")
                    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                    # Could do transforms on images like resize!
                    compare_image = cv2.resize(image, (224, 224))

                    # Get all images to ignore
                    for (dirpath, dirnames, filenames) in os.walk(ignore_path):
                        ignore_paths = [os.path.join(dirpath, file) for file in filenames]
                    ignore_flag = False

                    for ignore in ignore_paths:
                        ignore = cv2.imread(ignore)
                        difference = cv2.subtract(ignore, compare_image)
                        b, g, r = cv2.split(difference)
                        total_difference = cv2.countNonZero(b) + cv2.countNonZero(g) + cv2.countNonZero(r)
                        if total_difference == 0:
                            ignore_flag = True

                    if not ignore_flag:
                        subrfolder = os.path.join(image_path, f"{sub}/")
                        create_folder(subrfolder)
                        cv2.imwrite(f"{subrfolder}{sub}-{submission.id}.png", image)

                except Exception as e:
                    with open("failed.csv", "a") as writer:
                        writer.write(f"{sub}: {submission.url.lower()}\n")
    except Exception as e:
        print(e)


clear = open("new.csv", "w")
clear.close()

print("Retrying failed downloads")
failed_downloader.failed()

print("Checking for duplicates")
df.duplicate_finder()

print("Removing junk folders/Fixing sub lists")
fr.clean_subs()
