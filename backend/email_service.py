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
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nouvelle réservation</title>
        </head>
        <body style="margin: 0; padding: 0; background: linear-gradient(135deg, #fed7aa 0%, #fdba74 50%, #fb923c 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <div style="max-width: 650px; margin: 40px auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(251, 146, 60, 0.3); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 40px 30px; text-align: center; position: relative;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><defs><pattern id=\"grain\" patternUnits=\"userSpaceOnUse\" width=\"100\" height=\"100\"><circle cx=\"20\" cy=\"20\" r=\"1\" fill=\"%23ffffff\" fill-opacity=\"0.1\"/><circle cx=\"80\" cy=\"40\" r=\"1\" fill=\"%23ffffff\" fill-opacity=\"0.1\"/><circle cx=\"40\" cy=\"80\" r=\"1\" fill=\"%23ffffff\" fill-opacity=\"0.1\"/></pattern></defs><rect width=\"100\" height=\"100\" fill=\"url(%23grain)\"/></svg>') repeat; opacity: 0.1;"></div>
                    <div style="position: relative; z-index: 1;">
                        <h1 style="color: white; margin: 0 0 10px 0; font-size: 32px; font-weight: bold;">🎨 HennaLash</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 18px; font-weight: 500;">Nouvelle réservation</p>
                    </div>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #fed7aa 0%, #fb923c 100%); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                            <span style="font-size: 32px;">📅</span>
                        </div>
                        <h2 style="color: #1f2937; margin: 0 0 10px 0; font-size: 24px; font-weight: bold;">Nouvelle réservation reçue !</h2>
                        <p style="color: #6b7280; margin: 0; font-size: 16px;">Un client vient de faire une réservation</p>
                    </div>
                    
                    <!-- Client Info Card -->
                    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 16px; padding: 25px; margin: 25px 0; border-left: 5px solid #f97316; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <div style="display: grid; gap: 15px;">
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <span style="color: white; font-size: 16px;">👤</span>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Client</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{user_name}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <span style="color: white; font-size: 16px;">📧</span>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Email</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{user_email}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <span style="color: white; font-size: 16px;">🎨</span>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Service</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{service_name}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <span style="color: white; font-size: 16px;">📅</span>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Date</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{appointment_date}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                                    <span style="color: white; font-size: 16px;">🕐</span>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Heure</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{appointment_time}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Action Button -->
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%); border-radius: 12px; padding: 20px; border: 2px solid #f59e0b;">
                            <p style="margin: 0 0 15px 0; color: #92400e; font-weight: 600; font-size: 16px;">🚀 Action requise</p>
                            <p style="margin: 0; color: #78350f; font-size: 14px;">Connectez-vous à votre espace admin pour confirmer cette réservation et envoyer la confirmation au client.</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #6b7280; font-size: 14px; line-height: 1.6;">
                        <p style="margin: 20px 0 5px 0;">Cordialement,</p>
                        <p style="margin: 0; font-weight: 600; color: #f97316;">Système de réservation HennaLash</p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8fafc; padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0; color: #64748b; font-size: 12px; line-height: 1.5;">
                        Cet email a été envoyé automatiquement suite à une nouvelle réservation.<br>
                        <strong>HennaLash</strong> - Votre salon de henné et lashes de confiance
                    </p>
                </div>
            </div>
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
L'équipe HennaLash
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
                <p>Cordialement,<br><strong>L'équipe HennaLash</strong></p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666;">
                    <p>Cet email a été envoyé automatiquement suite à la confirmation de votre rendez-vous.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(client_email, subject, body, html_body)

    async def send_password_reset_email(self, email: str, code: str, first_name: str):
        """Send password reset code email."""
        subject = "Réinitialisation de votre mot de passe"
        
        body = f"""
Bonjour{' ' + first_name if first_name else ''},

Vous avez demandé la réinitialisation de votre mot de passe.

Votre code de réinitialisation est : {code}

Ce code est valable pendant 15 minutes uniquement.

Si vous n'avez pas fait cette demande, ignorez cet email.

Cordialement,
L'équipe HennaLash
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">HennaLash</h1>
                <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">Réinitialisation de mot de passe</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; border-left: 4px solid #f97316;">
                <p>Bonjour{' ' + first_name if first_name else ''},</p>
                
                <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
                
                <div style="background: white; border: 2px solid #f97316; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0 0 10px 0; font-weight: bold; color: #333;">Votre code de réinitialisation :</p>
                    <div style="font-size: 32px; font-weight: bold; color: #f97316; letter-spacing: 4px; font-family: monospace;">
                        {code}
                    </div>
                </div>
                
                <p style="color: #dc2626; font-weight: bold;">⏰ Ce code est valable pendant 15 minutes uniquement.</p>
                
                <p>Si vous n'avez pas fait cette demande, ignorez cet email en toute sécurité.</p>
                
                <p style="margin-top: 30px;">
                    Cordialement,<br>
                    <strong>L'équipe HennaLash</strong>
                </p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #6b7280;">
                    <p>Cet email a été envoyé automatiquement suite à votre demande de réinitialisation de mot de passe.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(email, subject, body, html_body)

# Global email service instance
email_service = EmailService()