import requests
import os
import shutil
from git import Repo

from database_connector import getUserId

root_url = "http://127.0.0.1:5000/"
user_name = "ernie"
user_pass = "bert"


def register_ernie():

    data = {
        "username":user_name,
        "password":user_pass
        }
    response = requests.post(root_url+"register",json=data)
    assert(response.status_code == 200)


def get_user_data():
    print("****Make sure git lfs is installed in order to download the project files****")
    repo_name = 'functionalscope-data'
    repo_download_path = os.getcwd() + '/' + repo_name + "/"
    git_url = 'git@github.com:grasbrook-cityscope/' + repo_name + '.git'

    print("cloning data repo")
    Repo.clone_from(git_url, repo_download_path)

    # copy recursive from downloaded git repo dir to user dir
    print("copying files to user folder", getUserId(user_name))
    user_dir = os.getcwd() + "/data/user/" + getUserId(user_name) + "/"
    global_dir = os.getcwd() + "/data/global/"
    recursive_copy(repo_download_path, user_dir, global_dir)

    print("deleting download folder")
    shutil.rmtree(repo_download_path)



# recursively copy files to their destinations
def recursive_copy(src, user_dest, global_dest, recursive_dest=None):
    if recursive_dest:
        dest = recursive_dest
    else:
        dest = global_dest

    os.chdir(src)

    for item in os.listdir():
        # copy files
        if os.path.isfile(os.path.join(src, item)):
            if item[0] == ".":
                # ignore dot files
                continue
            if item[-5:] == ".json":  # copy only jsons
                shutil.copy(os.path.join(src, item), dest)

        # handle folders
        elif os.path.isdir(os.path.join(src, item)):
            if item == "user":
                new_dst = user_dest  # copy user files to user folder
            elif item == "global":
                new_dst = global_dest  # copy global files to global folder
            else:
                new_dst = os.path.join(dest, item)  # else keep folder structure inside source data

            if not os.path.isdir(new_dst):
                os.mkdir(new_dst)

            new_src = os.path.join(src, item)
            recursive_copy(new_src, user_dest, global_dest, new_dst)


if __name__ == "__main__":
    try:
        register_ernie()
    except:
        print("user cannot be created , might already exist", "username: ", user_name)

    get_user_data()