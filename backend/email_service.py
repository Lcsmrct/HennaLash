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

# Global email service instance
email_service = EmailService()