
import smtplib
from string import Template
from email.message import EmailMessage


def send_welcome_mail(address: str, template_filename: str, template_values, smtp_server: str = 'localhost'):
    """Email a welcome email to the user."""
    msg = EmailMessage()

    with open(template_filename) as fobj:
        email_content = Template(fobj.read())
    msg.set_content(email_content.safe_substitute(**template_values))

    msg['From'] = template_values.get('mail_from', 'root')
    msg['To'] = address
    msg['Subject'] = template_values.get('mail_subject', 'Welcome!')

    smtp_conn = smtplib.SMTP(smtp_server)
    smtp_conn.send_message(msg)
    smtp_conn.quit()
