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
            <style>
                @media only screen and (max-width: 600px) {{
                    .container {{ width: 100% !important; margin: 0 !important; }}
                    .content {{ padding: 16px !important; }}
                    .header {{ padding: 24px 16px !important; }}
                    .card {{ padding: 16px !important; margin: 16px 0 !important; }}
                    .title {{ font-size: 24px !important; }}
                    .subtitle {{ font-size: 20px !important; }}
                    .info-row {{ flex-direction: column !important; text-align: center !important; }}
                    .info-icon {{ margin: 0 auto 8px auto !important; }}
                }}
            </style>
        </head>
        <body style="margin: 0; padding: 20px; background-color: #fef7ed; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div class="container" style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <!-- Header -->
                <div class="header" style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 32px 24px; text-align: center;">
                    <div style="width: 64px; height: 64px; background-color: rgba(255, 255, 255, 0.15); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19ZM7 10H9V12H7V10ZM11 10H13V12H11V10ZM15 10H17V12H15V10Z" fill="white"/>
                        </svg>
                    </div>
                    <h1 class="title" style="color: white; margin: 0 0 8px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">HennaLash</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 16px; font-weight: 500;">Nouvelle réservation</p>
                </div>
                
                <!-- Content -->
                <div class="content" style="padding: 32px 24px;">
                    <div style="text-align: center; margin-bottom: 32px;">
                        <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #fef3c7 0%, #f59e0b 100%); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19ZM7 10H9V12H7V10ZM11 10H13V12H11V10ZM15 10H17V12H15V10Z" fill="#d97706"/>
                            </svg>
                        </div>
                        <h2 class="subtitle" style="color: #1f2937; margin: 0 0 8px 0; font-size: 24px; font-weight: 700;">Nouvelle réservation reçue !</h2>
                        <p style="color: #6b7280; margin: 0; font-size: 16px;">Un client vient de faire une réservation</p>
                    </div>
                    
                    <!-- Client Info Card -->
                    <div style="background-color: #f8fafc; border-radius: 12px; padding: 24px; margin: 24px 0; border-left: 4px solid #f97316;">
                        <div style="display: flex; flex-direction: column; gap: 16px;">
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Client</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{user_name}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M20 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Email</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{user_email}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M9.4 16.6L4.8 12L3.4 13.4L9.4 19.4L20.6 8.2L19.2 6.8L9.4 16.6Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Service</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{service_name}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19ZM7 10H9V12H7V10ZM11 10H13V12H11V10ZM15 10H17V12H15V10Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Date</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{appointment_date}</p>
                                </div>
                            </div>
                            
                            <div style="display: flex; align-items: center; padding: 12px 0;">
                                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2ZM12 20C7.59 20 4 16.41 4 12S7.59 4 12 4 20 7.59 20 12 16.41 20 12 20ZM12.5 7H11V13L16.25 16.15L17 14.92L12.5 12.25V7Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Heure</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{appointment_time}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Action Button -->
                    <div style="text-align: center; margin: 32px 0;">
                        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%); border-radius: 12px; padding: 20px; border: 2px solid #f59e0b;">
                            <div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 12px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M1 21H23L12 2L1 21ZM13 18H11V16H13V18ZM13 14H11V10H13V14Z" fill="#d97706"/>
                                </svg>
                                <p style="margin: 0; color: #92400e; font-weight: 600; font-size: 16px;">Action requise</p>
                            </div>
                            <p style="margin: 0; color: #78350f; font-size: 14px; line-height: 1.5;">Connectez-vous à votre espace admin pour confirmer cette réservation et envoyer la confirmation au client.</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #6b7280; font-size: 14px; line-height: 1.6;">
                        <p style="margin: 20px 0 5px 0;">Cordialement,</p>
                        <p style="margin: 0; font-weight: 600; color: #f97316;">Système de réservation HennaLash</p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8fafc; padding: 20px 24px; text-align: center; border-top: 1px solid #e2e8f0;">
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
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nouvel avis client</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #fef7ed; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 32px 24px; text-align: center;">
                    <div style="width: 64px; height: 64px; background-color: rgba(255, 255, 255, 0.15); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z" fill="white"/>
                        </svg>
                    </div>
                    <h1 style="color: white; margin: 0 0 8px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">Nouvel Avis Client</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 16px; font-weight: 500;">Modération requise</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 32px 24px;">
                    <div style="text-align: center; margin-bottom: 32px;">
                        <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #fef3c7 0%, #f59e0b 100%); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z" fill="#d97706"/>
                            </svg>
                        </div>
                        <h2 style="color: #1f2937; margin: 0 0 8px 0; font-size: 24px; font-weight: 700;">Un client a laissé un avis !</h2>
                        <p style="color: #6b7280; margin: 0; font-size: 16px;">Action de modération requise</p>
                    </div>
                    
                    <!-- Rating Display -->
                    <div style="text-align: center; margin: 32px 0;">
                        <div style="display: inline-block; background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%); border-radius: 20px; padding: 24px 32px; border: 3px solid #f59e0b;">
                            <p style="margin: 0 0 12px 0; color: #92400e; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; font-weight: 700;">Note attribuée</p>
                            <div style="display: flex; justify-content: center; gap: 4px; margin: 12px 0;">
                                {''.join([f'<svg width="20" height="20" viewBox="0 0 24 24" fill="#f59e0b" xmlns="http://www.w3.org/2000/svg"><path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z"/></svg>' if i < rating else '<svg width="20" height="20" viewBox="0 0 24 24" fill="#e5e7eb" xmlns="http://www.w3.org/2000/svg"><path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z"/></svg>' for i in range(5)])}
                            </div>
                            <p style="margin: 12px 0 0 0; color: #78350f; font-size: 24px; font-weight: 700;">{rating}/5 étoiles</p>
                        </div>
                    </div>
                    
                    <!-- Client Info Card -->
                    <div style="background-color: #f8fafc; border-radius: 12px; padding: 24px; margin: 24px 0; border-left: 4px solid #f97316;">
                        <div style="display: flex; align-items: center; margin-bottom: 20px;">
                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="white"/>
                                </svg>
                            </div>
                            <div>
                                <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Client</p>
                                <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 20px; font-weight: 700;">{user_name}</p>
                            </div>
                        </div>
                        
                        <!-- Comment Section -->
                        <div style="background-color: white; border-radius: 12px; padding: 20px; border: 2px solid #e2e8f0;">
                            <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
                                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0;">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M20 2H4C2.9 2 2.01 2.9 2.01 4L2 22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H5.17L4 17.17V4H20V16Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0 0 8px 0; color: #374151; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Commentaire client</p>
                                </div>
                            </div>
                            <div style="background-color: #f8fafc; border-radius: 8px; padding: 16px; border-left: 4px solid #10b981;">
                                <p style="margin: 0; color: #1f2937; font-size: 16px; line-height: 1.6; font-style: italic;">"{comment}"</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Action Required -->
                    <div style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); border-radius: 12px; padding: 24px; margin: 32px 0; border: 2px solid #f97316;">
                        <div style="display: flex; align-items: flex-start;">
                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px; flex-shrink: 0;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M1 21H23L12 2L1 21ZM13 18H11V16H13V18ZM13 14H11V10H13V14Z" fill="white"/>
                                </svg>
                            </div>
                            <div>
                                <h4 style="margin: 0 0 8px 0; color: #dc2626; font-size: 18px; font-weight: 700;">Action de modération requise</h4>
                                <p style="margin: 0; color: #7f1d1d; font-size: 15px; line-height: 1.6;">
                                    <strong>Connectez-vous à votre espace admin</strong> pour approuver ou rejeter cet avis.<br>
                                    • <strong>Approuver</strong> : L'avis sera publié sur votre site<br>
                                    • <strong>Rejeter</strong> : L'avis sera supprimé définitivement
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #6b7280; font-size: 14px; line-height: 1.6; margin-top: 32px;">
                        <p style="margin: 20px 0 5px 0;">Cordialement,</p>
                        <p style="margin: 0; font-weight: 600; color: #f97316;">Système de gestion HennaLash</p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8fafc; padding: 24px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0 0 8px 0; color: #64748b; font-size: 12px; line-height: 1.5;">
                        Cet email a été envoyé automatiquement suite à la soumission d'un nouvel avis client.
                    </p>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#f97316" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.63L12 2L9.19 8.63L2 9.24L7.46 13.97L5.82 21L12 17.27Z"/>
                        </svg>
                        <span style="color: #f97316; font-weight: 700; font-size: 14px;">HennaLash Admin</span>
                        <span style="color: #64748b; font-size: 12px;">- Système de modération</span>
                    </div>
                </div>
            </div>
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
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rendez-vous confirmé</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #fef7ed; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 32px 24px; text-align: center;">
                    <div style="width: 64px; height: 64px; background-color: rgba(255, 255, 255, 0.15); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="white"/>
                        </svg>
                    </div>
                    <h1 style="color: white; margin: 0 0 8px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">Rendez-vous Confirmé !</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 16px; font-weight: 500;">Nous avons hâte de vous accueillir</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 32px 24px;">
                    <div style="text-align: center; margin-bottom: 32px;">
                        <h2 style="color: #1f2937; margin: 0 0 8px 0; font-size: 24px; font-weight: 700;">Bonjour {client_name} !</h2>
                        <p style="color: #6b7280; margin: 0; font-size: 16px; line-height: 1.6;">Excellente nouvelle ! Votre rendez-vous a été confirmé par notre équipe.</p>
                    </div>
                    
                    <!-- Appointment Details Card -->
                    <div style="background: linear-gradient(135deg, #fef7ed 0%, #fed7aa 100%); border-radius: 16px; padding: 24px; margin: 24px 0; border: 2px solid #f97316;">
                        <div style="text-align: center; margin-bottom: 24px;">
                            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2L13.09 8.26L22 9.27L17 14.14L18.18 23.02L12 19.77L5.82 23.02L7 14.14L2 9.27L10.91 8.26L12 2Z" fill="white"/>
                                </svg>
                            </div>
                            <h3 style="margin: 0; color: #ea580c; font-size: 20px; font-weight: 700;">Détails de votre rendez-vous</h3>
                        </div>
                        
                        <div style="display: flex; flex-direction: column; gap: 16px;">
                            <div style="background-color: white; border-radius: 12px; padding: 16px; display: flex; align-items: center;">
                                <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 2L13.09 8.26L22 9.27L17 14.14L18.18 23.02L12 19.77L5.82 23.02L7 14.14L2 9.27L10.91 8.26L12 2Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Service</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 18px; font-weight: 700;">{service_name}</p>
                                </div>
                            </div>
                            
                            <div style="background-color: white; border-radius: 12px; padding: 16px; display: flex; align-items: center;">
                                <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19ZM7 10H9V12H7V10ZM11 10H13V12H11V10ZM15 10H17V12H15V10Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Date</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 18px; font-weight: 700;">{appointment_date}</p>
                                </div>
                            </div>
                            
                            <div style="background-color: white; border-radius: 12px; padding: 16px; display: flex; align-items: center;">
                                <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2ZM12 20C7.59 20 4 16.41 4 12S7.59 4 12 4 20 7.59 20 12 16.41 20 12 20ZM12.5 7H11V13L16.25 16.15L17 14.92L12.5 12.25V7Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Heure</p>
                                    <p style="margin: 2px 0 0 0; color: #1e293b; font-size: 18px; font-weight: 700;">{appointment_time}</p>
                                </div>
                            </div>
                            
                            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%); border-radius: 12px; padding: 16px; display: flex; align-items: center; border: 2px solid #f59e0b;">
                                <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2ZM13.41 18.09L13.41 18.09C13.21 18.21 12.7 18.21 12.5 18.09C12.29 17.97 12 17.81 12 17.81S11.71 17.97 11.5 18.09C11.29 18.21 10.79 18.21 10.59 18.09L10.59 18.09C9.4 17.4 8.5 16.4 8.09 15.19C7.68 13.98 7.79 12.67 8.09 11.56C8.39 10.44 8.85 9.47 9.56 8.76C10.27 8.05 11.13 7.6 12 7.6S13.73 8.05 14.44 8.76C15.15 9.47 15.61 10.44 15.91 11.56C16.21 12.67 16.32 13.98 15.91 15.19C15.5 16.4 14.6 17.4 13.41 18.09ZM14 14H10V16H14V14ZM10 10H14V12H10V10Z" fill="white"/>
                                    </svg>
                                </div>
                                <div>
                                    <p style="margin: 0; color: #92400e; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Prix</p>
                                    <p style="margin: 2px 0 0 0; color: #78350f; font-size: 24px; font-weight: 700;">{service_price}€</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Info Box -->
                    <div style="background: linear-gradient(135deg, #fef7ed 0%, #fed7aa 100%); border-radius: 12px; padding: 20px; margin: 24px 0; border-left: 4px solid #f97316;">
                        <div style="display: flex; align-items: flex-start;">
                            <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; flex-shrink: 0;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2ZM13 17H11V11H13V17ZM13 9H11V7H13V9Z" fill="white"/>
                                </svg>
                            </div>
                            <div>
                                <h4 style="margin: 0 0 8px 0; color: #ea580c; font-size: 16px; font-weight: 700;">Informations importantes</h4>
                                <p style="margin: 0; color: #9a3412; font-size: 14px; line-height: 1.6;">
                                    • Merci d'arriver 5 minutes avant l'heure de votre rendez-vous<br>
                                    • En cas d'empêchement, prévenez-nous au moins 24h à l'avance<br>
                                    • N'hésitez pas à nous contacter pour toute question
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 32px 0 20px 0;">
                        <p style="color: #6b7280; font-size: 16px; line-height: 1.6; margin: 0 0 8px 0;">Nous avons hâte de vous accueillir !</p>
                        <p style="color: #1f2937; font-size: 14px; margin: 0 0 4px 0;">Cordialement,</p>
                        <p style="color: #f97316; font-weight: 700; font-size: 16px; margin: 0;">L'équipe HennaLash</p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8fafc; padding: 24px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0 0 8px 0; color: #64748b; font-size: 12px; line-height: 1.5;">
                        Cet email a été envoyé automatiquement suite à la confirmation de votre rendez-vous.
                    </p>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="#f97316" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L13.09 8.26L22 9.27L17 14.14L18.18 23.02L12 19.77L5.82 23.02L7 14.14L2 9.27L10.91 8.26L12 2Z"/>
                        </svg>
                        <span style="color: #f97316; font-weight: 700; font-size: 14px;">HennaLash</span>
                        <span style="color: #64748b; font-size: 12px;">- Votre salon de henné et lashes</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(client_email, subject, body, html_body)

    async def send_appointment_cancellation_to_client(self, client_email: str, client_name: str, 
                                                    service_name: str, appointment_date: str, 
                                                    appointment_time: str, service_price: float):
        """Send appointment cancellation notification to client."""
        subject = f"Annulation de votre rendez-vous - {service_name}"
        
        body = f"""
Bonjour {client_name},

Nous sommes désolés de vous informer que votre rendez-vous a été annulé.

Détails du rendez-vous annulé :
- Service : {service_name}
- Date : {appointment_date}
- Heure : {appointment_time}
- Prix : {service_price}€

N'hésitez pas à reprendre un nouveau rendez-vous quand vous le souhaitez.

Cordialement,
L'équipe HennaLash
        """
        
        html_body = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Annulation de rendez-vous</title>
            <style>
                @media only screen and (max-width: 600px) {{
                    .container {{ width: 100% !important; margin: 0 !important; }}
                    .content {{ padding: 16px !important; }}
                    .header {{ padding: 24px 16px !important; }}
                    .card {{ padding: 16px !important; }}
                    .title {{ font-size: 24px !important; }}
                    .button {{ width: 100% !important; padding: 16px !important; }}
                }}
            </style>
        </head>
        <body style="margin: 0; padding: 20px; background-color: #fef7ed; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div class="container" style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);">
                
                <!-- Header -->
                <div class="header" style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); padding: 32px 24px; text-align: center;">
                    <div style="width: 64px; height: 64px; background-color: rgba(255, 255, 255, 0.15); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px; backdrop-filter: blur(10px);">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="white"/>
                        </svg>
                    </div>
                    <h1 class="title" style="color: white; margin: 0 0 8px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">HennaLash</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 16px; font-weight: 500;">⚠️ Annulation de rendez-vous</p>
                </div>
                
                <!-- Content -->
                <div class="content" style="padding: 32px 24px;">
                    <div style="text-align: center; margin-bottom: 32px;">
                        <h2 style="color: #1f2937; margin: 0 0 16px 0; font-size: 24px; font-weight: 700;">Bonjour {client_name},</h2>
                        <p style="color: #6b7280; margin: 0; font-size: 16px; line-height: 1.6;">
                            Nous sommes désolés de vous informer que votre rendez-vous a été <strong style="color: #dc2626;">annulé</strong>.
                        </p>
                    </div>
                    
                    <!-- Appointment Details -->
                    <div class="card" style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 16px; padding: 24px; margin-bottom: 24px; border: 1px solid #f59e0b;">
                        <h3 style="color: #92400e; margin: 0 0 20px 0; font-size: 18px; font-weight: 700; display: flex; align-items: center;">
                            <span style="margin-right: 8px;">📅</span>
                            Détails du rendez-vous annulé
                        </h3>
                        
                        <div style="display: grid; gap: 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background-color: rgba(255,255,255,0.7); border-radius: 8px;">
                                <span style="color: #92400e; font-weight: 600;">🎨 Service</span>
                                <span style="color: #1f2937; font-weight: 700;">{service_name}</span>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background-color: rgba(255,255,255,0.7); border-radius: 8px;">
                                <span style="color: #92400e; font-weight: 600;">📅 Date</span>
                                <span style="color: #1f2937; font-weight: 700;">{appointment_date}</span>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background-color: rgba(255,255,255,0.7); border-radius: 8px;">
                                <span style="color: #92400e; font-weight: 600;">⏰ Heure</span>
                                <span style="color: #1f2937; font-weight: 700;">{appointment_time}</span>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background-color: rgba(255,255,255,0.7); border-radius: 8px;">
                                <span style="color: #92400e; font-weight: 600;">💰 Prix</span>
                                <span style="color: #1f2937; font-weight: 700;">{service_price}€</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Reassurance Message -->
                    <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #22c55e;">
                        <p style="color: #166534; margin: 0; font-size: 16px; font-weight: 600;">
                            💚 N'hésitez pas à reprendre un nouveau rendez-vous quand vous le souhaitez !
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8fafc; padding: 24px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="color: #6b7280; margin: 0 0 8px 0; font-size: 14px;">
                        Merci de votre compréhension
                    </p>
                    <p style="color: #9ca3af; margin: 0; font-size: 12px; font-weight: 600;">
                        L'équipe HennaLash ✨
                    </p>
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
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Réinitialisation de mot de passe</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #fef7ed; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 32px 24px; text-align: center;">
                    <div style="width: 64px; height: 64px; background-color: rgba(255, 255, 255, 0.15); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 8H17V6C17 3.24 14.76 1 12 1S7 3.24 7 6V8H6C4.9 8 4 8.9 4 10V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V10C20 8.9 19.1 8 18 8ZM12 17C11.17 17 10.5 16.33 10.5 15.5S11.17 14 12 14 13.5 14.67 13.5 15.5 12.83 17 12 17ZM15.1 8H8.9V6C8.9 4.29 10.29 2.9 12 2.9S15.1 4.29 15.1 6V8Z" fill="white"/>
                        </svg>
                    </div>
                    <h1 style="color: white; margin: 0 0 8px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">HennaLash</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 16px; font-weight: 500;">Réinitialisation de mot de passe</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 32px 24px;">
                    <div style="background-color: #f8fafc; border-radius: 12px; padding: 24px; border-left: 4px solid #f97316;">
                        <p style="margin: 0 0 16px 0; color: #1f2937; font-size: 16px;">Bonjour{' ' + first_name if first_name else ''},</p>
                        
                        <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 15px; line-height: 1.6;">Vous avez demandé la réinitialisation de votre mot de passe.</p>
                        
                        <div style="background-color: white; border: 2px solid #f97316; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
                            <p style="margin: 0 0 12px 0; font-weight: 700; color: #374151; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Votre code de réinitialisation :</p>
                            <div style="font-size: 36px; font-weight: 700; color: #f97316; letter-spacing: 6px; font-family: 'Courier New', monospace; margin: 16px 0;">
                                {code}
                            </div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); border-radius: 8px; padding: 16px; border: 1px solid #f87171; margin: 20px 0;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="#dc2626" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2ZM12 20C7.59 20 4 16.41 4 12S7.59 4 12 4 20 7.59 20 12 16.41 20 12 20ZM12.5 7H11V13L16.25 16.15L17 14.92L12.5 12.25V7Z"/>
                                </svg>
                                <p style="margin: 0; color: #dc2626; font-weight: 700; font-size: 14px;">Ce code est valable pendant 15 minutes uniquement.</p>
                            </div>
                        </div>
                        
                        <p style="margin: 20px 0 0 0; color: #6b7280; font-size: 14px;">Si vous n'avez pas fait cette demande, ignorez cet email en toute sécurité.</p>
                        
                        <p style="margin: 24px 0 0 0; color: #374151; font-size: 15px;">
                            Cordialement,<br>
                            <strong style="color: #f97316;">L'équipe HennaLash</strong>
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8fafc; padding: 20px 24px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0; color: #64748b; font-size: 12px; line-height: 1.5;">
                        Cet email a été envoyé automatiquement suite à votre demande de réinitialisation de mot de passe.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(email, subject, body, html_body)

# Global email service instance
email_service = EmailService()