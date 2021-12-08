from flask import Flask, render_template, request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests, pytz, smtplib, ssl, os

app = Flask(__name__)
api_key = '1512569043d30a4b91f6d131ab270736'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    weather = {}
    city = request.args.get("search")

    if city:
        search_results = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'
        response = requests.get(search_results.format(city, api_key)).json()

        weather = {
            'city': response['name'].title(),
            'tempurature': response['main']['temp'],
            'feels_like': response['main']['feels_like'],
            'temp_min': response['main']['temp_min'],
            'temp_max': response['main']['temp_max'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
            'country': pytz.country_names[response['sys']['country']]
        }
    return render_template('index.html', weather=weather)


@app.route('/email', methods=['GET', 'POST'])
def email():
    weather = {}
    email = request.form.get("email")
    location = request.form.get("location")
    
    # Splitting email address to get name
    email_name = email.split('@')
    
    sender_email = "mock.email.server@gmail.com"
    sender_password = os.getenv("mockemailserverpassword")
    
    # Setting up multipart email with required fields
    email_serve = MIMEMultipart("alternative")
    email_serve['Subject'] = "Weather Information - OpenWeatherAPI"
    email_serve['From'] = sender_email
    email_serve['To'] = email

    # Checking if email and location fields have input
    if not email or not location:
        error_statement = "Email and Location Required..."
        return render_template('index.html', error_statement=error_statement)

    # Getting response from OpenWeatherAPI using location provided
    search_results = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'
    response = requests.get(search_results.format(location, api_key)).json()

    weather = {
        'city': response['name'].title(),
        'tempurature': response['main']['temp'],
        'feels_like': response['main']['feels_like'],
        'temp_min': response['main']['temp_min'],
        'temp_max': response['main']['temp_max'],
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
        'country': pytz.country_names[response['sys']['country']]
    }
    
    message = """\
    <html>
        <body>
            <p>Hello <strong>{}</strong>,</p>
            <p>The requested weather for <strong>{}</strong> is below:</p>
            <ul>
                <li>City, Country: <strong>{}, {}</strong></li>
                <li>Tempurature: <strong>{}°C</strong></li>
                <li>Feels Like: <strong>{}°C</strong></li>
                <li>Low/High: <strong>{}°C/{}°C</strong></li>
                <li>Description: <strong>{}</strong></li>
            </ul> 
        </body>
    </html>
    """.format(email_name[0], location, weather['city'], weather['country'], weather['tempurature'], weather['feels_like'], weather['temp_min'], weather['temp_max'], weather['description'])
    
    # Adding html message to email multipart
    email_serve_message = MIMEText(message, "html")
    email_serve.attach(email_serve_message)
    
    # Creating secure connection and sending email
    email_context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=email_context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, email_serve.as_string())

    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
