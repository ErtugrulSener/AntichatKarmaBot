import json
import random
import sys
import threading
import time
from itertools import cycle

import requests
from faker import Faker


class safelist(list):
    def get(self, index, default=None):
        try:
            return self.__getitem__(index)
        except IndexError:
            return default


fake = Faker()
proxy_conf = safelist(sys.argv).get(3, None)
user_id = None
name = None


def create_fake_message():
    fake_messages = [f"I love you all <3",
                     f"Hahahahahaha",
                     f"Yeah that's nice, haha",
                     f"Selamün aleyküm",
                     f"Irgendwelche Leute da zum Schreiben?",
                     f"Hey Leute",
                     f"Bock auf ne Pfeife?",
                     f"Poky biatch",
                     f"biaaaaatch",
                     f"So dumb xD",
                     f"xDDDD",
                     f":D",
                     f"Who want's me?",
                     f"Blizzard's nice",
                     f"{fake.text()}"]

    return fake_messages


def getSessionToken():
    login_url = "https://mobile-elb.antich.at/login"
    login_params = {
        "username": username,
        "password": password,
        "_ApplicationId": application_id,
        "_ClientVersion": client_version,
        "_InstallationId": installation_id,
        "_method": method,
    }

    login_data = requests.post(login_url, login_params).json()

    global user_id
    user_id = login_data['objectId']

    global name
    name = login_data['profileName']

    return login_data['sessionToken']


def sendKarma():
    get_karma_url = "https://mobile-elb.antich.at/functions/getUserData"
    get_karma_params = {
        "userId": user_id,
        "_ApplicationId": application_id,
        "_ClientVersion": client_version,
        "_InstallationId": installation_id,
        "_SessionToken": session_token,
    }

    get_karma_data = requests.post(get_karma_url, get_karma_params).json()
    karma = get_karma_data['result']['karma']

    if karma >= 1000:
        purchase_gift_url = "https://mobile-elb.antich.at/functions/purchaseGift"
        purchase_gift_params = {
            "artifactName": "rose",
            "currency": "karma",
            # "dialogueId": "BaisDP0lME",
            "receiverId": "wPDPoFdPLh",
            "v": 10001,
            "_ApplicationId": application_id,
            "_ClientVersion": client_version,
            "_InstallationId": installation_id,
            "_SessionToken": session_token,
        }

        purchase_gift_data = requests.post(purchase_gift_url, purchase_gift_params)

        if purchase_gift_data.status_code != 400:
            print("Purchased gift and sent to minnie!")
        else:
            print(purchase_gift_data.json())


def get_proxies_from_file():
    with open("proxylist.txt", "r") as f:
        return set(f.read().splitlines())


proxies = get_proxies_from_file()
proxy_pool = cycle(proxies)
proxy = next(proxy_pool)

botname = "ErtuBot v1.0"

username = sys.argv[1]
password = sys.argv[2]
application_id = "fUEmHsDqbr9v73s4JBx0CwANjDJjoMcDFlrGqgY5"
client_version = "js1.11.1"
installation_id = "c9165079-def7-3b6e-18ee-aee875c2e818"
method = "GET"

# Step 1: Login in ans save sessionToken
session_token = getSessionToken()

# Step 2: Send a message using the sessionToken
send_message_url = "https://mobile-elb.antich.at/classes/Messages"

# Step 3: Get Top chats, to add the groups
groups = ["vDqRPhZLNi", "7eyQpyYtoB", "fecwhZEVXV"]

i = 0
timeout = 0
test_proxy = {}

sendKarma()

while True:
    for d in range(len(groups)):
        send_message_params = {
            "antiFlood": False,
            "dialogue": groups[d],
            "message": random.choice(create_fake_message()),
            "receiver": "group",
            "_ApplicationId": application_id,
            "_ClientVersion": client_version,
            "_InstallationId": installation_id,
            "_SessionToken": session_token,
        }

        headers = {'content-type': 'application/json'}

        if proxy_conf:
            done = False
            to_remove = []

            while not done:
                try:
                    login_data = requests.post(url=send_message_url, json=send_message_params, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=4)
                    done = True
                except:
                    to_remove.append(proxy)
                    proxy = next(proxy_pool)

            if len(to_remove) > 0:
                for pr in to_remove:
                    try:
                        proxies.remove(pr)
                        print(pr + " removed.")
                    except KeyError:
                        # removed by other instance already
                        pass

                    # with open("proxylist.txt", "r") as f:
                    #     with open("proxylist.txt", "w") as fw:
                    #         fw.writelines('\n'.join(proxies))

                proxy_pool = cycle(proxies)

        else:
            login_data = requests.post(url=send_message_url, json=send_message_params, headers=headers)

        if login_data.status_code == 201:
            print(f"{i} : {name}: Message sent succesfully. Sleeping for some seconds.")
            i += 1

            if i % 100 == 0:
                threading.Thread(target=sendKarma).start()
            elif i == 550:
                time.sleep(600)

        else:
            print(login_data.status_code, login_data.text)

            timeout += 1
            if timeout >= 9:
                sys.exit()
            elif timeout % 3 == 0:
                session_token = getSessionToken()

    time.sleep(14)
