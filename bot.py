#!/usr/bin/env python3

import logging
import os
import sys
import time
from kik_unofficial.callbacks import KikClientCallback
from kik_unofficial.client import KikClient
from kik_unofficial.datatypes.xmpp.chatting import IncomingStatusResponse, IncomingGroupStatus
from kik_unofficial.datatypes.xmpp.login import ConnectionFailedResponse
from kik_unofficial.datatypes.xmpp.roster import PeersInfoResponse

username = sys.argv[1] if len(sys.argv) > 1 else input('Username: ')
password = sys.argv[2] if len(sys.argv) > 2 else input('Password: ')

users = {}
focus = False


class InteractiveChatClient(KikClientCallback):
    def on_authenticated(self):
        print("I'm authenticated! You can now use the bot")

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("Connection failed")

    def on_status_message_received(self, response: IncomingStatusResponse):
        print(response.status)
        client.add_friend(response.from_jid)

    def on_group_status_received(self, response: IncomingGroupStatus):
        client.request_info_of_users(response.status_jid)
        if response.status.find("has joined") > 0:
            print(
                "--------------------------------------------------------\n[JOINED]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(response.group_jid)))
        if response.status.find("has left") > 0:
            print(
                "--------------------------------------------------------\n[LEFT]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(response.group_jid)))

        if response.status.find("removed") > 0:
            print(
                "--------------------------------------------------------\n[REMOVED]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(
                        response.group_jid)))

        if response.status.find("banned") > 0:
            print(
                "--------------------------------------------------------\n[BANNED]\nAJID:{}\nDisplay Name: {}\nGroup JID: {}_g@groups.kik.com\n--------------------------------------------------------".format(
                    response.status_jid,
                    jid_to_group_display_name(
                        response.status_jid),
                    get_group_jid_number(
                        response.group_jid)))

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
