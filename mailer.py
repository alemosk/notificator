import configparser
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = configparser.ConfigParser()
config.read('settings.ini')


def make_message(receiver_email):
    message = MIMEMultipart("alternative")
    message["Subject"] = config['MAIL']['subject']
    message["From"] = config['MAIL']['from']
    message["To"] = receiver_email

    with open(config['MAIL']['plain_mail_template']) as f:
        text = f.read()

    with open(config['MAIL']['html_mail_template']) as f:
        html = f.read()

    print('Reading text email body...')
    part1 = MIMEText(text, "plain")
    print('Reading html email body...')
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    return message


def send_mail(receiver_email):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
            config['CONNECTION']['smtp_server'],
            config['CONNECTION']['smtp_port'], context=context
    ) as server:
        server.login(config['CONNECTION']['email'], config['CONNECTION']['password'])
        message = make_message(receiver_email)
        server.sendmail(
            config['CONNECTION']['email'], receiver_email, message.as_string()
        )


def load_mail_list():
    with open(config['PROCESSING']['mail_list_file']) as f:
        result = f.readlines()

    result = [x.strip() for x in result]

    return result


def load_processed_list():
    try:
        with open(config['PROCESSING']['processed_list_file']) as f:
            result = f.readlines()
        result = [x.strip() for x in result]
    except FileNotFoundError:
        result = []

    return result


def update_processed_list(processed):
    with open(config['PROCESSING']['processed_list_file'], 'w') as f:
        f.writelines(processed)


def main():
    receivers = load_mail_list()
    processed = load_processed_list()

    for receiver_email in receivers:
        print(f'Sending email to {receiver_email}...', end=' ')
        if len(receiver_email) > 0 and receiver_email not in processed:
            send_mail(receiver_email)
            processed.append(receiver_email)
            update_processed_list(processed)
            print('OK')

            time.sleep(int(config['PROCESSING']['send_delay_sec']))
        else:
            print('SKIPPED')


if __name__ == '__main__':
    main()
