"""
F030: Multi-Channel Notification Dispatch.
Email (SendGrid/SMTP), push notifications, dashboard alerts per alert type.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """
    Multi-channel notification system supporting:
    - Email (SendGrid API or SMTP fallback)
    - Push notifications (placeholder for FCM/APNs)
    - Dashboard alerts (via WebSocket broadcast)
    """

    # Alert type -> default channels
    CHANNEL_MAP = {
        "budget_exhaustion": ["email", "dashboard", "push"],
        "evs_threshold": ["email", "dashboard"],
        "financial_anomaly": ["email", "dashboard", "push"],
        "cashflow_warning": ["email", "dashboard"],
        "milestone_delay": ["dashboard"],
    }

    async def dispatch(
        self,
        alert_type: str,
        severity: str,
        message: str,
        recipient_email: Optional[str] = None,
        entity_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        channels: Optional[list] = None,
    ) -> dict:
        """Dispatch notification across configured channels."""
        if channels is None:
            channels = self.CHANNEL_MAP.get(alert_type, ["dashboard"])

        results = {}

        for channel in channels:
            try:
                if channel == "email" and recipient_email:
                    results["email"] = await self._send_email(
                        to=recipient_email,
                        subject=f"[{severity.upper()}] {alert_type}: Financial Alert",
                        body=message,
                    )
                elif channel == "dashboard":
                    results["dashboard"] = await self._push_to_dashboard(
                        alert_type=alert_type,
                        severity=severity,
                        message=message,
                        entity_id=entity_id,
                    )
                elif channel == "push":
                    results["push"] = await self._send_push(
                        title=f"{alert_type} Alert",
                        body=message,
                    )
            except Exception as e:
                results[channel] = {"status": "failed", "error": str(e)}
                logger.error(f"Notification dispatch failed on {channel}: {e}")

        return results

    async def _send_email(self, to: str, subject: str, body: str) -> dict:
        """Send email via SendGrid API or SMTP fallback."""
        sendgrid_key = settings.SENDGRID_API_KEY

        if sendgrid_key:
            return await self._send_via_sendgrid(to, subject, body, sendgrid_key)
        else:
            return self._send_via_smtp(to, subject, body)

    async def _send_via_sendgrid(self, to: str, subject: str, body: str, api_key: str) -> dict:
        """Send email using SendGrid API."""
        try:
            import httpx
            payload = {
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": "alerts@financial-roi.io", "name": "Financial ROI Intelligence"},
                "subject": subject,
                "content": [
                    {"type": "text/html", "value": self._format_email_html(subject, body)}
                ],
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json=payload,
                    timeout=10,
                )
                if resp.status_code in (200, 202):
                    logger.info(f"SendGrid email sent to {to}")
                    return {"status": "sent", "provider": "sendgrid"}
                else:
                    logger.error(f"SendGrid error: {resp.status_code} {resp.text}")
                    return {"status": "failed", "provider": "sendgrid", "error": resp.text}
        except Exception as e:
            logger.error(f"SendGrid dispatch error: {e}")
            return {"status": "failed", "provider": "sendgrid", "error": str(e)}

    def _send_via_smtp(self, to: str, subject: str, body: str) -> dict:
        """Fallback SMTP email sending."""
        logger.info(f"[SMTP-MOCK] Email to={to}, subject={subject}")
        return {"status": "logged", "provider": "smtp_mock", "to": to, "subject": subject}

    def _format_email_html(self, subject: str, body: str) -> str:
        """Format email as HTML with styling."""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1a1a2e; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0;">🔔 Financial ROI Intelligence</h2>
            </div>
            <div style="padding: 20px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px;">
                <h3>{subject}</h3>
                <p style="color: #333; line-height: 1.6;">{body}</p>
                <hr style="border: none; border-top: 1px solid #e0e0e0;">
                <p style="color: #999; font-size: 12px;">
                    This alert was generated by the AI Financial Management &amp; ROI Intelligence Platform.
                </p>
            </div>
        </div>
        """

    async def _push_to_dashboard(self, alert_type: str, severity: str, message: str, entity_id: int = None) -> dict:
        """Push notification to WebSocket dashboard connections."""
        try:
            from app.api.ws.manager import ws_manager
            await ws_manager.broadcast({
                "type": "notification",
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "entity_id": entity_id,
            })
            return {"status": "pushed", "channel": "websocket"}
        except Exception as e:
            logger.warning(f"Dashboard push failed: {e}")
            return {"status": "logged", "channel": "websocket_fallback"}

    async def _send_push(self, title: str, body: str) -> dict:
        """Push notification via FCM/APNs (placeholder)."""
        logger.info(f"[PUSH-MOCK] title={title}, body={body}")
        return {"status": "logged", "provider": "push_mock", "title": title}


# Singleton
notification_dispatcher = NotificationDispatcher()
