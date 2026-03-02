import os
from dotenv import load_dotenv
load_dotenv()

def send_sms_alert(farmer_name, risk_level, risk_score, phone_number, crop, district):
    """
    Send SMS alert via Twilio.
    Sign up free at twilio.com → get SID, Token, Phone number → add to .env
    """
    try:
        from twilio.rest import Client
        account_sid = os.getenv("TWILIO_SID")
        auth_token  = os.getenv("TWILIO_TOKEN")
        from_number = os.getenv("TWILIO_PHONE")

        if not all([account_sid, auth_token, from_number]):
            return False, "Twilio credentials not set in .env file"

        messages = {
            "High": (
                f" AgriSOS ALERT\n"
                f"Farmer: {farmer_name} | {district}\n"
                f"Crop: {crop} | Risk Score: {risk_score}/100 (HIGH)\n"
                f"Immediate action needed!\n"
                f"Helpline: 1800-180-1551 (KVK - Free)"
            ),
            "Medium": (
                f" AgriSOS WARNING\n"
                f"Farmer: {farmer_name} | {district}\n"
                f"Crop: {crop} | Risk Score: {risk_score}/100 (MEDIUM)\n"
                f"Monitor your crop closely this week."
            ),
            "Low": (
                f" AgriSOS Update\n"
                f"Farmer: {farmer_name} | {district}\n"
                f"Crop: {crop} | Risk Score: {risk_score}/100 (LOW)\n"
                f"Conditions look stable. Stay alert!"
            ),
        }

        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=messages[risk_level],
            from_=from_number,
            to=phone_number
        )
        return True, f"SMS sent! SID: {msg.sid}"

    except ImportError:
        return False, "Twilio not installed. Run: pip install twilio"
    except Exception as e:
        return False, str(e)