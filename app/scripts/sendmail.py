import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Office 365 account details
sender_email = "systemalerts@acreafrica.com"
password = "Notifications@2022*"
receiver_email = "pkiruivits@gmail.com"

# Create the email
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "Test Email from Python (Office 365)"

# Email body
body = "Hello, this is a test email sent from Python using Office 365 SMTP!"
msg.attach(MIMEText(body, "plain"))

try:
    # Connect to Office 365 SMTP
    server = smtplib.SMTP("smtp.office365.com", 587)
    server.starttls()  # Upgrade to secure connection
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    print("✅ Email sent successfully")
except Exception as e:
    print("❌ Error:", e)
finally:
    server.quit()
# import smtplib

# try:
#     server = smtplib.SMTP("smtp.office365.com", 587)
#     server.starttls()
#     server.login("systemalerts@acreafrica.com", "Notifications@2022*")
#     print("✅ Login successful")
# except Exception as e:
#     print("❌ Error:", e)
# finally:
#     server.quit()