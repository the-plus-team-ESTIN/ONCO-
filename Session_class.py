from random import randint

from sympy import det


class Seance:
    def __init__(self, ID, ID_patient, poids, unite, date, type, medicament="", sceance_faite=False, details=""):

        self.ID:int = ID
        self.ID_patient:int = ID_patient
        self.poids:float = poids
        self.unite:int = unite
        self.date_seance:date = date
        self.type_traitement:int = type
        self.medicament:str = medicament
        self.seance_faite:bool = sceance_faite
        self.details:str = details

    def TYPE_TRAITEMENT(self):
        return ["Chimiothérapie/Traitement", "Controle/Consultation"][self.type_traitement-1]
    
    def SEANCE_FAITE(self):
        return["Faite", "Non faite"][self.seance_faite]

    def UNITE(self):
        return ["Thoracique", "Gynécologie", "Digestive"][self.unite-1]