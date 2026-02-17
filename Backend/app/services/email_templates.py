"""Bilingual email templates (FR/EN) for PriceWatch."""


def price_alert_template(
    lang: str,
    product_name: str,
    new_price: float,
    old_price: float,
    product_url: str,
    preferences_url: str,
) -> tuple[str, str]:
    """Returns (subject, html_body) for price alert email."""
    savings = old_price - new_price
    savings_percent = (savings / old_price * 100) if old_price > 0 else 0

    if lang == "en":
        subject = f"🔔 Price drop detected on {product_name}"
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4CAF50;">Great news! 🎉</h2>
                <p>Hello,</p>
                <p>The product <strong>{product_name}</strong> just dropped in price!</p>
                <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>New price:</strong> <span style="color: #4CAF50; font-size: 1.2em;">{new_price:.2f} €</span></p>
                    <p style="margin: 5px 0;"><strong>Old price:</strong> <span style="text-decoration: line-through; color: #999;">{old_price:.2f} €</span></p>
                    <p style="margin: 5px 0;"><strong>Savings:</strong> <span style="color: #FF5722;">{savings:.2f} € ({savings_percent:.1f}%)</span></p>
                </div>
                <p>
                    <a href="{product_url}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">
                        👉 View product
                    </a>
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    You are receiving this email because you are tracking this product on PriceWatch.<br>
                    <em>PriceWatch: watch prices, not your tabs.</em>
                </p>
                <p style="font-size: 0.8em; color: #999; margin-top: 20px;">
                    <a href="{preferences_url}" style="color: #999;">Manage my notification preferences</a> |
                    To stop receiving these alerts, disable notifications in your settings.
                </p>
            </body>
        </html>
        """.format(
            product_name=product_name,
            new_price=new_price,
            old_price=old_price,
            product_url=product_url,
            savings=savings,
            savings_percent=savings_percent,
            preferences_url=preferences_url,
        )
    else:
        subject = f"🔔 Baisse de prix détectée sur {product_name}"
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4CAF50;">Bonne nouvelle ! 🎉</h2>
                <p>Bonjour,</p>
                <p>Le produit <strong>{product_name}</strong> vient de baisser de prix !</p>
                <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Nouveau prix :</strong> <span style="color: #4CAF50; font-size: 1.2em;">{new_price:.2f} €</span></p>
                    <p style="margin: 5px 0;"><strong>Ancien prix :</strong> <span style="text-decoration: line-through; color: #999;">{old_price:.2f} €</span></p>
                    <p style="margin: 5px 0;"><strong>Économie :</strong> <span style="color: #FF5722;">{savings:.2f} € ({savings_percent:.1f}%)</span></p>
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
                <p style="font-size: 0.8em; color: #999; margin-top: 20px;">
                    <a href="{preferences_url}" style="color: #999;">Gérer mes préférences de notifications</a> |
                    Pour ne plus recevoir ces alertes, désactivez les notifications dans vos paramètres.
                </p>
            </body>
        </html>
        """.format(
            product_name=product_name,
            new_price=new_price,
            old_price=old_price,
            product_url=product_url,
            savings=savings,
            savings_percent=savings_percent,
            preferences_url=preferences_url,
        )

    return subject, html_content


def verification_email_template(lang: str, verification_url: str) -> tuple[str, str]:
    """Returns (subject, html_body) for email verification."""
    if lang == "en":
        subject = "Verify your email - PriceWatch"
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4CAF50;">Welcome to PriceWatch! 👋</h2>
                <p>Hello,</p>
                <p>Thank you for signing up for PriceWatch. To activate your account, please click the button below:</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Verify my email
                    </a>
                </p>
                <p>Or copy this link into your browser:</p>
                <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 0.9em;">
                    {verification_url}
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    If you did not create a PriceWatch account, you can ignore this email.
                </p>
            </body>
        </html>
        """.format(
            verification_url=verification_url
        )
    else:
        subject = "Vérifiez votre email - PriceWatch"
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4CAF50;">Bienvenue sur PriceWatch ! 👋</h2>
                <p>Bonjour,</p>
                <p>Merci de vous être inscrit sur PriceWatch. Pour activer votre compte, veuillez cliquer sur le bouton ci-dessous :</p>
                <p style="margin: 30px 0;">
                    <a href="{verification_url}" style="display: inline-block; padding: 12px 30px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Vérifier mon email
                    </a>
                </p>
                <p>Ou copiez ce lien dans votre navigateur :</p>
                <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 0.9em;">
                    {verification_url}
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    Si vous n'avez pas créé de compte PriceWatch, vous pouvez ignorer cet email.
                </p>
            </body>
        </html>
        """.format(
            verification_url=verification_url
        )

    return subject, html_content


def password_reset_template(lang: str, reset_url: str) -> tuple[str, str]:
    """Returns (subject, html_body) for password reset email."""
    if lang == "en":
        subject = "Password reset - PriceWatch"
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #FF5722;">Password Reset</h2>
                <p>Hello,</p>
                <p>You have requested a password reset. Click the button below to create a new password:</p>
                <p style="margin: 30px 0;">
                    <a href="{reset_url}" style="display: inline-block; padding: 12px 30px; background-color: #FF5722; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Reset my password
                    </a>
                </p>
                <p>Or copy this link into your browser:</p>
                <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 0.9em;">
                    {reset_url}
                </p>
                <p style="color: #FF5722; font-weight: bold;">⚠️ This link expires in 1 hour.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    If you did not request this reset, you can ignore this email.<br>
                    Your password will remain unchanged.
                </p>
            </body>
        </html>
        """.format(
            reset_url=reset_url
        )
    else:
        subject = "Réinitialisation de mot de passe - PriceWatch"
        html_content = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #FF5722;">Réinitialisation de mot de passe</h2>
                <p>Bonjour,</p>
                <p>Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                <p style="margin: 30px 0;">
                    <a href="{reset_url}" style="display: inline-block; padding: 12px 30px; background-color: #FF5722; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Réinitialiser mon mot de passe
                    </a>
                </p>
                <p>Ou copiez ce lien dans votre navigateur :</p>
                <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 0.9em;">
                    {reset_url}
                </p>
                <p style="color: #FF5722; font-weight: bold;">⚠️ Ce lien expire dans 1 heure.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.<br>
                    Votre mot de passe restera inchangé.
                </p>
            </body>
        </html>
        """.format(
            reset_url=reset_url
        )

    return subject, html_content


def weekly_summary_template(
    lang: str,
    products_html: str,
    total_products: int,
    total_savings: float,
    dashboard_url: str,
    preferences_url: str,
) -> tuple[str, str]:
    """Returns (subject, html_body) for weekly summary email."""
    if lang == "en":
        subject = "📊 Your PriceWatch weekly summary"
        empty_text = "No tracked products at the moment"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #2196F3;">📊 Your weekly summary</h2>
                <p>Hello,</p>
                <p>Here is an overview of your tracked products this week:</p>

                <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Tracked products:</strong> {total_products}</p>
                    <p style="margin: 5px 0;"><strong>Potential savings:</strong> <span style="color: #4CAF50;">{total_savings:.2f} €</span></p>
                </div>

                <h3 style="color: #333;">Price changes</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f4f4f4;">
                            <th style="padding: 10px; text-align: left;">Product</th>
                            <th style="padding: 10px; text-align: right;">Current price</th>
                            <th style="padding: 10px; text-align: right;">Change</th>
                            <th style="padding: 10px; text-align: right;">Lowest price</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products_html if products_html else f'<tr><td colspan="4" style="padding: 20px; text-align: center; color: #777;">{empty_text}</td></tr>'}
                    </tbody>
                </table>

                <p>
                    <a href="{dashboard_url}" style="display: inline-block; padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px;">
                        📈 View my dashboard
                    </a>
                </p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    <em>PriceWatch: watch prices, not your tabs.</em>
                </p>
                <p style="font-size: 0.8em; color: #999; margin-top: 20px;">
                    <a href="{preferences_url}" style="color: #999;">Manage my notification preferences</a> |
                    To stop receiving this summary, disable the weekly summary in your settings.
                </p>
            </body>
        </html>
        """
    else:
        subject = "📊 Votre résumé hebdomadaire PriceWatch"
        empty_text = "Aucun produit surveillé pour le moment"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #2196F3;">📊 Votre résumé hebdomadaire</h2>
                <p>Bonjour,</p>
                <p>Voici un aperçu de vos produits surveillés cette semaine :</p>

                <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Produits surveillés :</strong> {total_products}</p>
                    <p style="margin: 5px 0;"><strong>Économies potentielles :</strong> <span style="color: #4CAF50;">{total_savings:.2f} €</span></p>
                </div>

                <h3 style="color: #333;">Évolution des prix</h3>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #f4f4f4;">
                            <th style="padding: 10px; text-align: left;">Produit</th>
                            <th style="padding: 10px; text-align: right;">Prix actuel</th>
                            <th style="padding: 10px; text-align: right;">Variation</th>
                            <th style="padding: 10px; text-align: right;">Prix le plus bas</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products_html if products_html else f'<tr><td colspan="4" style="padding: 20px; text-align: center; color: #777;">{empty_text}</td></tr>'}
                    </tbody>
                </table>

                <p>
                    <a href="{dashboard_url}" style="display: inline-block; padding: 10px 20px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px;">
                        📈 Voir mon tableau de bord
                    </a>
                </p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.9em; color: #777;">
                    <em>PriceWatch : surveillez les prix, pas vos onglets.</em>
                </p>
                <p style="font-size: 0.8em; color: #999; margin-top: 20px;">
                    <a href="{preferences_url}" style="color: #999;">Gérer mes préférences de notifications</a> |
                    Pour ne plus recevoir ce résumé, désactivez le résumé hebdomadaire dans vos paramètres.
                </p>
            </body>
        </html>
        """

    return subject, html_content
