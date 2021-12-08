from flask import Flask, render_template, request, jsonify
import requests, pytz

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    weather = {}
    if request.method == 'GET':
        api_key = '1512569043d30a4b91f6d131ab270736'
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

if __name__ == '__main__':
    app.debug = True
    app.run()