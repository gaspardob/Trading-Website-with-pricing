from flask import Flask, render_template, request, flash
from flask import redirect, url_for, session
from flask import jsonify
import json

# Import other necessary modules
import os
import sys

# sys.path.append('/Users/clementdureuil/Downloads/2A/TDLOG/Projet TD LOG FINAL/PROJET-GCYF/src')
# sys.path.append('/Users/gaspardbeaudouin/Desktop/2A/Projet_TDLOG/PROJET_GCYF/src')

# Obtenez le chemin absolu du répertoire du script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Ajoutez le chemin relatif au répertoire du script
sys.path.append(os.path.join(script_dir, "src"))

import pandas as pd
from src import financeProg
from src.financeProg import *
from scipy.stats import norm
import numpy as np
import os


app = Flask(__name__)
from src.portefeuille import Porte_feuille

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///users.db"  # Chemin vers la base de données
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Modèle de l'utilisateur


# Créer la base de données (s'il n'existe pas encore)
with app.app_context():
    db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=500.0)
    stock_portfolio = db.Column(db.JSON, default={})
    european_option_portfolio = db.Column(db.JSON, default={})
    american_option_portfolio = db.Column(db.JSON, default={})


@app.route("/buy_stock", methods=["POST"])
def buy_stock():
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        user = User.query.get(user_id)
        number_of_stocks = int(request.form.get("stock_number_buy"))

        new_stock_portfolio = user.stock_portfolio.copy()
        # Get the stock name and validate it (you may add additional validation)
        stock_name = request.form.get("stock_name_buy")
        print(stock_name)

        if not stock_name:
            return "Invalid stock name."

        # Get the current price of the stock using the prix_actuelle function
        stock_price = prix_actuelle(stock_name)
        print("stock_price = ", stock_price)

        # Check if the user has enough balance to buy the stock
        if user.balance >= number_of_stocks * stock_price:
            # Deduct the stock price from the user's balance
            user.balance -= number_of_stocks * stock_price
            print("user.balance after purchase:", user.balance)

            user = User.query.get(user_id)
            # Update the user's portfolio
            if stock_name in user.stock_portfolio:
                new_stock_portfolio[stock_name] += number_of_stocks
            else:
                new_stock_portfolio[stock_name] = number_of_stocks

            user.stock_portfolio = new_stock_portfolio
            # Commit changes to the database after making all updates
            db.session.commit()

            print("user.stock_portfolio after purchase:", user.stock_portfolio)

            flash(
                f"Achat réussi! Tu as acheté {number_of_stocks} actions de {stock_name} cotées {stock_price}€ pour un total de {number_of_stocks * stock_price}€ "
            )
            return render_template(
                "actions.html",
                username=user.username,
                balance=round(user.balance, 2),
                stock_portfolio=user.stock_portfolio,
                real_user=user,
            )
        else:
            flash(f"Solde insuffisant pour acheter cette action.")
            return render_template(
                "actions.html",
                username=user.username,
                balance=round(user.balance, 2),
                stock_portfolio=user.stock_portfolio,
                real_user=user,
            )
    return redirect(url_for("login"))


@app.route("/sell_stock", methods=["POST"])
def sell_stock():
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        user = User.query.get(user_id)
        number_of_stocks = int(request.form.get("stock_number_sell"))
        new_stock_portfolio = user.stock_portfolio.copy()
        # Get the stock name and validate it (you may add additional validation)
        stock_name = request.form.get("stock_name_sell")
        print(stock_name)
        if not stock_name:
            return "Invalid stock name."

        # Get the current price of the stock using the prix_actuelle function
        stock_price = prix_actuelle(stock_name)
        print("stock_price = ", stock_price)

        if (
            stock_name in user.stock_portfolio
            and new_stock_portfolio[stock_name] >= number_of_stocks
        ):
            user.balance += number_of_stocks * stock_price
            print("user.balance after selling:", user.balance)
            user = User.query.get(user_id)
            # actualise les number of stocks
            new_stock_portfolio[stock_name] -= number_of_stocks

            # on cactualise la db
            user.stock_portfolio = new_stock_portfolio
            # Commit changes to the database after making all updates
            db.session.commit()

            print("user.stock_portfolio after purchase:", user.stock_portfolio)

            flash(
                f"Vente réussie! Tu as vendu {number_of_stocks} actions de {stock_name} cotées {stock_price}€ pour un total de {number_of_stocks * stock_price}€ "
            )
            return render_template(
                "actions.html",
                username=user.username,
                balance=round(user.balance, 2),
                stock_portfolio=user.stock_portfolio,
                real_user=user,
            )

        else:
            flash(
                f"Nombre d'actions dans le portefeuille insuffisant pour vendre ce nombre d'actions."
            )
            return render_template(
                "actions.html",
                username=user.username,
                balance=round(user.balance, 2),
                stock_portfolio=user.stock_portfolio,
                real_user=user,
            )
    return redirect(url_for("login"))


import copy

from copy import deepcopy


@app.route("/sell_european_option", methods=["POST"])
def sell_european_option():
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        user = User.query.get(user_id)

        option_name = request.form.get("option_name_sell_eur")
        number_of_option_eur = int(request.form.get("number_of_option_sell_eur"))
        K = int(request.form.get("K_sell_eur"))
        T = int(request.form.get("T_sell_eur"))
        sigma = prix_de_cloture_passé(option_name)

        new_european_option_portfolio = deepcopy(user.european_option_portfolio)

        print(option_name, K, T)

        if not option_name:
            return "Invalid stock name."

        sport_price = prix_actuelle(option_name)
        option_price = Black_Scholes(sport_price, K, 0.05, T, sigma)

        if option_name in new_european_option_portfolio.keys():
            if str(K) in (new_european_option_portfolio[option_name]).keys():
                if str(T) in new_european_option_portfolio[option_name][str(K)].keys():
                    if (
                        new_european_option_portfolio[option_name][str(K)][str(T)]
                        >= number_of_option_eur
                    ):
                        user.balance += number_of_option_eur * option_price
                        print("user.balance after selling:", user.balance)
                        user = User.query.get(user_id)
                        new_european_option_portfolio[option_name][str(K)][
                            str(T)
                        ] -= number_of_option_eur
                        user.european_option_portfolio = new_european_option_portfolio
                        db.session.commit()
                        print(
                            "user.european_option_portfolio after selling:",
                            user.european_option_portfolio,
                        )
                        flash(
                            f"Achat réussi! Tu as vendu {number_of_option_eur} actions de {option_name} cotées {option_price}€ pour un total de {number_of_option_eur * option_price}€ "
                        )
                        return render_template(
                            "european.html",
                            username=user.username,
                            balance=user.balance,
                            european_option_portfolio=user.european_option_portfolio,
                            real_user=user,
                        )
                    else:
                        flash(f"Pas assez d'options dans ton portefeuille pour vendre.")
                else:
                    flash("Invalid value for T.")
            else:
                flash("Invalid value for K.")
        else:
            flash("Stock not found in the portfolio.")

        return render_template(
            "european.html",
            username=user.username,
            balance=round(user.balance, 2),
            european_option_portfolio=user.european_option_portfolio,
            real_user=user,
        )

    return redirect(url_for("login"))


@app.route("/buy_european_option", methods=["POST"])
def buy_european_option():
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        user = User.query.get(user_id)

        option_name = request.form.get("option_name_buy_eur")
        number_of_option_eur_str = request.form.get("number_of_option_buy_eur")

        K = int(request.form.get("K_buy_eur"))
        T = int(request.form.get("T_buy_eur"))
        sigma = prix_de_cloture_passé(option_name)

        new_european_option_portfolio = copy.deepcopy(user.european_option_portfolio)

        print(option_name)
        if not option_name:
            flash("Invalid option name.")
            return redirect(
                url_for("your_redirect_route")
            )  # Adjust this to your actual redirect route

        if number_of_option_eur_str is not None:
            try:
                number_of_option_eur = int(number_of_option_eur_str)

                sport_price = prix_actuelle(option_name)
                option_price = Black_Scholes(sport_price, K, 0.05, T, sigma)

                print("option_price = ", option_price)

                if user.balance >= number_of_option_eur * option_price:
                    user.balance -= number_of_option_eur * option_price
                    print("user.balance after purchase:", user.balance)

                    # Check if the option_name exists in the portfolio
                    if option_name in new_european_option_portfolio:
                        # Check if K exists for the option_name
                        if K in new_european_option_portfolio[option_name]:
                            # Check if T exists for the option_name and K
                            if T in new_european_option_portfolio[option_name][K]:
                                new_european_option_portfolio[option_name][K][
                                    T
                                ] += number_of_option_eur
                            else:
                                new_european_option_portfolio[option_name][K][
                                    T
                                ] = number_of_option_eur
                        else:
                            new_european_option_portfolio[option_name][K] = {
                                T: number_of_option_eur
                            }
                    else:
                        new_european_option_portfolio[option_name] = {
                            K: {T: number_of_option_eur}
                        }

                    user.european_option_portfolio = new_european_option_portfolio
                    db.session.commit()

                    print(
                        "user.european_option_portfolio after purchase:",
                        user.european_option_portfolio,
                    )

                    flash(
                        f"Achat réussi! Tu as acheté {number_of_option_eur} options de {option_name} cotées {option_price}€ pour un total de {number_of_option_eur * option_price}€ "
                    )
                    return render_template(
                        "european.html",
                        username=user.username,
                        balance=round(user.balance, 2),
                        european_option_portfolio=user.european_option_portfolio,
                        real_user=user,
                    )
                else:
                    flash("Solde insuffisant pour acheter ces options.")
                    return render_template(
                        "european.html",
                        username=user.username,
                        balance=round(user.balance, 2),
                        european_option_portfolio=user.european_option_portfolio,
                        real_user=user,
                    )
            except ValueError:
                flash(
                    "Invalid input for the number of american options. Please enter a valid number."
                )
                return redirect(
                    url_for("your_redirect_route")
                )  # Adjust this to your actual redirect route
        else:
            flash(
                "The number of american options is not provided. Please enter a valid number."
            )
            return redirect(
                url_for("your_redirect_route")
            )  # Adjust this to your actual redirect route
    return redirect(url_for("login"))


@app.route("/sell_american_option", methods=["POST"])
def sell_american_option():
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        user = User.query.get(user_id)

        option_name = request.form.get("option_name_sell_am")
        number_of_option_am = int(request.form.get("number_of_option_sell_am"))
        K = int(request.form.get("K_sell_am"))
        T = int(request.form.get("T_sell_am"))
        sigma = prix_de_cloture_passé(option_name)

        new_american_option_portfolio = deepcopy(user.american_option_portfolio)

        print(option_name, K, T)

        if not option_name:
            return "Invalid stock name."

        sport_price = prix_actuelle(option_name)
        option_price = Black_Scholes(sport_price, K, 0.05, T, sigma)

        # print('option_price = ', option_price)
        # print('portfolioofdsin', new_american_option_portfolio['AAPL']['200'].keys())

        if option_name in new_american_option_portfolio.keys():
            if str(K) in (new_american_option_portfolio[option_name]).keys():
                if str(T) in new_american_option_portfolio[option_name][str(K)].keys():
                    if (
                        new_american_option_portfolio[option_name][str(K)][str(T)]
                        >= number_of_option_am
                    ):
                        user.balance += number_of_option_am * option_price
                        print("user.balance after selling:", user.balance)
                        user = User.query.get(user_id)
                        new_american_option_portfolio[option_name][str(K)][
                            str(T)
                        ] -= number_of_option_am
                        user.american_option_portfolio = new_american_option_portfolio
                        db.session.commit()
                        print(
                            "user.american_option_portfolio after selling:",
                            user.american_option_portfolio,
                        )
                        flash(
                            f"Achat réussi! Tu as vendu {number_of_option_am} actions de {option_name} cotées {option_price}€ pour un total de {number_of_option_am * option_price}€ "
                        )
                        return render_template(
                            "american.html",
                            username=user.username,
                            balance=user.balance,
                            american_option_portfolio=user.american_option_portfolio,
                            real_user=user,
                        )
                    else:
                        flash(f"Pas assez d'options dans ton portefeuille pour vendre.")
                else:
                    flash("Invalid value for T.")
            else:
                flash("Invalid value for K.")
        else:
            flash("Stock not found in the portfolio.")

        return render_template(
            "american.html",
            username=user.username,
            balance=round(user.balance, 2),
            american_option_portfolio=user.american_option_portfolio,
            real_user=user,
        )

    return redirect(url_for("login"))


# @app.route('/sell_european_option', methods=['POST'])
# def sell_european_option():
#     if 'user_id' in session:
#         user_id = session['user_id']
#         print(user_id)
#         user = User.query.get(user_id)

#         option_name = request.form.get('option_name_sell_eur')
#         number_of_option_eur= int(request.form.get('number_of_option_sell_eur'))

#         K = int(request.form.get('K_sell_eur'))
#         T = int(request.form.get('T_sell_eur'))
#         sigma = prix_de_cloture_passé(option_name)

#         new_european_option_portfolio = user.european_option_portfolio.copy()
#         # Get the stock name and validate it (you may add additional validation)

#         print(option_name)
#         if not option_name:
#             return "Invalid stock name."

#         # Get the current price of the stock using the prix_actuelle function

#         sport_price= prix_actuelle(option_name)
#         option_price= Black_Scholes(sport_price,K,0.05,T,sigma)

#         print('option_price = ', option_price)


#         if option_name in user.european_option_portfolio and new_european_option_portfolio[option_name]>=number_of_option_eur:
#             user.balance += number_of_option_eur * option_price
#             print('user.balance after selling:', user.balance)
#             user = User.query.get(user_id)
#             #actualise les number of stocks
#             new_european_option_portfolio[option_name] -= number_of_option_eur

#             #on cactualise la db
#             user.european_option_portfolio = new_european_option_portfolio
#             # Commit changes to the database after making all updates
#             db.session.commit()

#             print('user.stock_portfolio after purchase:', user.european_option_portfolio)

#             flash(f"Achat réussi! Tu as vendu {number_of_option_eur} actions de {option_name} cotées {option_price}€ pour un total de {number_of_option_eur * option_price}€ ")
#             return render_template('european.html', username=user.username, balance=user.balance, european_option_portfolio=user.european_option_portfolio, real_user=user)

#         else:
#             flash(f"pas assez d'options dans ton portefeuille.")
#             return render_template('european.html', username=user.username, balance=user.balance, european_option_portfolio=user.european_option_portfolio, real_user=user)
#     return redirect(url_for('login'))


@app.route("/sell_american_option", methods=["POST"])
def sell_ammerican_option():
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        user = User.query.get(user_id)

        option_name = request.form.get("option_name_sell_am")
        number_of_option_am = int(request.form.get("number_of_option_sell_am"))

        K = int(request.form.get("K_sell_am"))
        T = int(request.form.get("T_sell_am"))
        sigma = prix_de_cloture_passé(option_name)

        new_american_option_portfolio = copy.deepcopy(user.american_option_portfolio)

        print(option_name)
        if not option_name:
            flash("Invalid option name.")
            return redirect(
                url_for("your_redirect_route")
            )  # Adjust this to your actual redirect route

        if number_of_option_am is not None:
            try:
                number_of_option_am = int(number_of_option_am)

                sport_price = prix_actuelle(option_name)
                option_price = american_call_option_price(
                    sport_price, K, 0.05, T, sigma, 100
                )

                print("option_price = ", option_price)

                if user.balance >= number_of_option_am * option_price:
                    user.balance -= number_of_option_am * option_price
                    print("user.balance after purchase:", user.balance)

                    # Check if the option_name exists in the portfolio
                    if option_name in new_american_option_portfolio:
                        # Check if K exists for the option_name
                        if K in new_american_option_portfolio[option_name]:
                            # Check if T exists for the option_name and K
                            if T in new_american_option_portfolio[option_name][K]:
                                new_american_option_portfolio[option_name][K][
                                    T
                                ] += number_of_option_am
                            else:
                                new_american_option_portfolio[option_name][K][
                                    T
                                ] = number_of_option_am
                        else:
                            new_american_option_portfolio[option_name][K] = {
                                T: number_of_option_am
                            }
                    else:
                        new_american_option_portfolio[option_name] = {
                            K: {T: number_of_option_am}
                        }

                    user.american_option_portfolio = new_american_option_portfolio
                    db.session.commit()

                    print(
                        "user.american_option_portfolio after purchase:",
                        user.american_option_portfolio,
                    )

                    flash(
                        f"Achat réussi! Tu as acheté {number_of_option_am} options de {option_name} cotées {option_price}€ pour un total de {number_of_option_am * option_price}€ "
                    )
                    return render_template(
                        "american.html",
                        username=user.username,
                        balance=round(user.balance, 2),
                        american_option_portfolio=user.american_option_portfolio,
                        real_user=user,
                    )
                else:
                    flash("Solde insuffisant pour acheter ces options.")
                    return render_template(
                        "american.html",
                        username=user.username,
                        balance=round(user.balance, 2),
                        american_option_portfolio=user.american_option_portfolio,
                        real_user=user,
                    )
            except ValueError:
                flash(
                    "Invalid input for the number of American options. Please enter a valid number."
                )
                return redirect(
                    url_for("your_redirect_route")
                )  # Adjust this to your actual redirect route
        else:
            flash(
                "The number of American options is not provided. Please enter a valid number."
            )
            return redirect(
                url_for("your_redirect_route")
            )  # Adjust this to your actual redirect route
    return redirect(url_for("login"))


@app.route("/buy_american_option", methods=["POST"])
def buy_american_option():
    if "user_id" in session:
        user_id = session["user_id"]
        print(user_id)
        user = User.query.get(user_id)

        option_name = request.form.get("option_name_buy_am")
        number_of_option_am_str = request.form.get("number_of_option_buy_am")

        K = int(request.form.get("K_buy_am"))
        T = int(request.form.get("T_buy_am"))
        sigma = prix_de_cloture_passé(option_name)

        new_american_option_portfolio = copy.deepcopy(user.american_option_portfolio)

        print(option_name)
        if not option_name:
            flash("Invalid option name.")
            return redirect(
                url_for("your_redirect_route")
            )  # Adjust this to your actual redirect route

        if number_of_option_am_str is not None:
            try:
                number_of_option_am = int(number_of_option_am_str)

                sport_price = prix_actuelle(option_name)
                option_price = american_call_option_price(
                    sport_price, K, 0.05, T, sigma, 100
                )

                print("option_price = ", option_price)

                if user.balance >= number_of_option_am * option_price:
                    user.balance -= number_of_option_am * option_price
                    print("user.balance after purchase:", user.balance)

                    # Check if the option_name exists in the portfolio
                    if option_name in new_american_option_portfolio:
                        # Check if K exists for the option_name
                        if K in new_american_option_portfolio[option_name]:
                            # Check if T exists for the option_name and K
                            if T in new_american_option_portfolio[option_name][K]:
                                new_american_option_portfolio[option_name][K][
                                    T
                                ] += number_of_option_am
                            else:
                                new_american_option_portfolio[option_name][K][
                                    T
                                ] = number_of_option_am
                        else:
                            new_american_option_portfolio[option_name][K] = {
                                T: number_of_option_am
                            }
                    else:
                        new_american_option_portfolio[option_name] = {
                            K: {T: number_of_option_am}
                        }

                    user.american_option_portfolio = new_american_option_portfolio
                    db.session.commit()

                    print(
                        "user.american_option_portfolio after purchase:",
                        user.american_option_portfolio,
                    )

                    flash(
                        f"Achat réussi! Tu as acheté {number_of_option_am} options de {option_name} cotées {option_price}€ pour un total de {number_of_option_am * option_price}€ "
                    )
                    return render_template(
                        "american.html",
                        username=user.username,
                        balance=round(user.balance, 2),
                        american_option_portfolio=user.american_option_portfolio,
                        real_user=user,
                    )
                else:
                    flash("Solde insuffisant pour acheter ces options.")
                    return render_template(
                        "american.html",
                        username=user.username,
                        balance=round(user.balance, 2),
                        american_option_portfolio=user.american_option_portfolio,
                        real_user=user,
                    )
            except ValueError:
                flash(
                    "Invalid input for the number of american options. Please enter a valid number."
                )
                return redirect(
                    url_for("your_redirect_route")
                )  # Adjust this to your actual redirect route
        else:
            flash(
                "The number of american options is not provided. Please enter a valid number."
            )
            return redirect(
                url_for("your_redirect_route")
            )  # Adjust this to your actual redirect route
    return redirect(url_for("login"))


@app.route("/add_money", methods=["POST"])
def add_money():
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)

        # Get the amount to add and validate it (you may add additional validation)
        amount_to_add = request.form.get("amount")
        if not amount_to_add:
            return "Invalid amount."

        # Add the amount to the user's balance
        user.balance += float(amount_to_add)

        # Commit changes to the database
        db.session.commit()

        list_valeur_par_action = {}
        tot_portfolio = 0
        if user:
            portfolio_value = user.stock_portfolio
            for cle, valeur in portfolio_value.items():
                if type(cle) == str:
                    try:
                        prix = prix_actuelle(str(cle))
                        list_valeur_par_action[cle] = prix * portfolio_value[cle]
                        tot_portfolio += prix

                    except ValueError:
                        flash("cle not a str in index_route")
                        return redirect(url_for("login"))
        else:
            flash("User not found.")
            return redirect(url_for("login"))

        flash(f"Montant ajouté avec succès! Nouveau solde: {user.balance} euros.")
        return render_template(
            "index.html",
            list_valeur_par_action=list_valeur_par_action,
            tot_portfolio=round(tot_portfolio, 2),
            username=user.username,
            balance=round(user.balance, 2),
            stock_portfolio=user.stock_portfolio,
            real_user=user,
        )

    return redirect(url_for("login"))


@app.route("/")
def index():
    if "user_id" in session:
        # Retrieve the user's information from the database
        user_id = session["user_id"]
        user = User.query.get(user_id)

        list_valeur_par_action = {}
        tot_portfolio = 0
        if user:
            portfolio_value = user.stock_portfolio
            for cle, valeur in portfolio_value.items():
                if type(cle) == str:
                    try:
                        prix = prix_actuelle(str(cle))
                        list_valeur_par_action[cle] = prix * portfolio_value[cle]
                        tot_portfolio += prix

                    except ValueError:
                        flash("cle not a str in index_route")
                        return redirect(url_for("login"))
        else:
            flash("User not found.")
            return redirect(url_for("login"))

        # Render the template with the portfolio value
        return render_template(
            "index.html",
            list_valeur_par_action=list_valeur_par_action,
            tot_portfolio=round(tot_portfolio, 2),
            username=user.username,
            balance=round(user.balance, 2),
            portfolio_value=portfolio_value,
            stock_portfolio=user.stock_portfolio,
            real_user=user,
        )
    else:
        return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Cet utilisateur existe déjà !"

        # Créer un nouvel utilisateur
        new_user = User(username=username, password=password, balance=500)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            return redirect(url_for("index"))

        return "Identifiant ou mot de passe incorrect."

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


####ajout de yentl
@app.route("/actions")
def actions():
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
    return render_template(
        "actions.html",
        username=user.username,
        balance=user.balance,
        stock_portfolio=user.stock_portfolio,
        real_user=user,
    )


#####fin ajout
@app.route("/pricer")
def pricer():
    return render_template("pricer.html")


@app.route("/about_us")
def about_us():
    return render_template("about_us.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    file.save(
        os.path.join(os.path.expanduser("~/Desktop/hackaton flask"), file.filename)
    )
    return {"success": True}


@app.route("/stock_data/<symbol>/<Nom_Symbol>")
def stock_data(symbol, Nom_Symbol):
    if Nom_Symbol == "Nom":
        Real_Symbol = nom_marque_to_symbol(symbol)
    else:
        Real_Symbol = symbol
    # Code pour récupérer les données du cours de l'action
    L, V = plot_yesterday_stock(Real_Symbol)
    stock_data = {
        "labels": L,
        "values": V,
    }
    return jsonify(stock_data)


@app.route("/choix_option", methods=["POST"])
def choix_option():
    option = request.form["option"]

    if option == "americaine":
        return redirect(url_for("american"))
    elif option == "europenne":
        return redirect(url_for("european"))


@app.route("/american")
def american():
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
    return render_template(
        "american.html",
        username=user.username,
        balance=user.balance,
        american_option_portfolio=user.american_option_portfolio,
        real_user=user,
    )


@app.route("/european")
def european():
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
    return render_template(
        "european.html",
        username=user.username,
        balance=user.balance,
        european_option_portfolio=user.european_option_portfolio,
        real_user=user,
    )


from formule import Black_Scholes, american_call_option_price, monte_carlo_american_call
from src.financeProg import prix_de_cloture_passé, symbol, key, prix_actuelle


@app.route("/prix_americain_buy/<Echeance>/<Nom>/<Prix>")
def resultat_americaine_buy(Echeance, Nom, Prix):
    K = int(Prix)
    r = 0.05
    T = int(Echeance)

    stock_name = Nom

    S0 = prix_actuelle(stock_name)
    print("S0 =", S0)
    sigma = prix_de_cloture_passé(stock_name)
    resultat_americaine = round(american_call_option_price(S0, K, r, T, sigma, 300), 1)
    print("resultat")
    print(resultat_americaine)

    return jsonify(resultat_americaine=resultat_americaine)


@app.route("/prix_americain_sell/<Echeance>/<Nom>/<Prix>")
def resultat_americaine_sell(Echeance, Nom, Prix):
    K = int(Prix)
    r = 0.05
    T = int(Echeance)

    stock_name = Nom

    S0 = prix_actuelle(stock_name)
    print("S0 =", S0)
    sigma = prix_de_cloture_passé(stock_name)
    resultat_americaine = round(american_call_option_price(S0, K, r, T, sigma, 300), 1)
    print("resultat")
    print(resultat_americaine)

    return jsonify(resultat_americaine=resultat_americaine)


@app.route("/prix_européen_buy/<Echeance>/<Nom>/<Prix>")
def resultat_europeen_buy(Echeance, Nom, Prix):
    K = int(Prix)
    r = 0.05
    T = int(Echeance)

    stock_name = Nom

    S0 = prix_actuelle(stock_name)
    print("S0 =", S0)
    sigma = prix_de_cloture_passé(stock_name)
    resultat_euro = round(Black_Scholes(S0, K, r, T, sigma), 1)
    print("resultat")
    print(resultat_euro)

    return jsonify(resultat_euro=resultat_euro)


@app.route("/prix_européen_sell/<Echeance>/<Nom>/<Prix>")
def resultat_europeen_sell(Echeance, Nom, Prix):
    K = int(Prix)
    r = 0.05
    T = int(Echeance)

    stock_name = Nom

    S0 = prix_actuelle(stock_name)
    print("S0 =", S0)
    sigma = prix_de_cloture_passé(stock_name)
    resultat_euro = round(Black_Scholes(S0, K, r, T, sigma), 1)
    print("resultat")
    print(resultat_euro)

    return jsonify(resultat_euro=resultat_euro)


file_path = "nouveau_actions.txt"

with open(file_path, "r") as file:
    stocks_data = [line.strip().split(": ") for line in file]

stocks = [stocks_data[i][1] for i in range(len(stocks_data))]
noms = [stocks_data[i][0] for i in range(len(stocks_data))]

noms.append("")
stocks.append("")


@app.route("/get_stock_suggestions")
def get_stock_suggestions():
    input_prefix = request.args.get("input", "").lower()

    # Filter stocks based on input prefix
    suggestion = []
    for i in stocks:
        if i.lower().startswith(input_prefix):
            suggestion.append(i)
    return jsonify(suggestion)


@app.route("/get_stock_suggestions_noms")
def get_stock_suggestions_noms():
    input_prefix = request.args.get("input", "").lower()

    # Filter stocks based on input prefix
    suggestion = []
    for i in noms:
        if i.lower().startswith(input_prefix):
            suggestion.append(i)
    return jsonify(suggestion)


@app.route("/get_stock_suggestions_noms_buy")
def get_stock_suggestions_noms_buy():
    input_prefix = request.args.get("input", "").lower()

    # Filter stocks based on input prefix
    suggestion = []
    for i in noms:
        if i.lower().startswith(input_prefix):
            suggestion.append(i)
    return jsonify(suggestion)


if __name__ == "_main_":
    app.run(debug=True)
