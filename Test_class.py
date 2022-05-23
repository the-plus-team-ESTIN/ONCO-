class Test:
    def __init__(self, ID, ID_patient, date, details, type):
        self.ID:int = ID
        self.ID_patient:int = ID_patient
        self.date_test:date = date
        #details peuvent englober le type et l'etablissement
        self.details:str = details
        self.type:str = type#???
