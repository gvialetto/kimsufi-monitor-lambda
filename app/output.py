from __future__ import print_function
from requests import post


def _server_message(server_id, config):
    return config['servers'].get(server_id, server_id)


def send_console(server_id, config):
    print(config['slack']['bot_message_tpl'].format(
        server=_server_message(server_id, config)))


def send_slack(server_id, config):
    payload = {
        "text": config['slack']['bot_message_tpl'].format(
            server=_server_message(server_id, config)),
        "username": config['slack']['bot_name']
    }
    post(config['slack']['bot_url'], json=payload)
