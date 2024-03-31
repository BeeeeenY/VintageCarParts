from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
from flasgger import Swagger

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'shipping microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows retrieval of shipping rates'
}
swagger = Swagger(app)

@app.route('/shipping', methods=['GET', 'POST'])
def get_shipping_rate():

    """
    Retrieve shipping rates.

    ---
    tags:
        -   Shipping
    parameters:
        -   name: origin_country
            in: query
            required: true
            type: string
            description: The origin country for shipping.
        -   name: destination_country
            in: query
            required: true
            type: string
            description: The destination country for shipping.
    responses:
            200:
                description: Shipping rates retrieved successfully.
            400:
                description: Invalid request.
    """

    get_origin_country_url = 'http://host.docker.internal:5002/get_country'
    get_origin_country_params = {'part_id': 3}
    get_origin_country_response = requests.get(get_origin_country_url, params=get_origin_country_params)

    if get_origin_country_response.status_code == 200:
        origin_country = get_origin_country_response.json().get('Country')
        print("Origin country:", origin_country)


    get_destination_country_url = 'http://host.docker.internal:5004/get_country'
    get_destination_country_params = {'user_id': 3}
    get_destination_country_response = requests.get(get_destination_country_url, params=get_destination_country_params)

    if get_destination_country_response.status_code == 200:
        destination_country = get_destination_country_response.json().get('country')
        print("Destination country:", destination_country)

    # Constructing the URL with dynamic origin and destination countries
    url = f"https://ship.freightos.com/api/shippingCalculator?loadtype=boxes&weight=1&width=50&length=50&height=50&origin={origin_country}&quantity=1&destination={destination_country}"

    response = requests.get(url)
    data = response.json()

    estimated_rates = data['response']['estimatedFreightRates']

    if 'mode' in estimated_rates:
        modes = estimated_rates['mode']
        if isinstance(modes, list) and len(modes) >= 1:
            # If 'mode' is a list, take the first mode
            first_mode = modes[0]
        elif isinstance(modes, dict):
            # If 'mode' is a dictionary, use it directly
            first_mode = modes

        min_price = first_mode['price']['min']['moneyAmount']['amount']
        max_price = first_mode['price']['max']['moneyAmount']['amount']
        min_transit_time = first_mode['transitTimes']['min']
        max_transit_time = first_mode['transitTimes']['max']
        
        print(f"Min Price: {min_price} USD")
        print(f"Max Price: {max_price} USD")
        print(f"Min Transit Time: {min_transit_time} days")
        print(f"Max Transit Time: {max_transit_time} days")
    else:
        print("No shipping rates found.")

    return "Shipping rates retrieved."

        # print("Max Price:", max_price, "USD")
        # print("Min Transit Time:", min_transit_time, "days")
        # print("Max Transit Time:", max_transit_time, "days")

if __name__ == '__main__':
    app.run(port=5008, debug=True)