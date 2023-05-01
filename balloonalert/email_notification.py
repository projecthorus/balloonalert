import datetime
import logging
import time
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from .config import read_config

def send_email_notification(config, subject, message):
    """
    Attempt to send an email alert.
    """

    try:
        msg = "BalloonAlert Email Notification Message:\n"
        msg += "Timestamp: %s\n" % datetime.datetime.now().isoformat()
        msg += message
        msg += "\n"

        # Construct subject
        _subject = subject

        logging.debug("Subject: %s" % _subject)
        logging.debug("Message: %s" % msg)

        # Connect to the SMTP server.
        logging.debug("Server: " + config['email_smtp_server'])
        logging.debug("Port: " + config['email_smtp_port'])

        if config['email_smtp_authentication'] == "SSL":
            s = smtplib.SMTP_SSL(config['email_smtp_server'], config['email_smtp_port'])
        else:
            s = smtplib.SMTP(config['email_smtp_server'], config['email_smtp_port'])

        if config['email_smtp_authentication']  == "TLS":
            logging.debug("Initiating TLS..")
            s.ehlo()
            s.starttls()
            s.ehlo()

        if config['email_smtp_login'] != "None":
            logging.debug("Login: " + config['email_smtp_login'])
            s.login(config['email_smtp_login'], config['email_smtp_password'])

        # Send messages to all recepients.
        for _destination in config['email_to'].split(";"):

            logging.debug(f"Sending email to {_destination}")
            mime_msg = MIMEText(msg, "plain", "UTF-8")

            mime_msg["From"] = config['email_from']
            mime_msg["To"] = _destination
            mime_msg["Date"] = formatdate()
            mime_msg["Subject"] = _subject

            s.sendmail(mime_msg["From"], _destination, mime_msg.as_string())

            time.sleep(2)

        s.quit()

        logging.info("E-mail notification sent.")
    except Exception as e:
        logging.error("Error sending E-mail notification - %s" % str(e))







if __name__ == "__main__":
    import sys

    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s", level=logging.DEBUG
    )

    config = read_config(sys.argv[1])

    logging.debug(f"Read config: {config}")

    send_email_notification(config, "BalloonAlert - Test Email", "This is a test email from BalloonAlert.")

