import os
import sys
import requests
from twilio.rest import Client

# This works locally or on GitHub servers without leaking keys in the code text
WEATHER_KEY = os.environ.get('WEATHER_KEY')
TWILIO_SID = os.environ.get('ACC_SID')
TWILIO_TOKEN = os.environ.get('AUTH_TOK')

# Target Phone Numbers and Configuration
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER') # e.g., '+18313876061'
MY_NUMBER = os.environ.get('MY_NUMBER')         # e.g., '+918019659595'

# Guard clause: stop execution if vital deployment configuration is missing
if not all([WEATHER_KEY, TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER, MY_NUMBER]):
    print("❌ Error: Missing configuration keys in environment variables.")
    sys.exit(1)

WEATHER_API_URL = 'http://api.weatherapi.com/v1/forecast.json'
TARGET_COORDINATES = '18.8748343,77.9167345'  # Latitude, Longitude layout

query_parameters = {
    'q': TARGET_COORDINATES,
    'key': WEATHER_KEY,
    'days': 5
}


def get_today_weather() -> str:
    """Queries WeatherAPI to extract today's text weather condition phrase."""
    print("Querying WeatherAPI forecasts...")
    try:
        response = requests.get(WEATHER_API_URL, params=query_parameters)
        response.raise_for_status()
        
        weather_data = response.json()
        forecast_days = weather_data['forecast']['forecastday']
        
        # Pull text condition from the very first day index [0]
        condition_text = forecast_days[0]['day']['condition']['text']
        return condition_text
        
    except requests.exceptions.RequestException as req_err:
        print(f"❌ WeatherAPI request failed: {req_err}")
        return ""
    except (KeyError, IndexError):
        print("❌ Unexpected data structure returned from WeatherAPI.")
        return ""


def send_sms_alert(weather_message: str):
    """Dispatches weather condition string via Twilio SMS service gateway."""
    print("Initializing Twilio dispatch engine...")
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        
        message = client.messages.create(
            from_=TWILIO_NUMBER,
            to=MY_NUMBER,
            body=f"Today's weather is: {weather_message}"
        )
        print(f"Message sent successfully! SID reference: {message.sid}")
        
    except Exception as twilio_error:
        print(f"Twilio routing failed. Reason: {twilio_error}")


def main():
    today_condition = get_today_weather()
    if not today_condition:
        print("Aborting SMS dispatch due to upstream collection errors.")
        return
    send_sms_alert(today_condition)


if __name__ == '__main__':
    main()
