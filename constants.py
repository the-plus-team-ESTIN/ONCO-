import datetime as dt
"""
Here you find all the constants
that the program is in need for
"""

#ROOT username and password (used for initialising database)
_ROOT_ID = "admin"
_PASSWORD = "admin"

#main program elements
_MEDECIN = None
_PATIENT = None
_SEANCE = None
_TEST = None

#useful file paths
_DATA_BASE = "database.db"
_CONSTANT_FILE = "constants"

#IDs generators
_PATIENT_ID = 0
_DOCTOR_ID = 0
_SEANCE_ID = 0
_TEST_ID = 0
_YEAR = None

#lists for fetched data from database
_PATIENT_LIST = []
_DOCTOR_LIST = []
_SESSION_LIST = []
_TEST_LIST = []

def date_it(prmptr):
    date_entre_patient = list(map(int, prmptr.split("-")))
    return dt.date(date_entre_patient[0], date_entre_patient[1], date_entre_patient[2])
def convert(lst):
    res = ""
    for l in lst:
        res += l
    return res