import datetime
from random import randint, random
import sqlite3
from datetime import date
from core import Core
import time

def random_name():
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    l = randint(4, 10)
    s = ""
    for _ in range(l):
        s += alphabet[randint(0, 25)]
    return s

def random_weight():
    return round(random()*100, 2) + 30

def random_height():
    return int(random()*100+100)

def random_birth_date():
    return str(randint(950, 1022)+1000)+"-"+str(randint(1, 12))+"-"+str(randint(1, 28))

def random_wilaya():
    l = randint(1, 58)
    return l
    
def random_commune():
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    l = randint(4, 10)
    s = ""
    for j in range(l):
        s += alphabet[randint(0, 25)]
    return s

def random_unit():
    return randint(1, 3)

def random_date():
    return str(randint(0, 22)+2000)+"-"+str(randint(1, 12))+"-"+str(randint(1, 28))

def random_pathology():
    i = randint(1, 4)
    pat = str(randint(1, 200))
    for _ in range(i):
        pat = pat +  "/" + str(randint(1, 200))
    return pat

def random_blood():
    return randint(0, 3)

def random_rh():
    return randint(0,1)

def random_entry_date():
    l = [1]*50+[0]
    if l[randint(0, 50)]:
        return str(randint(0, 22)+2008)+"-"+str(randint(1, 12))+"-"+str(randint(1, 28))
    else:
        return datetime.date.today().isoformat()

def random_tel():
    tel = "0"
    for i in range(9):
        tel += str(randint(0,9))
    return tel 

def random_sex():
    return randint(0, 1)

def new_patient(id):
    nom = random_name().upper()
    prenom = random_name().lower()
    sexe = random_sex()
    pathologie = random_pathology()
    unite = random_unit()
    wilaya = random_wilaya()
    commune = random_commune()
    groupage = random_blood()
    rh = random_rh()
    poids  = random_weight()
    taille = random_height()
    tel = random_tel()
    tel_alt = random_tel()
    naissance = list(map(int, random_birth_date().split("-")))

    d_naissance = date(naissance[0], naissance[1], naissance[2])
    entree = list(map(int, random_entry_date().split("-")))
    d_entree = date(entree[0], entree[1], entree[2])
    Id = str(id)+ str(entree[0])[2:]
    
    program._ADD_PATIENT(Id, nom, prenom, d_naissance, sexe, pathologie, unite, groupage, rh, poids, taille, tel, tel_alt, commune, wilaya,0, "", "", d_entree)

if __name__ == "__main__":
    t = time.time()
    program = Core()
    db  = sqlite3.connect("database.db")
    cr = db.cursor()

    for i in range(50):
        print(i)
        new_patient(i+1)
    print(time.time()-t)
    db.commit()
    db.close()
    import new_file