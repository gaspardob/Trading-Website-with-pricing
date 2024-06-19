# Other libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from urllib.request import urlopen
import requests
import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries
import time

from datetime import datetime, timedelta
import pandas as pd

# import yfinance as yf

key = "238e6abfb856d6a972ed6aca3ef75418"
# key = '84b2859fb03d27f28125c365b0b8967d'


symbol = "NVDA"


def prix_de_cloture_passé(symbol):
    # URL de l'API pour récupérer les données historiques des prix d'une action
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey=84b2859fb03d27f28125c365b0b8967d"

    # Effectuer la requête GET vers l'API
    response = requests.get(url)

    if response.status_code == 200:
        # Convertir la réponse en format JSON
        data = response.json()
        # Récupérer les prix de clôture
        historical_data = data["historical"]

        # Extraire les dates et les prix de clôture pour le tracé
        dates = [entry["date"] for entry in historical_data]

        # Convertir les chaînes de date en objets datetime pour un meilleur affichage graphique
        dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

        closing_prices = [float(entry["close"]) for entry in historical_data]

        # Tracer le graphique
        # plt.figure(figsize=(10, 6))
        # plt.plot(dates, closing_prices, linestyle='-')
        # plt.title(f'Historique des prix de clôture pour {symbol}')
        # plt.xlabel('Date')
        # plt.ylabel('Prix de clôture')
        # plt.xticks(rotation=45)
        # plt.tight_layout()
        # plt.show()

        daily_logvariation = []
        for i in range(len(closing_prices) - 1):
            n = len(daily_logvariation)
            if closing_prices[i + 1] - closing_prices[i] > 1e-8:
                daily_logvariation.append(
                    np.log(closing_prices[i + 1] / closing_prices[i])
                )
        logmoy = sum(daily_logvariation) / n
        square = [(daily_logvariation[i] - logmoy) ** 2 for i in range(n)]
        s = sum(square) / (n - 1)
        volatilty = np.sqrt(s) * np.sqrt(
            255
        )  # on observe tous les jours et l'on suppose qu'il y a 255 jours de bourse sur un an
        # print(volatilty)
        return volatilty
    else:
        print("Échec de la requête. Vérifiez votre clé API ou le symbole de l'action.")


# def prix_actuelle(symbol):
#     #current_price_url = f'https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={key}'
#     current_price_url=f'https://financialmodelingprep.com/api/v3/stock/real-time-price/{symbol}?apikey=84b2859fb03d27f28125c365b0b8967d'

#     response_current_price = requests.get(current_price_url)

#     data_current_price = response_current_price.json()


#     print(data_current_price)
#     # Récupérer le prix actuel de l'action
#     print(data_current_price["companiesPriceList"])
#     #current_price = data_current_price["companiesPriceList"][0]['price']

#     return 100


def prix_actuelle(symbol):
    api_key = "84b2859fb03d27f28125c365b0b8967d"
    current_price_url = (
        f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}"
    )

    try:
        response_current_price = requests.get(current_price_url)
        response_current_price.raise_for_status()  # Vérifier les erreurs HTTP

        data_current_price = response_current_price.json()
        # print(data_current_price)
        # Récupérer le prix actuel de l'action
        current_price = data_current_price[0]["price"]
        return current_price

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")
        return None


def plot_yesterday_stock(symbol):
    # le programme ne marche pas le dimanche, samedi car bourse fermer
    api_key = "UFXVJ7HAEGYV19TX"
    ts = TimeSeries(key=api_key, output_format="pandas")

    # Récupération des données intraday (par 5 minutes) pour la journée d'hier
    yesterday = datetime.now() - timedelta(days=1)

    data, meta_data = ts.get_intraday(symbol=symbol, interval="5min", outputsize="full")

    # Filtrer les données pour inclure uniquement celles d'hier avant l'heure actuelle
    date_actuelle = datetime.now()

    jour_semaine = date_actuelle.strftime("%A")

    if jour_semaine == "Monday":
        yesterday = datetime.now() - timedelta(
            days=3
        )  # on prend les données du vendredi pour le lundi
    if jour_semaine == "Sunday" or jour_semaine == "Saturday":
        print("La bourse est fermé le week end")
        return

    market_open_time = yesterday.replace(
        hour=9, minute=30, second=0
    )  # heure d'ouverture du marché

    heure_actuelle = datetime.now()

    heure_int = heure_actuelle.hour
    minutes_int = heure_actuelle.minute
    seconde_int = heure_actuelle.second
    if heure_int > 17:
        heure_int = 17
        minutes_int = 0
        seconde_int = 0

    timestamps = data.index
    filtered_timestamps = []
    filtered_prices = []
    for i, timestamp in enumerate(timestamps):
        if timestamp >= market_open_time and timestamp < yesterday.replace(
            hour=heure_int, minute=minutes_int, second=seconde_int
        ):
            filtered_timestamps.append(timestamp)
            filtered_prices.append(data["4. close"][i])

    # Convertir les timestamps en format 'heure:minute'
    formatted_timestamps = [t.strftime("%H:%M") for t in filtered_timestamps]

    # Tracé initial du graphique
    # plt.figure(figsize=(15,8))
    formatted_timestamps.reverse()
    filtered_prices.reverse()
    # plt.plot(formatted_timestamps, filtered_prices, label='Prix intraday')
    # plt.xlabel('Heure')
    # plt.ylabel('Prix de l\'action')
    # plt.title(f'Prix de l\'action {symbol} hier jusqu\'à l\'heure actuelle')

    # plt.legend()
    # plt.xticks(rotation=45)
    # plt.tight_layout()

    # plt.show()
    return formatted_timestamps, filtered_prices


def get_stock_symbols():
    # Endpoint pour obtenir une liste de symboles boursiers
    endpoint = f"https://financialmodelingprep.com/api/v3/stock/list?apikey=84b2859fb03d27f28125c365b0b8967d"

    response = requests.get(endpoint)
    data = response.json()

    # Création du dictionnaire marque-action
    marques_actions = {}
    for company in data:
        marque = company["name"]
        marche = company["exchangeShortName"]
        symbol = company["symbol"]
        if marche == "NASDAQ":
            marques_actions[marque] = symbol
    return marques_actions


def nom_marque_to_symbol(nom_marque):
    marques_actions = get_stock_symbols()
    return marques_actions[nom_marque]


# fonction pour tester lorsqu'il y a eu plus de 25 tentatives


def fonction(symbol):
    if symbol == "chat":
        L = [4, 5, 6]
        V = [1, 3, 4]
        rep = L, V
        return rep
    else:
        L = [1, 1, 1]
        V = [1, 1, 1]
        rep = L, V
        return rep


def fonction_2(Symbol):
    return "chat"
