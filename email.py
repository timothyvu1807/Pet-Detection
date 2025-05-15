import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, message):
    # Set up the sender's email credentials
    sender_email = "" #add sender email
    sender_token = "" #add sender token

    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the message to the email
    msg.attach(MIMEText(message, 'plain'))

    # Set up the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Start the server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    # Log in to the email account
    server.login(sender_email, sender_token)

    # Send the email
    server.sendmail(sender_email, to_email, msg.as_string())

    # Quit the server
    server.quit()

if __name__ == "__main__":
    # Replace these values with your friend's email, subject, and message
    friend_email = "danielknguyen@live.com"
    email_subject = "Valorant Time"
    email_message = "Hop on bitch"

    # Send the email
    send_email(friend_email, email_subject, email_message)

    #print("Email has been sent")
