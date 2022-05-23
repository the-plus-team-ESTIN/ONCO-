#import Modules
import sqlite3
import datetime as dt
from Doctor_class import Medecin
from Patient_class import Patient
from Session_class import Seance
from Test_class import Test
from filler import import_formes, import_medicaments, import_pathologies, import_wilayas
from constants import _DATA_BASE, _MEDECIN, _PATIENT, _SEANCE, _TEST, _ROOT_ID, _PASSWORD, _PATIENT_LIST, _DOCTOR_ID,_SESSION_LIST,_TEST_LIST,date_it

import datetime as dt

#Core class is the interfacing class with the datatbase.
#it takes input from interface then processes it. 

class Core:
	def _INIT_DB(self):
		
		"""
			This function is used to create the database tables that do not exist
		"""

		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instruction_set = [
			"create table if not exists Medecin(ID integer, nom text, prenom text, grade Integer, unite Integer, num_tele text, nom_utilisateur text)",

			"create table if not exists MotDePasse(ID integer, mot_de_passe text)",

			"create table if not exists Patients(ID integer, Nom text, Prénom text, Date_De_Naissance date, Sexe integer, Pathologies text, Numero_Telephone text, Alternatif_Telephone text, Unite integer, Date_Entree date, Groupage integer, rh integer, Poids decimal(3, 5), Taille integer, Commune text, Wilaya integer, radiothérapie integer, debut date, fin date)",
			
			"create table if not exists Seances(ID Integer, Id_patient Integer, Poids decimal(2), unite Integer, date_seance date, type integer, medicament text, seance_faite integer, details text)",
			
			"create table if not exists Testes(ID Integer, Id_patient integer, type text, date_test date,  details text)",

			"create table if not exists Medicaments(ID integer, libelle text, forme integer)",

			"create table if not exists Formes(ID integer, libelle text, sigle text, dosage text, unite text)"
			
			]
		
		for i in instruction_set:
			#print(i)
			cr.execute(i)
		
		import_medicaments()
		import_formes()
		import_pathologies()
		import_wilayas()
		db.commit()
		db.close()

	#functions that concern the Doctors
	def _ADD_USER(self, id, nm, prnm, grd, unit, tel, usr, passwd):
		
		#set globals
		global _DATA_BASE
		
		
		if usr == _ROOT_ID:
			return -1#illegal username
		#initialise database
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()
		
		#search for similarities
		cr.execute(f"select count() from Medecin where nom_utilisateur = \"{usr}\" ")
		result = cr.fetchone()
		if result[0]:
			database.close()
			return 1
		#if doctor does not exist then increment 
			
		#add to database
		instruction = f"insert into Medecin(ID , nom , prenom , grade , unite, num_tele  , nom_utilisateur)values({id}, \"{nm}\", \"{prnm}\",{grd}, {unit},\"{tel}\" ,  \"{usr}\")"
		cr.execute(instruction)
		instruction2 = f"insert into MotDePasse(ID, mot_de_passe)values({id}, \"{passwd}\");"
		cr.execute(instruction2)
		database.commit()
		database.close()
		return 0

	def _UPDATE_USER(self, grade="", unite="", tel="", user="", password=""):
		#initialise database
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()
		
		#globals
		global _MEDECIN
		
		#Update values for the signed in account
		if grade:
			_MEDECIN.grade = grade
			#print(_MEDECIN.grade)
		if unite:
			_MEDECIN.unite = unite
			#print(_MEDECIN.unite)
		if tel:
			_MEDECIN.num_tele = tel
		if user:
			_MEDECIN.nom_utilisateur = user
			#print(_MEDECIN.nom_utilisateur)
		if password:
			_MEDECIN.mdp = password
			#print(_MEDECIN.mdp)
		
		#update database
		instruction_set = [
			f"update Medecin set grade = \"{_MEDECIN.grade}\" , unite = \"{_MEDECIN.unite}\" , num_tele = \"{_MEDECIN.num_tele}\" , nom_utilisateur = \"{_MEDECIN.nom_utilisateur}\" , where ID = {_MEDECIN.ID}", 
			f"update MotDePasse set mot_de_passe={_MEDECIN.mdp} where ID={_MEDECIN.ID}"
		]
		for i in instruction_set:
			cr.execute(i)

		database.commit()
		database.close()
		return 0

	def _SIGN_IN(self, user, password):
		
		"""
			Function for signing in the users
			return values <tuples>(<execution result>, <doctor data>): 
			0: success
			1: wrong password
			2: wrong username
		
			-2: database already exists (Admin not allowed to connect)
			-3: database does not exist, Admin password incorrect
			-1: Admin logged in
		
		"""

		#globals
		global _ROOT_ID
		global _PASSWORD

		#connect to database
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		
		#if it's the admin then other things will happen
		#the 'Admin' is only allowed when no

		if (user == _ROOT_ID):
			try:
				cr.execute("select count() from Medecin")
				t = cr.fetchone()
				if t[0]:
					return (-2, None)
				else:
					raise sqlite3.OperationalError

			except sqlite3.OperationalError:
				if password == _PASSWORD:
					return (-1, None)
				else:
					return (-3, None)

		#look for the username
		cr.execute(f"select * from Medecin where nom_utilisateur = \"{user}\" ")
		results = cr.fetchone()
		#if not found then signal that it's wrong
		if results:

			#check password
			cr.execute(f"select * from MotDePasse where ID={results[0]}")
			id_pass = cr.fetchone()

			if id_pass[-1] == password:
		
				#set the signed in account
				return (0, Medecin(*results, id_pass[-1]))
			else:
				#print("wrong password")
				return (1, None)
			
		else:
			#print("wrong username")
			return (2, None)

	def _SIGN_OUT(self):
		#might be removed!!
		#globals
		global _MEDECIN
		#reset _MEDECIN to None 
		_MEDECIN = None
		#return 0 so that the app returns
		return 0

	def _DELETE_USER(self, UserID):
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()
		cr.execute(f"select * from Medecin where ID = {UserID} ")
		results = cr.fetchone()
		if results:
			cr.execute(f"delete from Medecin where ID={UserID} ")
			cr.execute(f"delete from MotDePasse where ID={UserID}")
			database.commit()
			database.close()
			return 1
		else:
			database.close()
			return 0

	#Functions that concern the patients
	def _ADD_PATIENT(self,ID, nom, prenom, date_naissance, sexe, pathologies, unite, groupage, rh, poids, taille, tel, tel_alt, commune, wilaya, radio, debut, fin, date_entree):
		#Globals
		global _DATA_BASE
		
		#initialise database
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select count() from Patients where ID = {ID}")
		result = cr.fetchall()
		if result == []:
			db.close()
			return 1
		
		instruction = f"""insert into Patients (ID, Nom, Prénom, Date_De_Naissance, Sexe, Pathologies, Numero_Telephone, Alternatif_Telephone, Unite, Date_Entree, Groupage, rh, Poids, Taille, Commune, Wilaya, radiothérapie, debut, fin) values({ID},\"{nom}\",\"{prenom}\",\"{date_naissance}\",{sexe},\"{pathologies}\",\"{tel}\",\"{tel_alt}\",{unite},\"{date_entree}\",{groupage},{rh},{poids},{taille},\"{commune}\",{wilaya}, {radio}, \"{debut if radio else ""}\", \"{fin if radio else ""}\");"""
		cr.execute(instruction)
		db.commit()
		db.close()
		return 0

	def _UPDATE_PATEINT(self, ID, tel, tel_alt, wilaya, com, radio,debut, fin, pathologies, unite, poids, taille):
		
		#initialise database
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()

		#Change in the database
		cr.execute(txt:=f"update Patients set Pathologies = \"{pathologies}\" , Unite = {unite} , Poids = {poids} , Taille = {taille},Numero_Telephone = \"{tel}\", Alternatif_Telephone = \"{tel_alt}\", Commune = \"{com}\", Wilaya = {wilaya}, radiothérapie = {radio}, debut = \"{debut}\", fin = \"{fin}\" where ID={ID}")
		#print(txt)
		database.commit()
		database.close()

	def _SHOW_PATIENTS(self, unit=""):
		"""
			This function displays main patient data such as 
			name, age, gender, pathologies...    
		"""
		
		#set globals
		global _PATIENT_LIST
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		
		instruction = f"select * from Patients where Unite={unit if unit else _MEDECIN.unite}"
		cr.execute(instruction)
		results = cr.fetchall()
		#print(results)
		to_return = []
		if not results:
			pass
		else:
			for p in results:
				naissance = list(map(int,p[3].split("-")))
				entree = list(map(int,p[11].split("-")))
				patient = Patient(p[0], p[1], p[2], dt.date(*naissance), p[4], p[5], p[6], p[7], p[8], p[9], p[10], dt.date(*entree))
				to_return.append(patient)
				#print(patient.ID, "\t", patient.prenom, "\t", patient.nom, "\t", patient.AGE(),"\t",patient.pathologie)
		_PATIENT_LIST = to_return

	def _SELECT_PATIENT(self, id):
		#not yet decided, but might be removed "according to its usefullness"
		global _DATA_BASE

		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select * from Patients where ID = {id}")
		res = cr.fetchall()
		if res != []:
			to_ret = Patient(*res[0])
		
			return [to_ret]
		else:
			return None
	
	def _DELETE_PATIENT(self, PatientID):
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()
		cr.execute(f"select * from Patients where ID = {PatientID} ")
		results = cr.fetchone()
		if results:
			cr.execute(f"delete from Patients where ID={PatientID} ")
			cr.execute(f"delete from Seances where Id_patient={PatientID}")
			cr.execute(f"delete from Testes where Id_patient={PatientID}")
			database.commit()
			database.close()
			return 0
		else:
			database.close()
			return 1


	#Functions that concern the tests and sessions
	def _ADD_SESSION(self, ID, ID_patient, poids, unite, date, type, medicament, faite, details=""):
		#globals
		global _DATA_BASE

		#connect database
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()

		#insert to database
		cr.execute(f"select * from Patients where ID={ID_patient}")
		result2 = cr.fetchone()
		if len(result2) == 0:
			return -1
		else:
			if (result2[0][9] < date):
				#session date less than entry date
				return -2

		cr.execute(f"select count() from Seances where ID ={ID}")
		result = cr.fetchone()
		instruction = f"insert into Seances(ID, Id_patient, Poids, unite, date_seance, type, medicament, seance_faite, details) values ({ID}, {ID_patient}, {poids},  {unite}, \"{date}\", {type}, \"{medicament}\", {faite}, \"{details}\")"
		if result[0] :
			return 1

		#print(instruction)
		cr.execute(instruction)

		#commit changes and close
		db.commit()
		db.close()
		return 0
	
	def _ADD_TEST(self, ID, Id_patient, date_test, details, type):
		#globals
		global _DATA_BASE
		#connect database
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		
		cr.execute(f"select count() from Seances where ID ={ID}")
		result = cr.fetchone()
		if result[0] :
			return 1
		#insert to database
		instruction = f"insert into Testes(ID, Id_patient, type, date_test, details) values({ID}, {Id_patient}, \"{type}\", \"{date_test}\", \"{details}\")"

		cr.execute(instruction)

		#commit changes and close
		db.commit()
		db.close()
		return 0

	def _DELETE_SESSION(self, ID):
		global _DATA_BASE
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()
		cr.execute(f"select count() from Seances where ID = {ID} ")
		results = cr.fetchone()
		#print((results))
		if results[0]:
			cr.execute(f"delete from Seances where ID={ID} ")
			database.commit()
			database.close()
			return 0
		else:
			database.close()
			return 1

	def _DELETE_TEST(self, ID):
		global _DATA_BASE
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()
		cr.execute(f"select count() from Testes where ID = {ID}")
		results = cr.fetchone()
		if results:
			cr.execute(f"delete from Testes where ID={ID} ")
			database.commit()
			database.close()
			return 0
		else:
			database.close()
			return 1
	
	def _UPDATE_SESSION(self, ID, poids, date, type, medicament, faite, details):
		#globals
		global _DATA_BASE

		#initialise database
		database = sqlite3.connect(_DATA_BASE)
		cr = database.cursor()

		#Change in the database
		cr.execute(f"update Seances set poids={poids}, date_seance=\"{date}\", type={type}, medicament=\"{medicament}\", seance_faite={faite}, details=\"{details}\" where ID={ID}")
		database.commit()
		database.close()

	def _UPDATE_TEST(self,ID, Id_patient, date, details, type_test):
		global _DATA_BASE

		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = f"update Testes set details=\"{details}\", id_patient={Id_patient}, date_test=\"{date}\", type=\"{type_test}\" where ID={ID}"
		print(instr)
		cr.execute(instr)
		db.commit()
		db.close()

	def _ALL_PATIENT_SESSIONS(self, patient_id):
		global _DATA_BASE
	   
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()

		cr.execute(f"select * from Seances where Id_patient={patient_id}")
		result = cr.fetchall()
		result = [Seance(*x) for x in result]
		db.close()
		return result

	def _ALL_PATIENT_TESTS(self, patient_id):
		global _DATA_BASE
		global _TEST_LIST
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()

		cr.execute(f"select * from Testes where Id_patient={patient_id}")
		result =  cr.fetchall()
		result = [Test(x[0], x[1], x[3], x[4], x[2]) for x in result]
		db.close()
		return result

	def _FILTERED_SESSIONS(self, date, unite=0, type=0):
		global _DATA_BASE
	   
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = f"select * from Seances where date_seance=\"{date}\""
		if unite != 0:
			instr += f" and unite={unite}"
		if type != 0:
			instr += f" and type={type}"
		
		cr.execute(instr)
		result = cr.fetchall()

		print("res : ", result)
		result = [Seance(*r) for r in result]
		db.close()
		return result
		
	def _FILTERED_PATIENTS(self, unite=0, text=""):
		global _DATA_BASE
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = "select * from Patients "
		if (txt:=text.replace("/", "")).isnumeric():
			instr += f"where ID like \"{txt[:-2]}__\" or ID like\"%{txt[-2:]}\""
		else:
			words = text.split(" ")
			if words != [""]:
				instr += f"where (Nom like\"{words[0]}%\" or Prénom like\"{words[0]}%\""
				for w in words[1:]:
					instr += f" or Nom like\"{w}%\" or Prénom like\"{w}%\""
				instr += ")"
		if unite!=0:
			if "where" not in instr:
				instr += " where "
			else:
				instr += " and "
			instr += f"unite={unite}"

		cr.execute(instr)
		results = cr.fetchall()

		results = [Patient(*x) for x in results]
		db.close()
		return results

	def _FILTERED_DOCTORS(self, unite=0, grade=0, text=""):
		global _DATA_BASE
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = "select * from Medecin "
		words = text.split(" ")
		if words != [""]:
			instr += f"where (Nom like\"{words[0]}%\" or prenom like\"{words[0]}%\" or nom_utilisateur like\"{words[0]}%\""
			for w in words[1:]:
				instr += f" or Nom like\"{w}%\" or prenom like\"{w}%\" or nom_utilisateur like\"{words[0]}%\""
			instr += ")"
		if unite!=0:
			if "where" not in instr:
				instr += " where "
			else:
				instr += " and "
			instr += f"unite={unite}"
		if grade!=0:
			if "where" not in instr:
				instr += " where "
			else:
				instr += " and "
			instr += f"grade={grade}"
		print(instr)
		cr.execute(instr)
		results = cr.fetchall()
		results2 = []
		for m in results:
			results2 += cr.execute(f"select * from MotDePasse where ID={m[0]}")
		print(results, results2)

		to_ret = [Medecin(*results[x], results2[x][1]) for x in range(len(results))]
		db.close()
		return to_ret


	def getMedicaments(self, SEANCE:Seance):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		meds = SEANCE.medicament.split("/")[:-1]
		toReturn = []

		for i in meds :
			print(i)
			instr = f"select * from Medicaments where ID={i}"
			print(instr)
			cr.execute(instr)
			med = cr.fetchone()
			cr.execute(f"select * from Formes where ID = {med[2]}")
			forme = cr.fetchone()
			toReturn.append(med[1] + " " + forme[1] + " " + forme[2] + " " + forme[3] + " " + forme[4])
		db.close()
		return toReturn

	def getPathologies(self, PATIENT:Patient):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		paths = PATIENT.pathologies.split("/")
		print(paths)
		toReturn = []
		if paths != [""]:
			for i in paths :
				cr.execute(f"select * from Pathologies where ID = '{int(i)}'")
				path = cr.fetchone()
				toReturn.append(path[1] + " " + path[2] + " " + path[3])
		db.close()
		return toReturn

	def getPathologiesCodes(self, pathologies):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		paths = pathologies.split("/")
		toReturn = []
		if paths != [""]:
			for i in paths:
				cr.execute(f"select classe, code from Pathologies where ID = {int(i)}")
				path = cr.fetchone()
				toReturn.append(path[0]+ path[1])
		db.close()
		return toReturn

	def getWilaya(self, PATIENT:Patient):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select * from Wilayas where Code={PATIENT.wilaya}")
		toReturn = cr.fetchone()
		db.close()
		return toReturn[1]

	def getAllPathologies(self):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select * from Pathologies")
		paths = cr.fetchall()
		db.close()
		return paths

	def getForms(self, med):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		i1 = f"select forme from Medicaments where libelle=\"{med}\""
	
		i2=lambda x : f"select * from Formes where ID=\"{x}\""
		
		cr.execute(i1)
		formes = cr.fetchall()
		#print(formes)
		fetched = []
		for i in formes:
			cr.execute(t:=i2(i[0]))
			#print(t)
			fetched+=cr.fetchall()
		
		result = []
		for i in fetched:
			s = str(i[0])+"-"+i[1]
			s += i[3] if i[3] != "#" else ""
			s += " " if s[-1]!=" " else ""
			s += i[4] if i[4] != "#" else ""
			result.append(s)
		return result

	def getMedicineId(self, med, form):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select * from Medicaments where libelle=\"{med}\" and forme={form[:form.index('-')]}")
		return cr.fetchone()[0]
	
	def getAllWilayas(self):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select * from Wilayas")
		paths = cr.fetchall()
		db.close()
		return paths

	def getPatientsWeightInformation(self, LIST_SEANCE):
		lst = LIST_SEANCE[-15:]
		result = {"Dates": [i.date_seance for i in lst], "Poids": [i.poids for i in lst]}
		return result
	
	def getPatientFromSeance(SEANCE:Seance):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select * from Patients where ID = {SEANCE.ID_patient}")
		res = cr.fetchone[0]
		db.close()
		return Patient(*res)

	def fillter_patho(self, date_1, date_2, unit, patho):  
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instruction = f"select * from Patients where  (Date_Entree between '{date_1}' and '{date_2}') "
		if unit != 0:
			instruction += f" and Unite = {unit}"
		cr.execute(instruction)
		if patho != 0 :
			instruction += f" (Pathologies like '{patho}/%' or Pathologies like '%/{patho}/%' or Pathologies like '%/{patho}') "
		result = cr.fetchall()
		db.close()      
		for i in range(len(result)):
			_PATIENT = Patient(*result[i])
			result[i]=_PATIENT
		return result

	def grande_fillter_age(self, date_1, date_2, unit, age_1, age_2):           
		
		#fonction intermidean
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instruction = f"select * from Patients where (Date_Entree < '{date_1}') "
		if unit != 0 :
			instruction += f" and Unite = {unit}  "
		cr.execute(instruction)
		result = cr.fetchall()
		i = 0
		HOMME_AC = 0
		FEMME_AC = 0
		HOMME_NC = 0
		FEMME_NC = 0
		for element in result :
			_PATIENT = Patient(*element)
			_PATIENT.date_naissance = _PATIENT.date_naissance
			if  ( age_1 <=_PATIENT.AGE() <= age_2 ):
				result[i] = element
				i += 1
		result = result[:i]
		for i in range(len(result)):
			_PATIENT = Patient(*result[i])
			_PATIENT.date_naissance = _PATIENT.date_naissance
			_PATIENT.date_entree = _PATIENT.date_entree
			if _PATIENT.sexe == 1 :
				HOMME_AC += 1
			else :
				FEMME_AC += 1
			result[i] = _PATIENT

		instruction = f"select * from Patients where (Date_Entree >= '{date_1}' and Date_Entree <= '{date_2}') "
		if unit != 0 :
			instruction += f" and Unite = {unit}  "
		cr.execute(instruction)
		result = cr.fetchall()
		i = 0
		for element in result :
			_PATIENT = Patient(*element)
			_PATIENT.date_naissance = _PATIENT.date_naissance
			if  ( age_1 <=_PATIENT.AGE() <= age_2 ):
				result[i] = element
				i += 1
		result = result[:i]
		for i in range(len(result)):
			_PATIENT = Patient(*result[i])
			_PATIENT.date_naissance = _PATIENT.date_naissance
			_PATIENT.date_entree = _PATIENT.date_entree
			if _PATIENT.sexe == 1 :
				HOMME_NC += 1
			else :
				FEMME_NC += 1
			result[i] = _PATIENT
		#print("result:", result)
		db.close()  
		TOTAL_AC = HOMME_AC + FEMME_AC
		TOTAL_NC = HOMME_NC + FEMME_NC
		TOTAL_GN = TOTAL_AC + TOTAL_NC
		return [str(age_1)+"-"+str(age_2), HOMME_AC, HOMME_NC, FEMME_AC, FEMME_NC, TOTAL_AC, TOTAL_NC, TOTAL_GN, result]


	def fillter_age(self, date_1, date_2, unit, age_1, age_2):
		return self.grande_fillter_age(date_1, date_2, unit, age_1, age_2)[8]


	def fillter_region(self, date_1, date_2, unit, wilaya):
		wilaya = int(wilaya)
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instruction = f"select * from Patients where (Date_Entree >= '{date_1}' and Date_Entree <= '{date_2}') and Wilaya = {wilaya} "
		if unit != 0 :
			instruction += f" and Unite = {unit} "
		cr.execute(instruction)
		result = cr.fetchall()
		db.close() 
		for i in range(len(result)):
			_PATIENT = Patient(*result[i])
			result[i]=_PATIENT       
		return result


	def fillter_patient_unity(self, date_1, date_2, unit):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instruction = f"select * from Patients where (Date_Entree between '{date_1}'and '{date_2}') "
		if unit != 0 :
			instruction += f" and Unite = {unit} "
		cr.execute(instruction)
		result = cr.fetchall()
		db.close()
		for i in range(len(result)):
			_PATIENT = Patient(*result[i])
			_PATIENT.date_naissance = _PATIENT.date_naissance
			_PATIENT.date_entree = _PATIENT.date_entree
			result[i]=_PATIENT
		return result 


	def stat_pathologie_partiel(self, date_1, date_2, unit, patho):
		#fonction intermidean  

		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()

		instruction = f"select count() from Patients where (Pathologies like '{patho}/%' or Pathologies like '%/{patho}/%' or Pathologies like '%/{patho}' ) and (Date_Entree < '{date_1}') and Sexe = 1 "

		if unit != 0:
			instruction += f" and Unite = {unit} "
		cr.execute(instruction)
		HOMME_AC = cr.fetchone()[0]

		instruction = f"select count() from Patients where (Pathologies like '{patho}/%' or Pathologies like '%/{patho}/%' or Pathologies like '%/{patho}' ) and (Date_Entree between '{date_1}' and '{date_2}') and Sexe = 1 "
		if unit != 0:
			instruction += f" and Unite = {unit} "
		cr.execute(instruction)
		HOMME_NC = cr.fetchone()[0]

		instruction = f"select count() from Patients where (Pathologies like '{patho}/%' or Pathologies like '%/{patho}/%' or Pathologies like '%/{patho}' ) and (Date_Entree < '{date_1}') and Sexe = 0"
		if unit != 0:
			instruction += f" and Unite = {unit} "
		cr.execute(instruction)
		FEMME_AC = cr.fetchone()[0]
	
		instruction = f"select count() from Patients where (Pathologies like '{patho}/%' or Pathologies like '%/{patho}/%' or Pathologies like '%/{patho}' ) and (Date_Entree between '{date_1}' and '{date_2}') and Sexe = 0 "
		if unit != 0:
			instruction += f" and Unite = {unit}"
		cr.execute(instruction)
		FEMME_NC = cr.fetchone()[0]

		TOTAL_AC = HOMME_AC + FEMME_AC
		TOTAL_NC = HOMME_NC + FEMME_NC
		TOTAL_GN = TOTAL_AC + TOTAL_NC

		db.close()
		return [HOMME_AC, HOMME_NC, FEMME_AC, FEMME_NC, TOTAL_AC, TOTAL_NC, TOTAL_GN]


	def stat_pathologie(self,date_1, date_2, unit, path = None):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		if path == None:
			cr.execute("select * from Pathologies")
			liste = cr.fetchall()
			result = []
			for i in liste:
				patho = str(i[0])
				# print(i[0])
				result.append([i[3]]+self.stat_pathologie_partiel(date_1, date_2, unit, patho))
			return result
		else:
			cr.execute(f"select * from Pathologies where id={path}")
			liste = cr.fetchall()
			result = []
			for i in liste:
				patho = str(i[0])
				result.append([i[3]]+self.stat_pathologie_partiel(date_1, date_2, unit, patho))
			return result


	def stat_region(self,date_1, date_2, unit, wilaya):
		wilaya = int(wilaya)
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute("select nom from Wilayas")
		wilayas = [x[0] for x in cr.fetchall()]
		cr.execute(f"select count() from Patients where (Wilaya =  {wilaya}) and (Date_Entree < '{date_1}') and Sexe = {1}  ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		HOMME_AC = cr.fetchone()[0]

		cr.execute(f"select count() from Patients where (Wilaya =  {wilaya}) and (Date_Entree between '{date_1}'and '{date_2}') and Sexe = {1}  ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		HOMME_NC = cr.fetchone()[0]

		cr.execute(f"select count() from Patients where (Wilaya =  {wilaya}) and (Date_Entree < '{date_1}') and Sexe = {0} ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		FEMME_AC = cr.fetchone()[0]

		cr.execute(f"select count() from Patients where (Wilaya =  {wilaya}) and (Date_Entree between '{date_1}'and '{date_2}') and Sexe = {0} ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		FEMME_NC = cr.fetchone()[0]

		TOTAL_AC = HOMME_AC + FEMME_AC
		TOTAL_NC = HOMME_NC + FEMME_NC
		TOTAL_GN = TOTAL_AC + TOTAL_NC

		db.close()
		return [wilayas[wilaya-1], HOMME_AC, HOMME_NC, FEMME_AC, FEMME_NC, TOTAL_AC, TOTAL_NC, TOTAL_GN]


	def stat_age(self, date_1, date_2, unit, age_1, age_2):
		return self.grande_fillter_age(date_1, date_2, unit, age_1, age_2)[:8]

	def stat_patient_unity(self, date_1, date_2, unit):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute(f"select count() from Patients where (Date_Entree < '{date_1}') and Sexe = {1}  ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		HOMME_AC = cr.fetchone()[0]

		cr.execute(f"select count() from Patients where (Date_Entree between '{date_1}'and '{date_2}') and Sexe = {1}  ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		HOMME_NC = cr.fetchone()[0]

		cr.execute(f"select count() from Patients where (Date_Entree < '{date_1}') and Sexe = {0} ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		FEMME_AC = cr.fetchone()[0]

		cr.execute(f"select count() from Patients where (Date_Entree between '{date_1}'and '{date_2}') and Sexe = {0} ")
		if unit != 0:
			instruction += f" and Unite = {unit} "
		FEMME_NC = cr.fetchone()[0]

		TOTAL_AC = HOMME_AC + FEMME_AC
		TOTAL_NC = HOMME_NC + FEMME_NC
		TOTAL_GN = TOTAL_AC + TOTAL_NC

		db.close()
		return [unit, HOMME_AC, HOMME_NC, FEMME_AC, FEMME_NC, TOTAL_AC, TOTAL_NC, TOTAL_GN]

	def page_statistique(self, date_1, date_2, unite, critere, age_1, age_2, wilaya, patho, chifres_liste):
		#chifre_liste soit égale à "liste" soit égale à "chifres"
		if chifres_liste == 1 :
			if critere == 0 :
				return self.fillter_patient_unity(date_1, date_2, unite)
			elif critere == 1 :
				return self.fillter_patho(date_1, date_2, unite, patho)
			elif critere == 2 :
				return self.fillter_age(date_1, date_2, unite, age_1, age_2)
			else :
				if wilaya != 0:
					return self.fillter_region(date_1, date_2, unite, wilaya)
				else:
					return []
		
		else :
			if critere == 0 :
				return [self.stat_patient_unity(date_1, date_2, unite)]
			elif critere == 1 :
				if patho == 0 :
					return self.stat_pathologie(date_1, date_2, unite)
				else :
					return self.stat_pathologie(date_1, date_2, unite, patho)
			elif critere == 2 :
				return [self.stat_age(date_1, date_2, unite, age_1, age_2)]
			else :
				if wilaya != 0:
					return [self.stat_region(date_1, date_2, unite, wilaya)]
				else:
					return [self.stat_region(date_1, date_2, unite, w) for w in range(1, 59)]
	
	def stat_totalACHomme(self, date1, unit):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = f"select count() from Patients where (Date_Entree <'{date1}') and Sexe = {1} "
		if (unit != 0):
			instr += f" and Unite = {unit}"
		cr.execute(instr)
		HOMME_AC = cr.fetchone()[0]
		return HOMME_AC

	def stat_totalNCHomme(self, date1, date2, unit):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = f"select count() from Patients where (Date_Entree between '{date1}'and '{date2}') and Sexe = {1} "
		if (unit != 0):
			instr += f" and Unite = {unit}"
		cr.execute(instr)
		HOMME_NC = cr.fetchone()[0]
		return HOMME_NC

	def stat_totalACFemme(self, date1, unit):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = f"select count() from Patients where (Date_Entree <'{date1}') and Sexe = {0} "
		if (unit != 0):
			instr += f" and Unite = {unit}"
		cr.execute(instr)
		FEMME_AC = cr.fetchone()[0]
		return FEMME_AC

	def stat_totalNCFemme(self, date1, date2, unit):
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		instr = f"select count() from Patients where (Date_Entree between '{date1}'and '{date2}') and Sexe = {0} "
		if (unit != 0):
			instr += f" and Unite = {unit}"
		cr.execute(instr)
		FEMME_NC = cr.fetchone()[0]
		return FEMME_NC
		