import os
import time
import random
import logging
import pandas as pd
import yagmail
import keyring
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slow_mailer.log'),
        logging.StreamHandler()
    ]
)

class SlowMailer:
    def __init__(self, email, password=None, test_mode=False):
        self.email = email
        self.test_mode = test_mode
        self.user_agent = UserAgent(
            software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value],
            operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.MAC.value],
            limit=100
        )
        
        if not password:
            password = keyring.get_password("slow_mailer", email)
        
        if not password:
            raise ValueError("Email password not found. Please set it using keyring.set_password('slow_mailer', email, password)")
        
        self.smtp = yagmail.SMTP(email, password)
        logging.info(f"Initialized SlowMailer for {email} (Test Mode: {test_mode})")

    def send_email(self, to_email, subject, html_content, text_content=None, template_vars=None):
        """Send a single email with human-like behavior."""
        if template_vars:
            html_content = html_content.format(**template_vars)
            if text_content:
                text_content = text_content.format(**template_vars)

        if self.test_mode:
            logging.info(f"[TEST MODE] Would send email to {to_email}")
            logging.info(f"Subject: {subject}")
            logging.info(f"Content: {html_content[:200]}...")
            return True

        try:
            # Add random user agent to headers
            headers = {
                'User-Agent': self.user_agent.get_random_user_agent()
            }
            
            self.smtp.send(
                to=to_email,
                subject=subject,
                contents=[text_content, html_content] if text_content else html_content,
                headers=headers
            )
            
            logging.info(f"Successfully sent email to {to_email}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            # Save failed recipient to CSV
            self._save_failed_recipient(to_email, template_vars)
            return False

    def _save_failed_recipient(self, email, template_vars):
        """Save failed recipient to a CSV file for later retry."""
        failed_file = "failed_emails.csv"
        try:
            # Create file with headers if it doesn't exist
            if not os.path.exists(failed_file):
                with open(failed_file, "w") as f:
                    f.write("email," + ",".join(template_vars.keys()) + "\n")
            
            # Append failed recipient
            with open(failed_file, "a") as f:
                f.write(email + "," + ",".join(str(v) for v in template_vars.values()) + "\n")
            logging.info(f"Saved failed recipient {email} to {failed_file}")
        except Exception as e:
            logging.error(f"Failed to save failed recipient to CSV: {str(e)}")

    def send_bulk_emails(self, csv_path, subject_template, html_template, text_template=None, start_index=0):
        """Send bulk emails with human-like delays."""
        df = pd.read_csv(csv_path)
        total = len(df)
        success_count = 0
        fail_count = 0

        logging.info(f"Starting bulk email send. Total recipients: {total}")

        for index, row in df.iloc[start_index:].iterrows():
            template_vars = row.to_dict()
            to_email = template_vars['email']
            
            success = self.send_email(
                to_email=to_email,
                subject=subject_template.format(**template_vars),
                html_content=html_template,
                text_content=text_template,
                template_vars=template_vars
            )

            if success:
                success_count += 1
            else:
                fail_count += 1

            # Human-like delays
            if index < total - 1:  # Don't delay after the last email
                # Random delay between 45-90 seconds
                delay = random.uniform(45, 90)
                
                # Occasionally take a longer break (10% chance)
                if random.random() < 0.1:
                    delay += random.uniform(120, 300)  # 2-5 minute break
                
                logging.info(f"Email {index + 1}/{total} - Waiting {delay:.1f} seconds before next email...")
                time.sleep(delay)

        logging.info(f"Bulk email send complete. Success: {success_count}, Failed: {fail_count}")
        return success_count, fail_count

    def close(self):
        """Close the SMTP connection."""
        if hasattr(self, 'smtp'):
            self.smtp.close()
            logging.info("SMTP connection closed")

def main():
    load_dotenv()
    
    # Get email credentials from environment variables
    email = os.getenv('EMAIL')
    password = os.getenv('EMAIL_PASSWORD')
    
    if not email:
        email = input("Enter your email address: ")
    
    if not password:
        password = input("Enter your email password: ")
        keyring.set_password("slow_mailer", email, password)
    
    # Initialize SlowMailer
    mailer = SlowMailer(email, password, test_mode=True)  # Start in test mode
    
    # Example usage
    csv_path = "students.csv"
    subject_template = "Hello {first_name}, Welcome to Our Program!"
    html_template = """
    <html>
        <body>
            <h1>Hello {first_name}!</h1>
            <p>Welcome to our program. We're excited to have you on board.</p>
            <p>Best regards,<br>The Team</p>
        </body>
    </html>
    """
    
    try:
        # Send emails
        mailer.send_bulk_emails(csv_path, subject_template, html_template)
    finally:
        # Ensure SMTP connection is closed
        mailer.close()

if __name__ == "__main__":
    main() 