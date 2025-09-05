import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.environ.get("GMAIL_USERNAME")
        self.password = os.environ.get("GMAIL_PASSWORD")
        self.enabled = bool(self.username and self.password)
        
        if not self.enabled:
            logger.warning("Gmail credentials not configured. Email notifications disabled.")
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None):
        """Send email via Gmail SMTP."""
        if not self.enabled:
            logger.info(f"Email would be sent to {to_email}: {subject}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_appointment_notification(self, admin_email: str, user_name: str, user_email: str, 
                                          service_name: str, appointment_date: str, appointment_time: str):
        """Send appointment notification to admin."""
        subject = f"Nouvelle réservation - {service_name}"
        
        body = f"""
Bonjour,

Une nouvelle réservation a été effectuée :

Client: {user_name}
Email: {user_email}
Service: {service_name}
Date: {appointment_date}
Heure: {appointment_time}

Veuillez vous connecter à votre espace admin pour confirmer cette réservation.

Cordialement,
Système de réservation
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Nouvelle réservation</h2>
            <p>Une nouvelle réservation a été effectuée :</p>
            <ul>
                <li><strong>Client:</strong> {user_name}</li>
                <li><strong>Email:</strong> {user_email}</li>
                <li><strong>Service:</strong> {service_name}</li>
                <li><strong>Date:</strong> {appointment_date}</li>
                <li><strong>Heure:</strong> {appointment_time}</li>
            </ul>
            <p>Veuillez vous connecter à votre espace admin pour confirmer cette réservation.</p>
            <p>Cordialement,<br>Système de réservation</p>
        </body>
        </html>
        """
        
        return await self.send_email(admin_email, subject, body, html_body)

    async def send_review_notification(self, admin_email: str, user_name: str, rating: int, comment: str):
        """Send review notification to admin."""
        subject = f"Nouvel avis client - {rating}/5 étoiles"
        
        body = f"""
Bonjour,

Un nouvel avis client a été soumis :

Client: {user_name}
Note: {rating}/5 étoiles
Commentaire: {comment}

Veuillez vous connecter à votre espace admin pour approuver ou rejeter cet avis.

Cordialement,
Système de réservation
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Nouvel avis client</h2>
            <p>Un nouvel avis client a été soumis :</p>
            <ul>
                <li><strong>Client:</strong> {user_name}</li>
                <li><strong>Note:</strong> {rating}/5 étoiles</li>
                <li><strong>Commentaire:</strong> {comment}</li>
            </ul>
            <p>Veuillez vous connecter à votre espace admin pour approuver ou rejeter cet avis.</p>
            <p>Cordialement,<br>Système de réservation</p>
        </body>
        </html>
        """
        
        return await self.send_email(admin_email, subject, body, html_body)

    async def send_appointment_confirmation_to_client(self, client_email: str, client_name: str, 
                                                    service_name: str, appointment_date: str, 
                                                    appointment_time: str, service_price: float):
        """Send appointment confirmation to client when admin confirms."""
        subject = f"Confirmation de votre rendez-vous - {service_name}"
        
        body = f"""
Bonjour {client_name},

Excellente nouvelle ! Votre rendez-vous a été confirmé :

Service: {service_name}
Date: {appointment_date}
Heure: {appointment_time}
Prix: {service_price}€

Nous avons hâte de vous accueillir !

En cas de besoin, n'hésitez pas à nous contacter.

Cordialement,
L'équipe Henné Artisanal
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #e67e22;">✅ Rendez-vous Confirmé !</h2>
                <p>Bonjour <strong>{client_name}</strong>,</p>
                <p>Excellente nouvelle ! Votre rendez-vous a été confirmé :</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 10px 0;"><strong>🎨 Service:</strong> {service_name}</li>
                        <li style="margin: 10px 0;"><strong>📅 Date:</strong> {appointment_date}</li>
                        <li style="margin: 10px 0;"><strong>🕐 Heure:</strong> {appointment_time}</li>
                        <li style="margin: 10px 0;"><strong>💰 Prix:</strong> {service_price}€</li>
                    </ul>
                </div>
                
                <p>Nous avons hâte de vous accueillir !</p>
                <p>En cas de besoin, n'hésitez pas à nous contacter.</p>
                <p>Cordialement,<br><strong>L'équipe Henné Artisanal</strong></p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666;">
                    <p>Cet email a été envoyé automatiquement suite à la confirmation de votre rendez-vous.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(client_email, subject, body, html_body)

# Global email service instance
email_service = EmailService()