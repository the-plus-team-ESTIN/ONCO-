class Medecin :
    def __init__(self, ID=None, nom=None, prenom=None, grade=None, 
    unite=None, num_tele=None, nom_utilisateur=None, mdp=None):
        self.ID:int = ID#unique
        self.nom:str = nom
        self.prenom:str = prenom
        self.nom_utilisateur:str = nom_utilisateur#unique, tester s'il existe dans la base de données
        self.num_tele:str = num_tele
        self.unite:int = unite#1, 2, 3
        self.grade:int = grade# 0:Chef de service, 1:generaliste, 2:spécialiste
        self.mdp:str = mdp#plus de 5 caractères

    def GRADE(self):
        return ["Chef de service/ Administrateur", "Spécialiste", "Géneraliste"][int(self.grade)-1]

    def UNITE(self):
        return ["Thoracique", "Gynécologie", "Digestive"][self.unite-1]

    def __eq__(self, __o: object) -> bool:
        return self.ID == __o.ID if __o != None else False

        