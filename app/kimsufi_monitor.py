from transitions import Machine
import requests


class KimsufiMonitor(object):
    API_URL = \
        "https://ws.ovh.com/dedicated/r2/ws.dispatcher/getAvailability2"
    UNAVAILABLE_STATES = [
        "unknown",
        "unavailable"
    ]

    states = [
        "disconnected",
        "with_servers",
        "without_servers"
    ]

    transitions = [
        {
            "trigger": "fetch_servers",
            "source": "disconnected",
            "dest": "with_servers",
            "prepare": [
                "do_fetch_servers"
            ],
            "unless": [
                "has_failed",
                "has_no_servers"
            ]
        },
        {
            "trigger": "fetch_servers",
            "source": "disconnected",
            "dest": "failed",
            "conditions": [
                "has_failed"
            ]
        },
        {
            "trigger": "fetch_servers",
            "source": "disconnected",
            "dest": "without_servers",
            "conditions": [
                "has_no_servers"
            ]
        },
        {
            "trigger": "send_messages",
            "source": "*",
            "dest": "disconnected",
            "before": [
                "do_send_messages"
            ],
            "unless": [
                "has_failed"
            ]
        }
    ]

    def __init__(self, config, output_function):
        self.__output = output_function
        self.__failed = False
        self.__available_servers = []
        self.__cfg = config
        self.__machine = Machine(
            model=self,
            states=KimsufiMonitor.states,
            transitions=KimsufiMonitor.transitions,
            initial="disconnected",
            auto_transitions=False)

    def has_failed(self, *args, **kwargs):
        return self.__failed

    def has_no_servers(self, *args, **kwargs):
        return len(self.__available_servers) == 0

    def __get_available(self, availability_data, servertypes):
        for availability_info in availability_data['answer']['availability']:
            if availability_info['reference'] not in servertypes:
                continue

            available = any([
                zone['availability'].lower() not in self.UNAVAILABLE_STATES
                for zone in availability_info['zones']
            ])
            if available:
                yield availability_info['reference']

    def do_fetch_servers(self):
        try:
            r = requests.get(self.API_URL)
            r.raise_for_status()
            kimsufi_servers = self.__cfg['servers'].keys()
            self.__available_servers = list(
                self.__get_available(r.json(), kimsufi_servers)
            )
        except (ValueError, KeyError, requests.exceptions.HTTPError):
            self.__failed = True

    def do_send_messages(self):
        for server in self.__available_servers:
            self.__output(server_id=server, config=self.__cfg)
