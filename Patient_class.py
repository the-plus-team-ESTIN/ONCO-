#Include modules
import datetime as dt
from constants import date_it
#Patient class is the class that takes all patient data.

class Patient :
    def __init__(self, ID, nom, prenom, date_naissance, sexe, 
    pathologies, Numero_Telephone, Alternatif_Telephone, unite,
    date_entree, groupage, rh, poids, taille, Commune, Wilaya, radiothérapie=False, debut=None, fin=None) :
        #ID is unique for patients
        self.ID:int = ID

        #Main patient information
        self.nom:str = nom
        self.prenom:str = prenom
        self.date_naissance:dt.date = date_naissance
        self.sexe:int = sexe #1: masculin, 0 feminin
        self.commune:str = Commune
        self.wilaya:int = Wilaya

        #communication data
        self.tel_patient:str = Numero_Telephone
        self.tel_alt:str = Alternatif_Telephone

        #Cancer data
        #nothing differs when changing types
        #we can use list and store it as string
        self.pathologies:str = pathologies  

        #hospital data
        self.unite:int = unite # 1, 2, 3. Names coming later
        self.date_entree = date_entree
        self.radiotherapie = radiothérapie
        self.debut = debut
        self.fin = fin
        
        #More data
        self.groupage:int = groupage #O A B AB -> 0 1 2 3
        self.rh:int = rh #1 + , 0 -
        self.poids:float = poids
        self.taille:int = taille#cm

    def AGE(self): #parametre :date de naissence
        today = dt.date.today()
        delta = today - date_it(self.date_naissance)
        return delta.days//365

    def SEXE(self):
        return ["Homme", "Femme"][self.sexe]
    
    def UNITE(self):
        return ["Thoracique", "Gynécologie", "Digestive"][self.unite-1]
    
    def TYPE_SANGUIN(self):
        return (["O", "A", "B", "AB"][self.groupage],"+-"[self.rh])
