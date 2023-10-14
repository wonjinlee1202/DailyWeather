import schedule
import time
import requests
import email, smtplib, ssl
from providers import PROVIDERS
from datetime import datetime

def get_weather(latitude, longitude):
    base_url = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m".format(latitude, longitude)
    response = requests.get(base_url)
    data = response.json()
    return data

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def send_sms_via_email(
    number: str,
    message: str,
    provider: str,
    sender_credentials: tuple,
    subject: str = "DailyWeather",
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 465,
):
    sender_email, email_password = sender_credentials
    receiver_email = f'{number}@{PROVIDERS.get(provider).get("sms")}'

    email_message = f"Subject:{subject}\nTo:{receiver_email}\n{message}"

    with smtplib.SMTP_SSL(
        smtp_server, smtp_port, context=ssl.create_default_context()
    ) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, receiver_email, email_message)

def send_weather_update():
    latitude = 34.0635
    longitude = -118.4455

    weather_data = get_weather(latitude, longitude)
    today_date = datetime.now().date()
    search_time = today_date.strftime('%Y-%m-%dT08:00')
    index = weather_data["hourly"]["time"].index(search_time)
    temperature_celsius = sum(weather_data["hourly"]["temperature_2m"][index:index+23])/24
    relativehumidity = round(sum(weather_data["hourly"]["relativehumidity_2m"][index:index+23])/24, 2)
    wind_speed = round(sum(weather_data["hourly"]["windspeed_10m"][index:index+23])/24, 2)
    temperature_fahrenheit = round(celsius_to_fahrenheit(temperature_celsius), 2)

    weather_info = (
        f"\n\n\nGood morning!\n"
        f"\nToday's weather:\n"
        f"Temperature: {temperature_fahrenheit:.2f} F\n"
        f"Relative Humidity: {relativehumidity}%\n"
        f"Wind Speed: {wind_speed} m/s\n"
    )

    send_sms_via_email("phone-number", weather_info, "carrier", ("xxxxx@gmail.com", "google-app-password"))

def main():
    schedule.every().day.at("08:00").do(send_weather_update)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()