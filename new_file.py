from random import randint, random
from sqlite3 import *
import time
from core import Core
from Session_class import Seance
from constants import date_it
def random_unit():
    return randint(1, 3)

def random_date():
    return str(randint(2015, 2020))+"-"+str(randint(1, 12))+"-"+str(randint(1, 28))


def random_patient_id():
    db = connect("database.db")
    cr = db.cursor()
    cr.execute("select ID from Patients")
    result = cr.fetchall()
    return result[randint(0, len(result)-1)][0]

def random_medicament():
    return randint(0, 1000)

def random_unite():
    return randint(1, 3)

def randodm_poids():
    return (random()*1000)//100 + 30

def random_review():
    chars = "abcdefghijklmnopqrstuvwxyz.,;0123456789 \n"
    res = ""
    for i in range(100):
        res += chars[randint(0, 40)]
    return res

def random_name():
    chars = "abcdefghijklmnopqrstuvwxyz"
    res = ""
    for i in range(100):
        res += chars[randint(0, 25)]
    return res

c = Core()
t = time.time()
for i in range(150):
    print(i)
    s = [i, random_patient_id(), randodm_poids(),
        random_unite(), random_date(), randint(1, 2), str(random_medicament())]
    c._ADD_SESSION(*s, True, "")
    c._ADD_TEST(i, random_patient_id(), random_date(), random_review(), random_name())
print(time.time() - t)