"""Email service for Joulaa platform with Arabic support"""

import asyncio
from typing import Dict, Any, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
from jinja2 import Environment, FileSystemLoader, select_autoescape
import structlog
from pathlib import Path

from ..core.config import settings
from ..models.user import User
from ..core.exceptions import EmailServiceError

logger = structlog.get_logger()


class EmailService:
    """Email service with Arabic template support"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        
        # Setup Jinja2 environment for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            enable_async=True
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        language: str = "ar"
    ) -> bool:
        """Send email with Arabic support"""
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Set RTL direction for Arabic emails
            if language == "ar":
                msg['Content-Language'] = 'ar'
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(
                "Email sent successfully",
                to_email=to_email,
                subject=subject,
                language=language
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send email",
                to_email=to_email,
                subject=subject,
                error=str(e),
                exc_info=True
            )
            raise EmailServiceError(f"Failed to send email: {str(e)}")
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        
        try:
            with open(attachment['path'], 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error(
                "Failed to add attachment",
                attachment_path=attachment.get('path'),
                error=str(e)
            )
    
    async def send_verification_email(self, user: User) -> bool:
        """Send email verification email"""
        
        try:
            # Generate verification token (implement in user service)
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={user.verification_token}"
            
            # Determine language and template
            language = user.language_preference or "ar"
            template_name = f"verification_{language}.html"
            
            # Render template
            template = self.jinja_env.get_template(template_name)
            html_content = await template.render_async(
                user_name=user.full_name_ar if language == "ar" else user.full_name_en,
                verification_url=verification_url,
                app_name="جولة" if language == "ar" else "Joulaa",
                support_email=settings.SUPPORT_EMAIL
            )
            
            subject = "تأكيد البريد الإلكتروني - جولة" if language == "ar" else "Email Verification - Joulaa"
            
            return await self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                language=language
            )
            
        except Exception as e:
            logger.error(
                "Failed to send verification email",
                user_id=str(user.id),
                error=str(e),
                exc_info=True
            )
            return False
    
    async def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email"""
        
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            language = user.language_preference or "ar"
            template_name = f"password_reset_{language}.html"
            
            template = self.jinja_env.get_template(template_name)
            html_content = await template.render_async(
                user_name=user.full_name_ar if language == "ar" else user.full_name_en,
                reset_url=reset_url,
                app_name="جولة" if language == "ar" else "Joulaa",
                support_email=settings.SUPPORT_EMAIL,
                expiry_hours=24
            )
            
            subject = "إعادة تعيين كلمة المرور - جولة" if language == "ar" else "Password Reset - Joulaa"
            
            return await self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                language=language
            )
            
        except Exception as e:
            logger.error(
                "Failed to send password reset email",
                user_id=str(user.id),
                error=str(e),
                exc_info=True
            )
            return False
    
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new users"""
        
        try:
            language = user.language_preference or "ar"
            template_name = f"welcome_{language}.html"
            
            template = self.jinja_env.get_template(template_name)
            html_content = await template.render_async(
                user_name=user.full_name_ar if language == "ar" else user.full_name_en,
                app_name="جولة" if language == "ar" else "Joulaa",
                dashboard_url=f"{settings.FRONTEND_URL}/dashboard",
                support_email=settings.SUPPORT_EMAIL,
                docs_url=f"{settings.FRONTEND_URL}/docs"
            )
            
            subject = "مرحباً بك في جولة!" if language == "ar" else "Welcome to Joulaa!"
            
            return await self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                language=language
            )
            
        except Exception as e:
            logger.error(
                "Failed to send welcome email",
                user_id=str(user.id),
                error=str(e),
                exc_info=True
            )
            return False
    
    async def send_organization_invite_email(
        self,
        invitee_email: str,
        inviter_name: str,
        organization_name: str,
        invite_token: str,
        language: str = "ar"
    ) -> bool:
        """Send organization invitation email"""
        
        try:
            invite_url = f"{settings.FRONTEND_URL}/accept-invite?token={invite_token}"
            
            template_name = f"organization_invite_{language}.html"
            
            template = self.jinja_env.get_template(template_name)
            html_content = await template.render_async(
                inviter_name=inviter_name,
                organization_name=organization_name,
                invite_url=invite_url,
                app_name="جولة" if language == "ar" else "Joulaa",
                support_email=settings.SUPPORT_EMAIL,
                expiry_days=7
            )
            
            subject = f"دعوة للانضمام إلى {organization_name} - جولة" if language == "ar" else f"Invitation to join {organization_name} - Joulaa"
            
            return await self.send_email(
                to_email=invitee_email,
                subject=subject,
                html_content=html_content,
                language=language
            )
            
        except Exception as e:
            logger.error(
                "Failed to send organization invite email",
                invitee_email=invitee_email,
                organization_name=organization_name,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def send_notification_email(
        self,
        user: User,
        notification_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """Send notification email based on type"""
        
        try:
            language = user.language_preference or "ar"
            template_name = f"notification_{notification_type}_{language}.html"
            
            template = self.jinja_env.get_template(template_name)
            html_content = await template.render_async(
                user_name=user.full_name_ar if language == "ar" else user.full_name_en,
                app_name="جولة" if language == "ar" else "Joulaa",
                support_email=settings.SUPPORT_EMAIL,
                **context
            )
            
            # Get subject from context or use default
            subject = context.get('subject', 
                f"إشعار من جولة" if language == "ar" else "Notification from Joulaa"
            )
            
            return await self.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                language=language
            )
            
        except Exception as e:
            logger.error(
                "Failed to send notification email",
                user_id=str(user.id),
                notification_type=notification_type,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        language: str = "ar",
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """Send bulk emails with rate limiting"""
        
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "errors": []
        }
        
        # Process in batches to avoid overwhelming SMTP server
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            # Send emails in parallel within batch
            tasks = [
                self.send_email(
                    to_email=email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    language=language
                )
                for email in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append({
                        "email": batch[j],
                        "error": str(result)
                    })
                elif result:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
            
            # Add delay between batches
            if i + batch_size < len(recipients):
                await asyncio.sleep(1)
        
        logger.info(
            "Bulk email completed",
            total=results["total"],
            sent=results["sent"],
            failed=results["failed"]
        )
        
        return results


# Global email service instance
email_service = EmailService()