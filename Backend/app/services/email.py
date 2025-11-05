import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM

    def send_price_alert(self, to_email: str, product_name: str, new_price: float, old_price: float, product_url: str):
        """Send a price alert email to the user."""
        subject = f"🔔 Baisse de prix détectée sur {product_name}"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4CAF50;">Bonne nouvelle ! 🎉</h2>
                <p>Bonjour,</p>
                <p>Le produit <strong>{product_name}</strong> vient de baisser de prix !</p>
                <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Nouveau prix :</strong> <span style="color: #4CAF50; font-size: 1.2em;">{new_price:.2f} €</span></p>
                    <p style="margin: 5px 0;"><strong>Ancien prix :</strong> <span style="text-decoration: line-through; color: #999;">{old_price:.2f} €</span></p>
                    <p style="margin: 5px 0;"><strong>Économie :</strong> <span style="color: #FF5722;">{(old_price - new_price):.2f} € ({((old_price - new_price) / old_price * 100):.1f}%)</span></p>
                </div>
                <p>
                    <a href="{product_url}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
                        👉 Voir le produit
                    </a>
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    Vous recevez cet email car vous surveillez ce produit sur PriceWatch.<br>
                    <em>PriceWatch : surveillez les prix, pas vos onglets.</em>
                </p>
            </body>
        </html>
        """

        self._send_email(to_email, subject, html_content)

    def _send_email(self, to_email: str, subject: str, html_content: str):
        """Internal method to send email via SMTP."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)

            print(f"Email sent successfully to {to_email}")

        except Exception as e:
            print(f"Error sending email to {to_email}: {str(e)}")
            raise


email_service = EmailService()
