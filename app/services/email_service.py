import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio de envío de emails via Gmail SMTP con App Password."""

    GMAIL_SMTP_HOST = "smtp.gmail.com"
    GMAIL_SMTP_PORT = 587

    def _build_reset_html(self, username: str, code: str) -> str:
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Restablecer contraseña</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background-color:#ffffff;border-radius:8px;overflow:hidden;
                      box-shadow:0 2px 8px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background-color:#1a1a2e;padding:32px 40px;">
              <p style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:.5px;">
                Portfolio API
              </p>
              <p style="margin:6px 0 0;color:#a0aec0;font-size:13px;">
                Restablecimiento de contraseña
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <p style="margin:0 0 16px;color:#2d3748;font-size:15px;">
                Hola, <strong>{username}</strong>
              </p>
              <p style="margin:0 0 24px;color:#4a5568;font-size:14px;line-height:1.6;">
                Recibimos una solicitud para restablecer la contraseña de tu cuenta.
                Usa el siguiente código de verificación:
              </p>

              <!-- Code box -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:24px 0;">
                    <div style="display:inline-block;background-color:#f7fafc;border:2px solid #e2e8f0;
                                border-radius:8px;padding:18px 48px;">
                      <span style="font-size:36px;font-weight:800;letter-spacing:12px;
                                   color:#1a1a2e;font-family:'Courier New',monospace;">
                        {code}
                      </span>
                    </div>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;color:#718096;font-size:13px;text-align:center;">
                ⏳ Este código expira en <strong>{settings.PASSWORD_RESET_CODE_EXPIRE_MINUTES} minutos</strong>.
              </p>
              <p style="margin:0 0 32px;color:#718096;font-size:13px;text-align:center;">
                Si no solicitaste este cambio, puedes ignorar este correo.
              </p>

              <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 0 24px;" />
              <p style="margin:0;color:#a0aec0;font-size:12px;line-height:1.6;">
                Por seguridad, nunca compartas este código con nadie.<br />
                Este es un mensaje automático, por favor no respondas a este correo.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f7fafc;padding:20px 40px;">
              <p style="margin:0;color:#a0aec0;font-size:11px;text-align:center;">
                © 2026 Portfolio API · Todos los derechos reservados
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
        """.strip()

    def send_password_reset_email(self, to_email: str, code: str, username: str) -> None:
        """Envía el email de restablecimiento de contraseña via Gmail SMTP.

        Maneja errores internamente y los registra en el log para no
        interrumpir el flujo de la petición al usuario.
        """
        if not settings.GMAIL_SENDER_EMAIL or not settings.GMAIL_APP_PASSWORD:
            logger.error(
                "GMAIL_SENDER_EMAIL o GMAIL_APP_PASSWORD no están configurados. "
                "El email de reset no pudo ser enviado."
            )
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Código de verificación para restablecer tu contraseña"
        msg["From"] = f"Portfolio API <{settings.GMAIL_SENDER_EMAIL}>"
        msg["To"] = to_email

        plain_text = (
            f"Hola {username},\n\n"
            f"Tu código de verificación es: {code}\n\n"
            f"Expira en {settings.PASSWORD_RESET_CODE_EXPIRE_MINUTES} minutos.\n\n"
            "Si no solicitaste este cambio, ignora este mensaje.\n"
        )
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(self._build_reset_html(username, code), "html", "utf-8"))

        try:
            with smtplib.SMTP(self.GMAIL_SMTP_HOST, self.GMAIL_SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(settings.GMAIL_SENDER_EMAIL, settings.GMAIL_APP_PASSWORD)
                smtp.sendmail(settings.GMAIL_SENDER_EMAIL, to_email, msg.as_string())
            logger.info("Email de reset enviado a %s", to_email)
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "Fallo de autenticación SMTP. Verifica GMAIL_SENDER_EMAIL y GMAIL_APP_PASSWORD."
            )
        except smtplib.SMTPException as exc:
            logger.error("Error SMTP al enviar email de reset: %s", exc)
        except OSError as exc:
            logger.error("Error de red al conectar con Gmail SMTP: %s", exc)

    # ------------------------------------------------------------------ #
    #  Contact form                                                       #
    # ------------------------------------------------------------------ #

    def _build_contact_html(self, name: str, email: str, message: str) -> str:
        safe_name = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_email = email.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br />")
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Nuevo mensaje de contacto</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background-color:#ffffff;border-radius:8px;overflow:hidden;
                      box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <tr>
            <td style="background-color:#1a1a2e;padding:32px 40px;">
              <p style="margin:0;color:#ffffff;font-size:22px;font-weight:700;letter-spacing:.5px;">
                Portfolio API
              </p>
              <p style="margin:6px 0 0;color:#a0aec0;font-size:13px;">
                Nuevo mensaje de contacto
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:40px;">
              <p style="margin:0 0 8px;color:#718096;font-size:13px;">De:</p>
              <p style="margin:0 0 20px;color:#2d3748;font-size:15px;">
                <strong>{safe_name}</strong> &lt;{safe_email}&gt;
              </p>
              <p style="margin:0 0 8px;color:#718096;font-size:13px;">Mensaje:</p>
              <div style="background-color:#f7fafc;border:1px solid #e2e8f0;border-radius:6px;
                          padding:20px;color:#2d3748;font-size:14px;line-height:1.6;">
                {safe_message}
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color:#f7fafc;padding:20px 40px;">
              <p style="margin:0;color:#a0aec0;font-size:11px;text-align:center;">
                Mensaje enviado desde el formulario de contacto del portfolio.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
        """.strip()

    def send_contact_email(self, name: str, email: str, message: str) -> bool:
        """Envía un email de contacto al propietario del portfolio.

        Returns True si se envió correctamente, False en caso contrario.
        """
        if not settings.GMAIL_SENDER_EMAIL or not settings.GMAIL_APP_PASSWORD:
            logger.error(
                "GMAIL_SENDER_EMAIL o GMAIL_APP_PASSWORD no están configurados. "
                "El email de contacto no pudo ser enviado."
            )
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Nuevo mensaje de contacto de {name}"
        msg["From"] = f"Portfolio API <{settings.GMAIL_SENDER_EMAIL}>"
        msg["To"] = settings.GMAIL_SENDER_EMAIL
        msg["Reply-To"] = email

        plain_text = (
            f"Nuevo mensaje de contacto\n\n"
            f"De: {name} <{email}>\n\n"
            f"Mensaje:\n{message}\n"
        )
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(self._build_contact_html(name, email, message), "html", "utf-8"))

        try:
            with smtplib.SMTP(self.GMAIL_SMTP_HOST, self.GMAIL_SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(settings.GMAIL_SENDER_EMAIL, settings.GMAIL_APP_PASSWORD)
                smtp.sendmail(
                    settings.GMAIL_SENDER_EMAIL,
                    settings.GMAIL_SENDER_EMAIL,
                    msg.as_string(),
                )
            logger.info("Email de contacto recibido de %s <%s>", name, email)
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "Fallo de autenticación SMTP. Verifica GMAIL_SENDER_EMAIL y GMAIL_APP_PASSWORD."
            )
            return False
        except smtplib.SMTPException as exc:
            logger.error("Error SMTP al enviar email de contacto: %s", exc)
            return False
        except OSError as exc:
            logger.error("Error de red al conectar con Gmail SMTP: %s", exc)
            return False
