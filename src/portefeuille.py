from financeProg import *


class Porte_feuille:
    def __init__(self, user, argent):
        self.action_detenu = (
            {}
        )  # dictionnaire avec l'action en clé et le nbre d'action détenus
        self.action_achat = (
            {}
        )  # dictionnaire de l'argent investi dans une action mise a jour avec la vente de l'action
        self.__argent_investi = argent  # argent mis dans le prote feuille au total
        self.__argent = argent  # argent disponible liquidité
        self.user = user

    def get_argent(self):
        return self.__argent

    def update_portfolio_in_db(self):
        from main import db

        # Update the user's portfolio information in the database
        self.user.update_portfolio(self)
        db.session.commit()

    def acheter_action(self, symbol, nombre):
        if self.__argent - prix_actuelle(symbol) * nombre < 0:
            print("achat impossible")
            return "pas assez d'argent pour acheter"
        self.__argent = self.__argent - prix_actuelle(symbol) * nombre

        if symbol in self.action_detenu:
            self.action_detenu[symbol] += nombre
            self.action_achat[symbol] += prix_actuelle(symbol) * nombre
        else:
            self.action_detenu[symbol] = nombre
            self.action_achat[symbol] = prix_actuelle(symbol) * nombre

        self.update_portfolio_in_db()

    def vendre_action(self, symbol, nombre):
        if symbol in self.action_detenu:
            if self.action_detenu[symbol] < nombre:
                return "vous vendez plus d'action que ce que vous en posséder"
            self.__argent = self.__argent + prix_actuelle(symbol) * nombre
            self.action_achat[symbol] -= prix_actuelle(symbol) * nombre
            self.action_detenu[symbol] -= nombre

            self.update_portfolio_in_db()

    def valorisation(self):
        # renvoi la valeur du portefeuille
        valo = 0
        for element in self.action_detenu:
            valo += prix_actuelle(element) * self.action_detenu[element]
        return valo

    def ajouter_argent(self, monnaie):
        self.__argent += monnaie
        self.__argent_investi += monnaie

    def retirer_argent(self, montant):
        self.__argent -= montant
        self.__argent_investi -= montant

    def gain_ou_perte_total(self):
        # renvoi vraie si le portefeuille en positive et faux sinon
        return self.valorisation() > self.__argent_investi

    def gain_ou_perte_action(self, symbol):
        # renvoi vraie si on a gagne de l'argent en achetant cette actions meme si les actions sont acheter a des dates differentes
        return self.action_achat[symbol] < prix_actuelle(symbol) * self.action[symbol]

    def afficher_portefeuille(self):
        print("Actions dans le portefeuille :")
        for action, quantite in self.action_detenu.items():
            print(f"{action}: {quantite}")
        print(f"Argent disponible : {self.__argent}€")

    ##sert pour afficher la composition du portefeuille
    def get_owned_stocks(self):
        return list(self.action_detenu.keys())

    ##ajout pour lier à la database


# test
# mon_portefeuille = Porte_feuille(1000)

# Achat d'actions
# mon_portefeuille.acheter_action('AAPL', 10)
# mon_portefeuille.acheter_action('GOOGL', 5)
# mon_portefeuille.acheter_action('AAPL', 5)

# Vente d'actions
# mon_portefeuille.vendre_action('AAPL', 8)
# mon_portefeuille.vendre_action('GOOGL', 3)
# mon_portefeuille.vendre_action('MSFT', 5)  # Tentative de vente d'une action non détenue

# Affichage du portefeuille
# mon_portefeuille.afficher_portefeuille()
