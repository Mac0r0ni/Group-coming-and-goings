#!/usr/bin/env python3
# Credits: @Tomer8007 for the API, @StethoSaysHello for the ban/unban code(found on a github issue)
import logging
import os
import sys
import time
import pprint

from kik_unofficial import client
from kik_unofficial.callbacks import KikClientCallback
from kik_unofficial.client import KikClient
from kik_unofficial.datatypes.xmpp import chatting, roster
from kik_unofficial.datatypes.xmpp.chatting import IncomingStatusResponse, IncomingGroupStatus
from kik_unofficial.datatypes.xmpp.login import ConnectionFailedResponse
from kik_unofficial.datatypes.xmpp.roster import PeersInfoResponse, FetchRosterResponse

global kik_authenticated, online_status, my_jid

username = sys.argv[1] if len(sys.argv) > 1 else input('Username: ')
password = sys.argv[2] if len(sys.argv) > 2 else input('Password: ')

users = {}
focus = False


class InteractiveChatClient(KikClientCallback):
    def on_authenticated(self):
        print("Authentication Successful")  # Let's you know that the auth was a success
        # client.request_roster() # This will request the bots roster, to use this function, delete these comments

    def on_roster_received(self,
                           response: FetchRosterResponse):  # If you choose to request your roster, then this will print it to the console for you
        pp = pprint.PrettyPrinter(width=85, sort_dicts=True,
                                  compact=False)  # This is prettyprint. Makes text more readable.
        print("[+] Chat partners:\n" + '\n'.join([str(member) for member in response.peers]))  # This prints the roster

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("Connection Failed")  # If your connection failed

    def on_chat_message_received(self,
                                 chat_message: chatting.IncomingChatMessage):  # on_chat_message_received - what happens when your bot gets a DM
        print("[+ DIRECT MESSAGE] '{}' says: {}".format(chat_message.from_jid,
                                                        chat_message.body))  # This prints the info from the message received
        client.send_chat_message(chat_message.from_jid,
                                 # send_chat_message - This sends a message (to the user who DMd the bot)
                                 "You said \"" + chat_message.body + "\"!\nBut why are you messaging a bot?\n\n Please Join #RaidLiveStreams")  # This sends back (or "echos" back what the user said, plus an additional message)

    def on_status_message_received(self, response: IncomingStatusResponse):
        print(response.status)
        client.add_friend(response.from_jid)

    def on_group_status_received(self,
                                 response: IncomingGroupStatus):  # This will allow us to get status messages in the group, and respond accordingly.
        client.request_info_of_users(response.status_jid)  # this attempts to get the JID of the user
        if response.status.find("has joined") > 0:  # This shows users who have joined
            print(
                "--------------------------------------------------------\n[JOINED]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(response.group_jid)))
        if response.status.find("has left") > 0:  # This shows users who have lft
            print(
                "--------------------------------------------------------\n[LEFT]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(response.group_jid)))

        if response.status.find("removed") > 0:  # This shows users who have been removed
            print(
                "--------------------------------------------------------\n[REMOVED]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(
                        response.group_jid)))

        if response.status.find("banned") > 0:  # This shows users who have been banned
            print(
                "--------------------------------------------------------\n[BANNED]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(
                        response.group_jid)))

    def on_group_message_received(self,
                                  chat_message: chatting.IncomingGroupChatMessage):  # this reads and prints the messages that are sent in the group
        print(
            "--------------------------------------------------------\n[+ GROUP MESSAGE +]\n AJID '{}'\n From group: {} \n Says: {}\n--------------------------------------------------------".format(
                chat_message.from_jid,
                chat_message.group_jid,
                chat_message.body))
        message = str(
            chat_message.body.lower())  # This "scans" the messages in the group, which allow looking for particular words, and acts accordingly. To be used for admin triggers.
        if message.startswith("ban"):  # This is the start of the ban command
            user = str(message.replace("ban ", ""))
            client.send_chat_message(chat_message.group_jid,
                                     "Attempting to ban \"" + user + "\" from the group...")  # This sends a message to the group stating the bot is attempting the ban
            try:
                def get_jid(user):  # this gets the JID of the user
                    try:
                        grab_jid = client.get_jid(user)
                        return grab_jid
                    except:
                        return False

                jid = get_jid(user)
                attempts = 1
                while not jid:
                    if attempts > 5:
                        client.send_chat_message(chat_message.group_jid,
                                                 "")  # This lets you know it was unable to get the JID
                        jid = ""
                    else:
                        jid = get_jid(user)
                        attempts = attempts + 1
                client.ban_member_from_group(chat_message.group_jid, jid)  # This bans the member from the group
                if jid:
                    client.send_chat_message(chat_message.group_jid,
                                             "!")  # Bot send message to the group stating the ban is complete
            except:
                client.send_chat_message(chat_message.group_jid, "")  # Ban attempt failed messages
        elif message.startswith("unban"):  # This is the start of the unban command, same as above.....but reverse.
            user = str(message.replace("unban ", ""))
            client.send_chat_message(chat_message.group_jid,
                                     "")
            try:
                def get_jid(user):
                    try:
                        grab_jid = client.get_jid(user)
                        return grab_jid
                    except:
                        return False

                jid = get_jid(user)
                attempts = 1
                while not jid:
                    if attempts > 5:
                        client.send_chat_message(chat_message.group_jid,
                                                 "")
                        jid = ""
                    else:
                        jid = get_jid(user)
                        attempts = attempts + 1
                client.unban_member_from_group(chat_message.group_jid, jid)
                if jid:  # Checks if there is a JID
                    client.send_chat_message(chat_message.group_jid, "")
            except:
                client.send_chat_message(chat_message.group_jid, "")

        elif message.startswith(
                "add"):  # This is the start of the add command. will attempt to add user to the group. the person you are trying to add must be in your chat list to be directly added. If the user is not in your chat list, then they will be sent an invite.
            user = str(message.replace("add ", ""))
            client.send_chat_message(chat_message.group_jid,
                                     "")
            try:
                def get_jid(user):
                    try:
                        grab_jid = client.get_jid(user)
                        return grab_jid
                    except:
                        return False

                jid = get_jid(user)
                attempts = 1
                while not jid:
                    if attempts > 5:
                        client.send_chat_message(chat_message.group_jid,
                                                 "")
                        jid = ""
                    else:
                        jid = get_jid(user)
                        attempts = attempts + 1
                client.add_peer_to_group(chat_message.group_jid, jid)
                if jid:  # Checks if there is a JID
                    client.send_chat_message(chat_message.group_jid, "")
            except:
                print("add attempt failed!")

        elif message.startswith("remove"):  # This is the start of the remove command
            user = str(message.replace("remove ", ""))
            client.send_chat_message(chat_message.group_jid,
                                     "")
            try:
                def get_jid(user):
                    try:
                        grab_jid = client.get_jid(user)
                        return grab_jid
                    except:
                        return False

                jid = get_jid(user)
                attempts = 1
                while not jid:
                    if attempts > 5:
                        client.send_chat_message(chat_message.group_jid,
                                                 "")
                        jid = ""
                    else:
                        jid = get_jid(user)
                        attempts = attempts + 1
                client.remove_peer_from_group(chat_message.group_jid, jid)
                if jid:  # Checks if there is a JID
                    client.send_chat_message(chat_message.group_jid, "")
            except:
                print("remove failed!")

        elif message.startswith("bing"):
            client.send_chat_message(chat_message.group_jid, "bong")

    def on_peer_info_received(self, response: PeersInfoResponse):
        users[response.users[0].jid] = response.users[0]


def query_user(jid):
    if jid in users:
        return users[jid]
    else:
        client.request_info_of_users(jid)
        while jid not in users:
            pass
        return users[jid]


def jid_to_group_display_name(jid):
    return query_user(jid).display_name


def get_group_jid_number(jid):
    return jid.split('@')[0][0:-2]


if __name__ == '__main__':
    # set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stream_handler = logging.FileHandler(os.path.dirname(__file__) + '/' + str(int(time.time() * 1000.0)) + '.log')
    stream_handler.setFormatter(logging.Formatter(KikClient.log_format()))
    logger.addHandler(stream_handler)

    # create the client
    callback = InteractiveChatClient()
    client = KikClient(callback=callback, kik_username=username, kik_password=password)

while True: pass
