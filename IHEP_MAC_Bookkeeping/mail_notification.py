import streamlit as st
def send_email_notification(group_name, subject, message, sender_email, sender_password):
    
    import pandas as pd
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Read the CSV file
    file_path = "user/mail_notification.csv"
    df = pd.read_csv(file_path)

    # Filter emails for the specified group
    recipient_emails = df[df["group"] == group_name]["email"].tolist()

    if not recipient_emails:
        print(f"No recipients found for group '{group_name}'. No email sent.")
        return

    # Set up the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipient_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP("cernmx.cern.ch", 25)  
        server.starttls()  # Secure the connection
        #server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()

        print(f"\u2705 Email sent successfully to {', '.join(recipient_emails)} for group '{group_name}'.")
        st.success(f"\u2705 An email notification sent successfully to group '{group_name}', including the following recipient(s): {', '.join(recipient_emails)}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
