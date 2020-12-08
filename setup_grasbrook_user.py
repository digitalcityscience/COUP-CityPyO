import requests
import os
import zipfile
import json
import getpass

from database_connector import getUserId

# todo load from file
root_url = "http://127.0.0.1:5000/"
src_folder_cloud = "cityPyoData"

cwd = os.getcwd()


# getting user credentials from local file
def get_cityPyo_user_credentials():
    with open('user_credentials.json', 'r') as f:
        user_creds = json.load(f)

    return user_creds["username"], user_creds["password"]


def register_grasbrook_user():
    user_name, user_pass = get_cityPyo_user_credentials()

    data = {
        "username":user_name,
        "password":user_pass
        }

    response = requests.post(root_url+"register",json=data)

    print(response.status_code)

    if response.status_code == 200:
        print("Sucessfully registered the user")

    elif response.status_code == 403:
        print("user already exits")

    else:
        print("could not register user for unknown reason")
        print(response.status_code)


# prompts for login credentials to the hcu cloud
def get_user_credentials_for_hcu_cloud():
    print("provide your hcu login credentials in order to download from the cloud")
    user = input("your hcu username: ")
    password = getpass.getpass(prompt='your hcu password: ')

    return user, password

# looks in the src folder on the cloud and downloads a the specified file
def download_data_from_cloud(src_file_name):
    # request to file
    url = f"https://cloud.hcu-hamburg.de/nextcloud/remote.php/dav/files/43AB43CD-FA95-42AF-8595-CB060146FBB3/{src_folder_cloud}/{src_file_name}"
    response = requests.get(url, auth=(cloud_user, cloud_pass))

    # if request successful
    if response.status_code == 200:
        with open(cwd + "/" + src_file_name, 'wb') as file:
            file.write(response.content)
    elif response.status_code == 401:
        print("could not login to cloud - or you do not have access to the file")
        print("response: ", response.status_code)
        exit()
    else:
        print("could not download data file ", src_file_name)
        print("response: ", response.status_code)
        exit()


# download and unzip the global data from the cloud
def get_global_data():
    print("getting global data")
    download_data_from_cloud("global.zip")
    unpack_zipfile("global.zip")
    os.remove("global.zip")


# download and unzip the user data from the cloud
def get_user_data():
    print("getting user data")
    download_data_from_cloud("user.zip")
    unpack_zipfile("user.zip", "data" + "/user" + "/" + getUserId(get_cityPyo_user_credentials()[0]))
    os.remove("user.zip")


# unpacks a local zipfile to a specified destination folder
def unpack_zipfile(file_name, destination_folder="data"):
    with zipfile.ZipFile(cwd + "/" + file_name, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)

    print("unzipped ", file_name)


def create_destination_folders():
    if not os.path.isdir(cwd + "/" + "data"):
        os.mkdir(cwd + "/" + "data")

    if not os.path.isdir(cwd + "/" + "data" + "/" + "user"):
        os.mkdir(cwd + "/" + "data" + "/" + "user")


if __name__ == "__main__":
    try:
        register_grasbrook_user()
    except:
        print("could not register user.")
        print("If you need to register a user - make sure CityPyo is running")

    print("\n \n Download data from HCU CLOUD")
    cloud_user, cloud_pass = get_user_credentials_for_hcu_cloud()
    create_destination_folders()
    get_global_data()
    get_user_data()




