import json
from app import KimsufiMonitor, send_console, send_slack


def handle_lambda(event, context):
    main(output_function=send_slack)


def main(output_function):
    with open('./config.json') as config_file:
        data = json.load(config_file)
    km = KimsufiMonitor(data, output_function)
    km.fetch_servers()
    km.send_messages()


if __name__ == '__main__':
    main(output_function=send_console)
