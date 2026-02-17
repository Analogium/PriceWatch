import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

import requests

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.email_templates import (
    password_reset_template,
    price_alert_template,
    verification_email_template,
    weekly_summary_template,
)

logger = get_logger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.frontend_url = settings.FRONTEND_URL

    def send_price_alert(
        self,
        to_email: str,
        product_name: str,
        new_price: float,
        old_price: float,
        product_url: str,
        user_preferences=None,
        lang: str = "fr",
    ):
        """Send a price alert email to the user.

        Args:
            to_email: User's email address
            product_name: Name of the product
            new_price: New price of the product
            old_price: Previous price of the product
            product_url: URL of the product
            user_preferences: UserPreferences object (optional)
            lang: Language code ("fr" or "en")
        """
        # Check if user has email notifications enabled
        if user_preferences:
            if not user_preferences.email_notifications:
                logger.info(f"Email notifications disabled for {to_email}, skipping price alert")
                return
            if not user_preferences.price_drop_alerts:
                logger.info(f"Price drop alerts disabled for {to_email}, skipping")
                return
            # Use user's language preference if available
            if hasattr(user_preferences, "language") and user_preferences.language:
                lang = user_preferences.language

        preferences_url = f"{self.frontend_url}/settings/notifications"

        subject, html_content = price_alert_template(
            lang=lang,
            product_name=product_name,
            new_price=new_price,
            old_price=old_price,
            product_url=product_url,
            preferences_url=preferences_url,
        )

        self._send_email(to_email, subject, html_content)

        # Send webhook notification if enabled
        if user_preferences and user_preferences.webhook_notifications and user_preferences.webhook_url:
            self._send_webhook_notification(
                webhook_url=user_preferences.webhook_url,
                webhook_type=user_preferences.webhook_type,
                product_name=product_name,
                new_price=new_price,
                old_price=old_price,
                product_url=product_url,
            )

    def send_verification_email(self, to_email: str, token: str, lang: str = "fr"):
        """Send email verification link."""
        verification_url = f"{self.frontend_url}/verify-email?token={token}"

        subject, html_content = verification_email_template(lang=lang, verification_url=verification_url)

        self._send_email(to_email, subject, html_content)

    def send_password_reset_email(self, to_email: str, token: str, lang: str = "fr"):
        """Send password reset link."""
        reset_url = f"{self.frontend_url}/reset-password?token={token}"

        subject, html_content = password_reset_template(lang=lang, reset_url=reset_url)

        self._send_email(to_email, subject, html_content)

    def send_weekly_summary(
        self,
        to_email: str,
        products_summary: list,
        total_products: int,
        total_savings: float,
        user_preferences=None,
        lang: str = "fr",
    ):
        """Send a weekly summary email with price tracking highlights.

        Args:
            to_email: User's email address
            products_summary: List of dicts with product info (name, current_price, lowest_price, highest_price, url)
            total_products: Total number of tracked products
            total_savings: Total potential savings if all products reached target price
            user_preferences: UserPreferences object (optional)
            lang: Language code ("fr" or "en")
        """
        # Check if user has email notifications and weekly summary enabled
        if user_preferences:
            if not user_preferences.email_notifications:
                logger.info(f"Email notifications disabled for {to_email}, skipping weekly summary")
                return
            if not user_preferences.weekly_summary:
                logger.info(f"Weekly summary disabled for {to_email}, skipping")
                return
            # Use user's language preference if available
            if hasattr(user_preferences, "language") and user_preferences.language:
                lang = user_preferences.language

        # Build products table HTML
        products_html = ""
        for product in products_summary[:10]:  # Limit to 10 products
            price_change = product.get("price_change", 0)
            price_change_class = (
                "color: #4CAF50;" if price_change < 0 else "color: #F44336;" if price_change > 0 else ""
            )
            price_change_symbol = "↓" if price_change < 0 else "↑" if price_change > 0 else "→"
            stable_text = "Stable" if lang == "en" else "Stable"
            price_change_text = f"{price_change_symbol} {abs(price_change):.2f} €" if price_change != 0 else stable_text

            products_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;">
                    <a href="{product['url']}" style="color: #333; text-decoration: none;">{product['name'][:50]}{'...' if len(product['name']) > 50 else ''}</a>
                </td>
                <td style="padding: 10px; text-align: right;">{product['current_price']:.2f} €</td>
                <td style="padding: 10px; text-align: right; {price_change_class}">{price_change_text}</td>
                <td style="padding: 10px; text-align: right; color: #4CAF50;">{product.get('lowest_price', product['current_price']):.2f} €</td>
            </tr>
            """

        preferences_url = f"{self.frontend_url}/settings/notifications"
        dashboard_url = f"{self.frontend_url}/dashboard"

        subject, html_content = weekly_summary_template(
            lang=lang,
            products_html=products_html,
            total_products=total_products,
            total_savings=total_savings,
            dashboard_url=dashboard_url,
            preferences_url=preferences_url,
        )

        self._send_email(to_email, subject, html_content)
        logger.info(f"Weekly summary sent successfully to {to_email}")

    def _send_email(self, to_email: str, subject: str, html_content: str):
        """Internal method to send email via SMTP."""
        try:
            logger.info(f"Sending email to {to_email}: {subject}")

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

            logger.info(f"Email sent successfully to {to_email}")

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}", exc_info=True)
            raise

    def _send_webhook_notification(
        self,
        webhook_url: str,
        webhook_type: str,
        product_name: str,
        new_price: float,
        old_price: float,
        product_url: str,
    ):
        """Send webhook notification for price drop.

        Args:
            webhook_url: The webhook URL to send to
            webhook_type: Type of webhook (slack, discord, custom)
            product_name: Name of the product
            new_price: New price of the product
            old_price: Previous price of the product
            product_url: URL of the product
        """
        try:
            logger.info(f"Sending webhook notification to {webhook_url} (type: {webhook_type})")

            # Prepare payload based on webhook type
            payload: Dict[str, Any]
            if webhook_type == "slack":
                payload = {
                    "text": "🔔 Price Drop Alert!",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": f"*{product_name}* vient de baisser de prix !"},
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": f"*Nouveau prix:*\n€{new_price:.2f}"},
                                {"type": "mrkdwn", "text": f"*Ancien prix:*\n~€{old_price:.2f}~"},
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Économie:*\n€{(old_price - new_price):.2f} ({((old_price - new_price) / old_price * 100):.1f}%)",
                                },
                            ],
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "Voir le produit"},
                                    "url": product_url,
                                }
                            ],
                        },
                    ],
                }
            elif webhook_type == "discord":
                payload = {
                    "content": "🔔 **Price Drop Alert!**",
                    "embeds": [
                        {
                            "title": product_name,
                            "url": product_url,
                            "color": 5025616,  # Green color
                            "fields": [
                                {"name": "Nouveau prix", "value": f"€{new_price:.2f}", "inline": True},
                                {"name": "Ancien prix", "value": f"~~€{old_price:.2f}~~", "inline": True},
                                {
                                    "name": "Économie",
                                    "value": f"€{(old_price - new_price):.2f} ({((old_price - new_price) / old_price * 100):.1f}%)",
                                    "inline": True,
                                },
                            ],
                        }
                    ],
                }
            else:
                # Custom webhook - generic JSON payload
                payload = {
                    "event": "price_drop",
                    "product_name": product_name,
                    "new_price": new_price,
                    "old_price": old_price,
                    "savings": old_price - new_price,
                    "savings_percent": ((old_price - new_price) / old_price * 100),
                    "product_url": product_url,
                }

            response = requests.post(
                webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=10
            )

            if response.status_code in [200, 201, 204]:
                logger.info(f"Webhook notification sent successfully to {webhook_url}")
            else:
                logger.warning(f"Webhook notification returned status {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending webhook notification to {webhook_url}: {str(e)}", exc_info=True)
            # Don't raise - webhook failures shouldn't prevent email sending
        except Exception as e:
            logger.error(f"Unexpected error sending webhook notification: {str(e)}", exc_info=True)


email_service = EmailService()
