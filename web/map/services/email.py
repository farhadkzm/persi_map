import smtplib


def send_email(email):
    sender = 'from@fromdomain.com'
    receivers = [email]
    smtp_server = 'localhost'
    message = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    Subject: SMTP e-mail test

    This is a test e-mail message.
    """

    try:
        smtpObj = smtplib.SMTP(smtp_server)
        smtpObj.sendmail(sender, receivers, message)
        print "Successfully sent email"
        return False
    except smtplib.SMTPException:
        print "Error: unable to send email"
        return True
