import sqlite3
import traceback
from Doctor_class import Medecin
from Patient_class import Patient
from constants import date_it, convert, _DATA_BASE
from core import Core
from Session_class import Seance
from Test_class import Test
from User_interface import ErrorDialog, SessionInfoDialog, MedicineDialog, PathologiesDialog, DeletionConfirm, MainScreen, SignInPage
import PyQt5
from File_genereator import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QDialog
from datetime import date
import res
import sys


class Main():

	def __init__(self):
		
		#data to fetch from database
		self.user = None
		self.patientList = None
		self.doctorList = []
		self.sessionList = []
		self.testList = []
		self.selectedPatient = None
		self.selectedDoctor = None
		self.selectedSession = None
		self.selectedTest = None
		self.pathologiesList = []
		self.medicinesList = []
		
		#for going back in the interface
		self.lastIndex = [0, 0]

		self.app = QApplication(sys.argv)
		self.core = Core()
		
		self.pathologiesDialogCont = None
		self.pathologiesDialog = None
		
		self.dialogCont = None
		self.dialog = None

		self.medicineDialogCont = None
		self.medicineDialog = None

		self.screens = {"Acceuil": MainScreen(), "Connection": SignInPage()}
		self.MainWindow = QMainWindow()
		self.screens["Connection"].setupUi(self.MainWindow, self)
		
		#Error Message
		self.msg = ""
		
		#IDs for patients, doctors, sessions and tests
		self.IdPatient = 0
		self.IdMedecin = 0
		self.IdSeance = 0
		self.IdTeste = 0

	def handleError(func):
		def executeFunction(self, param=None):
			try:
				#print("params for ",func, ":", param)
				if param != None:
					func(self, param)
				else:
					func(self)
			except Exception:
				self.showErrorMessage(traceback.format_exc())
		
		return executeFunction
	
	@handleError
	def run(self):
		try:
			with open("IdSave", "r") as f:
				result = f.readlines()
				#print(result)
				self.IdPatient = int(result[0])
				self.IdMedecin = int(result[1])
				self.IdSeance = int(result[2])
				self.IdTeste = int(result[3])
				#print(self.IdMedecin, self.IdPatient, self.IdSeance, self.IdTeste)

		except FileNotFoundError:
			self.IdPatient = 1
			self.IdMedecin = 0
			self.IdSeance = 0
			self.IdTeste = 0
		
		except IndexError:
			self.IdPatient = 1
			self.IdMedecin = 0
			self.IdSeance = 0
			self.IdTeste = 0
		
		self.MainWindow.showMaximized()
		return_val = self.app.exec_()
		with open("IdSave", "w") as f:
			f.write(str(self.IdPatient)+"\n"+str(self.IdMedecin)+"\n"+str(self.IdSeance)+"\n"+str(self.IdTeste))

		sys.exit(return_val)

	def showErrorMessage(self, msg):
		self.msg=msg
		self.ErrorCont = QDialog()
		self.ErrorDialog = ErrorDialog()
		self.ErrorDialog.setupUi(self.ErrorCont, self)
		self.ErrorDialog.label_2.setText(self.msg)
		self.ErrorCont.exec()

	def kill(self):
		with open("IdSave", "w") as f:
			f.write(str(self.IdPatient)+"\n"+str(self.IdMedecin)+"\n"+str(self.IdSeance)+"\n"+str(self.IdTeste))

		sys.exit(1)
	
	def extractErrorMessage(self):
		filePicker = QFileDialog()
		pth = filePicker.getSaveFileName(caption="Sauvegarder message d'erreur",
		directory="Error log"+date.today().isoformat(), filter="tous les fichier (*)")
		if pth[0]!="":
			with open(pth[0], "w") as f:
				f.write(self.msg)
			self.ErrorCont.close()
			self.kill()
	
	@handleError	
	def addAdmin(self):
		interface = self.screens["Connection"]
		nom = interface.lineEdit_8.text()
		prenom = interface.lineEdit_9.text()
		usern = interface.lineEdit_7.text()
		passwrd = interface.lineEdit_6.text()
		unite = 1+ interface.comboBox_10.currentIndex()
		num_tel = interface.lineEdit_11.text()
		if nom.replace(" ", "").isalpha() == False:
			interface.utilisateurExisteError.setText("Veuillez remplir le champ de Nom avec seulement des caractères latins et des espaces")
			interface.utilisateurExisteError.show()
			return

		if prenom.replace(" ", "").isalpha() == False:
			interface.utilisateurExisteError.setText("Veuillez remplir le champ de Prénom avec des caractères latins ou des espaces")
			interface.utilisateurExisteError.show()
			return

		if num_tel.isnumeric() == False or num_tel[0]!="0":
			interface.utilisateurExisteError.setText("Veuillez introduire un numéro de téléphone valide (seulement des chiffres commençant par un 0)")
			interface.utilisateurExisteError.show()
			return 

		self.core._ADD_USER(0, nom, prenom, 1, unite, num_tel, usern, passwrd)
		self.IdMedecin = 1
		interface.changeSubWindow(0)
	
	@handleError
	def logout(self):
		self.user = None
		self.screens["Connection"].setupUi(self.MainWindow, self)

	@handleError
	def login(self):
		username = self.screens["Connection"].userNameBar.text()
		password = self.screens["Connection"].passwordBar.text()
		try:
			result = self.core._SIGN_IN(username, password)
			if result[0] == 2:
				self.screens["Connection"].msgErrorUsername.setText("Le nom d'utilisateur es incorrect")
				self.screens["Connection"].userNameBar.setStyleSheet(""" background-color:white;
			font-family:"mulish medium";
			font-size:18px;
			color:#717072;
			border:none;
			border-bottom:2px solid #ff0000;
			""")
			elif result[0] == 1 or result[0] == -3:
				self.screens["Connection"].msgErrorPassword.setText("Le mot de passe est incorrect")
				self.screens["Connection"].passwordBar.setStyleSheet(""" background-color:white;
			font-family:"mulish medium";
			font-size:18px;
			color:#717072;
			border:none;
			border-bottom:2px solid #ff0000;
			""")
			elif result[0] == 0:
				self.user = result[1]
				self.user.grade = int(self.user.grade)
				self.screens["Acceuil"].setupUi(self.MainWindow, self)
				self.screens["Acceuil"].doctorListBtn.setEnabled(self.user.grade==1)
				

			elif result[0] == -2:
				self.screens["Connection"].msgErrorUsername.setText("Admin n'a pas la permission car la base de données est déja initialisée")
				self.screens["Connection"].userNameBar.setStyleSheet(""" background-color:white;
			font-family:"mulish medium";
			font-size:18px;
			color:#717072;
			border:none;
			border-bottom:2px solid #ff0000;
			""")
			elif result[0] == -1:
				self.core._INIT_DB()
				self.screens["Connection"].changeSubWindow(1)
		except sqlite3.OperationalError:
			self.screens["Connection"].msgErrorUsername.setText("Base de données non initialisée ou corrempu, connectez en utilisant le nom d'utilisateur admin")
			#print(traceback.extract_stack())

		self.screens["Connection"].passwordBar.setText("")
		self.screens["Connection"].userNameBar.setText("")
	
	@handleError
	def goBack(self):
		interface = self.screens["Acceuil"]
		interface.changeSubWindow(self, self.lastIndex[0])
		self.selectedDoctor = None
		self.selectedPatient = None
		self.selectedSession = None
		self.selectedTest = None
	
	@handleError
	def addNewDoctor(self):
		scrn = self.screens["Acceuil"]
		nom = scrn.lineEdit_10.text()
		num = self.IdMedecin
		prenom = scrn.lineEdit_8.text()
		nom_util = scrn.lineEdit_7.text()
		mdp = scrn.lineEdit_6.text()
		unite = 1 + scrn.comboBox_10.currentIndex()
		grade = 1 + scrn.comboBox_5.currentIndex()
		num_tele = scrn.lineEdit_11.text()
		# utilisateurExisteError
		if nom.replace(" ", "").isalpha() == False:
			scrn.utilisateurExisteError.setText("Veuillez remplir le champ de Nom avec seulement des caractères latins et des espaces")
			scrn.utilisateurExisteError.show()
			return

		if prenom.replace(" ", "").isalpha() == False:
			scrn.utilisateurExisteError.setText("Veuillez remplir le champ de Prénom avec des caractères latins ou des espaces")
			scrn.utilisateurExisteError.show()
			return

		if num_tele.isnumeric() == False or num_tele[0]!="0":
			scrn.utilisateurExisteError.setText("Veuillez introduire un numéro de téléphone valide (seulement des chiffres commençant par un 0)")
			scrn.utilisateurExisteError.show()
			return 

		op = self.core._ADD_USER(num,
		nom,
		prenom, 
		grade, 
		unite, 
		num_tele,
		nom_util,
		mdp)

		if(op == 0):
			self.selectedDoctor = Medecin(num, nom, prenom, grade, unite, num_tele, nom_util, mdp)
			self.IdMedecin += 1
		
		elif op == -1:
			scrn.utilisateurExisteError.setText("Veuillez introduire un autre nom d'utilisateur légale (different de Admin)")
			scrn.utilisateurExisteError.show()
			return
		
		elif op == 1:
			scrn.utilisateurExisteError.setText("Veuillez introduire un autre nom d'utilisateur non éxistant")
			scrn.utilisateurExisteError.show()
			return
		scrn.changeSubWindow(self, 7, 0)

	@handleError
	def modifyDoctor(self):
		scrn = self.screens["Acceuil"]
		nom = scrn.lineEdit_10.text()
		prenom = scrn.lineEdit_8.text()
		nom_util = scrn.lineEdit_7.text()
		mdp = scrn.lineEdit_6.text()
		unite = 1 + scrn.comboBox_10.currentIndex()
		grade = 1 + scrn.comboBox_5.currentIndex()
		num_tele = scrn.lineEdit_11.text()
		num = self.selectedDoctor.ID
		if nom.replace(" ", "").isalpha() == False:
			scrn.utilisateurExisteError.setText("Veuillez remplir le champ de Nom avec seulement des caractères latins et des espaces")
			scrn.utilisateurExisteError.show()
			return

		if prenom.replace(" ", "").isalpha() == False:
			scrn.utilisateurExisteError.setText("Veuillez remplir le champ de Prénom avec des caractères latins ou des espaces")
			scrn.utilisateurExisteError.show()
			return

		if num_tele.isnumeric() == False or num_tele[0]!="0":
			scrn.utilisateurExisteError.setText("Veuillez introduire un numéro de téléphone valide (seulement des chiffres commençant par un 0)")
			scrn.utilisateurExisteError.show()
			return 

		bl = (self.selectedDoctor == self.user)
		self.selectedDoctor = Medecin(num, nom, prenom, grade, unite, num_tele, nom_util, mdp)
		
		if bl: 
			self.user = self.selectedDoctor

		
		self.core._UPDATE_USER(self.selectedDoctor)
		if bl: scrn.changeSubWindow(self, 7, 3)
		else: scrn.changeSubWindow(self, 7, 0)
 
	@handleError
	def addNewPatient(self):
		scrn = self.screens["Acceuil"]
		nom = scrn.lineEdit_2.text()
		prenom = scrn.lineEdit.text()
		num = scrn.spinBox_2.value()
		dtnais = scrn.dateEdit.date().toString(PyQt5.QtCore.Qt.ISODate)
		sx = scrn.comboBox.currentIndex()
		dtentr = scrn.dateEdit_2.date().toString(PyQt5.QtCore.Qt.ISODate)
		tel = scrn.lineEdit_4.text()
		alttel = scrn.lineEdit_3.text()
		unite = 1 + scrn.comboBox_4.currentIndex()
		grp = scrn.comboBox_7.currentIndex()
		rh = scrn.comboBox_6.currentIndex()
		pds = scrn.doubleSpinBox.value()
		tll = scrn.spinBox.value()
		rdio = scrn.comboBox_8.currentIndex()
		db = scrn.dateEdit_4.date().toString(PyQt5.QtCore.Qt.ISODate)
		df = scrn.dateEdit_3.date().toString(PyQt5.QtCore.Qt.ISODate)
		wly = scrn.comboBox_9.currentIndex()+1
		com = scrn.lineEdit_5.text()
		
		if nom.replace(" ", "").isalpha() == False:
			scrn.numExisterror.setText("Veuillez remplir le champ de Nom avec seulement des caractères latins et des espaces")
			scrn.numExisterror.show()
			return 
		
		if prenom.replace(" ", "").isalpha() == False:
			scrn.numExisterror.setText("Veuillez remplir le champ de Prénom avec des caractères latins ou des espaces")
			scrn.numExisterror.show()
			return 
		
		if dtnais>dtentr:
			scrn.numExisterror.setText("Veuillez introduire une date de naissance avant la date d'entrée")
			scrn.numExisterror.show()
			return 
		
		if tel.isnumeric() == False or tel[0]!="0":
			scrn.numExisterror.setText("Veuillez introduire un numéro de téléphone valide (seulement des chiffres commençant par un 0)")
			scrn.numExisterror.show()
			return 
		
		if alttel.isnumeric() == False or alttel[0]!="0":
			scrn.numExisterror.setText("Veuillez introduire un numéro de téléphone alternatif valide (seulement des chiffres commençant par un 0)")
			scrn.numExisterror.show()
			return 
		
		if com.replace(" ", "").isalpha() == False:
			scrn.numExisterror.setText("Veuillez remplir le champ de commune avec des caractères latins ou des espaces")
			scrn.numExisterror.show()
			return 
		
		path = ""
		for i in self.pathologiesList:
			path += i.replace("\t", "")
		path = path[:-1]
		#print(path)

		op = self.core._ADD_PATIENT(int(str(num)+dtentr[2:4]),nom,prenom,dtnais, sx, path,unite, grp,rh,pds, tll,tel,alttel,com, wly,rdio,db, df,dtentr)

		if op == 0:
			self.selectedPatient = Patient(str(num)+dtentr[2:4], nom, prenom, dtnais, sx, path,
		 tel, alttel, unite, dtentr, grp, rh, pds, tll, com, wly, rdio, db, df)
			self.IdPatient = int(self.selectedPatient.ID[:-2])+1
		else:
			scrn.numExisterror.setText("Veuillez introduire un numéro non éxistant")
			scrn.numExisterror.show()
			return 
		self.pathologiesList = []
		scrn.changeSubWindow(self, 6, 0)
	
	@handleError
	def modifyPatient(self):
		scrn = self.screens["Acceuil"]
		nom = scrn.lineEdit_2.text()
		prenom = scrn.lineEdit.text()
		num = scrn.spinBox_2.value()
		dtnais = scrn.dateEdit.date().toString(PyQt5.QtCore.Qt.ISODate)
		sx = 1 - scrn.comboBox.currentIndex()
		dtentr = scrn.dateEdit_2.date().toString(PyQt5.QtCore.Qt.ISODate)
		tel = scrn.lineEdit_4.text()
		alttel = scrn.lineEdit_3.text()
		unite = 1 + scrn.comboBox_4.currentIndex()
		grp = scrn.comboBox_7.currentIndex()
		rh = scrn.comboBox_6.currentIndex()
		pds = scrn.doubleSpinBox.value()
		tll = scrn.spinBox.value()
		rdio = scrn.comboBox_8.currentIndex()
		db = scrn.dateEdit_4.date().toString(PyQt5.QtCore.Qt.ISODate)
		df = scrn.dateEdit_3.date().toString(PyQt5.QtCore.Qt.ISODate)
		wly = scrn.comboBox_9.currentIndex()
		com = scrn.lineEdit_5.text()
		self.selectedPatient = Patient(str(num)+dtentr[2:4], nom, prenom, dtnais, sx, self.pathologiesList,
		 tel, alttel, unite, dtentr, grp, rh, pds, tll, com, wly, rdio, db, df)

		op = self.core._UPDATE_PATEINT(
		self.selectedPatient.ID,
		self.selectedPatient.tel_patient,
		self.selectedPatient.tel_alt, 
		self.selectedPatient.wilaya, 
		self.selectedPatient.commune, 
		self.selectedPatient.radiotherapie,
		self.selectedPatient.debut, 
		self.selectedPatient.fin,
		self.selectedPatient.pathologies,
		self.selectedPatient.unite, 
		self.selectedPatient.poids, 
		self.selectedPatient.taille
		)

		scrn.changeSubWindow(self, 6, 0)
	
	@handleError
	def addNewRendezVous(self):
		scrn = self.screens["Acceuil"]
		ID = self.IdSeance
		if(not self.selectedPatient):
			ID_patient = scrn.spinBox_4.value() 
		else:
			#print(self.selectedPatient)
			ID_patient = self.selectedPatient.ID
			scrn.spinBox_2.setValue(ID_patient)
		
		poids = scrn.doubleSpinBox_2.value()
		unite = scrn.comboBox_15.currentIndex() + 1
		date_seance = scrn.dateEdit_5.date().toString(PyQt5.QtCore.Qt.ISODate)
		traitement = scrn.comboBox_13.currentIndex() + 1
		medicament = self.medicinesList
		etat = scrn.comboBox_18.currentIndex()
		# details = scrn.label_54.text()
		details = scrn.textEdit_2.toPlainText()

		
		op = self.core._ADD_SESSION(ID, ID_patient, poids, unite, date_seance, traitement, medicament, etat, details)
		if(op == 0):
			self.selectedSession = Seance(ID, ID_patient, poids, unite, date_seance, traitement,  medicament, etat, details)
			#print(self.selectedSession)
			self.IdSeance += 1
		if (op == -1):
			#patient does not exist
			return
		if op == 1:
			#session Id exists
			return
		if op == -2:
			#date before entry date
			print("No No")
			return

		scrn.changeSubWindow(self, 8, 0)
	
	@handleError
	def modifyRendezVous(self):
		scrn = self.screens["Acceuil"]
		ID = self.selectedSession.ID
		ID_patient = scrn.spinBox_4.value()
		poids = scrn.doubleSpinBox_2.value()
		unite = scrn.comboBox_15.currentIndex() + 1
		date_seance = scrn.dateEdit_5.date().toString(PyQt5.QtCore.Qt.ISODate)
		traitement = scrn.comboBox_13.currentIndex() + 1
		medicament = self.medicinesList
		etat = scrn.comboBox_18.currentIndex()
		# details = scrn.label_54.text()
		details = scrn.textEdit_2.toPlainText()
		self.selectedSession = Seance(ID, ID_patient, poids, unite, date_seance, traitement, medicament, etat, details)

		op = self.core._UPDATE_SESSION(
		self.selectedSession.ID,
		self.selectedSession.poids,
		self.selectedSession.date_seance, 
		self.selectedSession.type_traitement, 
		self.selectedSession.medicament, 
		self.selectedSession.seance_faite,
		self.selectedSession.details
		)

		scrn.changeSubWindow(self, 8, 0)
	
	@handleError
	def addNewTest(self):
		scrn = self.screens["Acceuil"]
		ID = self.IdTeste
		ID_patient = self.selectedPatient.ID
		type_teste = scrn.lineEdit_9.text()
		date_teste = scrn.dateEdit_6.date().toString(PyQt5.QtCore.Qt.ISODate)
		details = scrn.textEdit.toPlainText()

		op = self.core._ADD_TEST(ID, ID_patient, date_teste, details, type_teste)
		if(op == 0):
			self.selectedTest = Test(ID, ID_patient,  date_teste, details,type_teste)
			#print(self.selectedTest)
			self.IdTeste += 1
		else:
			return

		scrn.changeSubWindow(self, 9, 0)
	
	@handleError
	def modifyTest(self):
		scrn = self.screens["Acceuil"]
		ID = self.selectedTest.ID
		ID_patient = self.selectedPatient.ID
		type_teste = scrn.lineEdit_9.text()
		date_test = scrn.dateEdit_6.date().toString(PyQt5.QtCore.Qt.ISODate)
		details = scrn.textEdit.toPlainText()
		self.selectedTest = Test(ID, ID_patient, date_test, details, type_teste)

		op = self.core._UPDATE_TEST(ID, ID_patient, date_test, details, type_teste)
		scrn.changeSubWindow(self, 9, 0)
	
	@handleError
	def extractSessionsList(self):
		filePicker = QFileDialog()
		pth = filePicker.getSaveFileName(caption="Sauvegarder Liste des Scéances",
		directory="Liste Du Jour "+date.today().isoformat(), filter="Microsoft Excel Worksheet (*.xlsx);;All Files (*)")
		if pth[0]!="":
			printTodaysSessions(self, pth[0], self.sessionList)

	@handleError
	def extractPatientsList(self):
		filePicker = QFileDialog()
		pth = filePicker.getSaveFileName(caption="Sauvegarder Liste des Patients",
		directory="Liste Des Patients",
		filter="Microsoft Excel Worksheet (*.xlsx);;All Files (*)")
		if pth[0]!="":
			printListPatients(pth[0], self.patientList)

	@handleError
	def extractDoctorsList(self):
		filePicker = QFileDialog()
		pth = filePicker.getSaveFileName(caption="Sauvegarder Liste des Médecins",
		directory="Liste Des Medecins",
		 filter="Microsoft Excel Worksheet (*.xlsx);;All Files (*)")

		if pth[0] != "":  
			printListDoctors(pth[0], self.doctorList)
	
	@handleError
	def extractMedicalData(self):
		filePicker = QFileDialog()
		self.selectedPatient.date_entree = date_it(self.selectedPatient.date_entree)
		self.selectedPatient.date_naissance = date_it(self.selectedPatient.date_naissance)
		self.selectedPatient.debut = date_it(self.selectedPatient.debut)if self.selectedPatient.radiotherapie else ""
		
		self.selectedPatient.fin = date_it(self.selectedPatient.fin)if self.selectedPatient.radiotherapie else ""

		pth = filePicker.getSaveFileName(caption="Sauvegarder Dossier Medical",
		directory="Dossier Medical de "+self.selectedPatient.nom + " "+self.selectedPatient.prenom,
		 filter="Fichier PDF (*.pdf);;Tous les fichiers (*)")

		if pth[0] != "":  
			printPatient(self.core, pth[0], self.selectedPatient, self.sessionList, self.testList)

	@handleError
	def extractStats(self):
		interface = self.screens["Acceuil"]
		date_1 = interface.dateDebut.date().toString(PyQt5.QtCore.Qt.ISODate)
		date_2 = interface.dateFin.date().toString(PyQt5.QtCore.Qt.ISODate)
		unit = interface.critereDrop_2.currentIndex()
		filePicker = QFileDialog()
		pth = filePicker.getSaveFileName(caption="Extraire les statistiques", directory="Statistiques", filter="Microsoft Excel Worksheet (*.xslx);;Tous les Fichiers (*)")
		printStatistics(pth[0], self.core, date_1, date_2, unit)
	
	@handleError
	def extractWeightGraph(self):
		filePicker = QFileDialog()
		pth = filePicker.getSaveFileName(caption="Extraire les statistiques", directory="Changement du poids de "+self.selectedPatient.nom+" "+self.selectedPatient.prenom, filter="Fichier PDF (*.pdf);;Tous les Fichiers (*)")
		printWeightPlot(self, pth[0], self.selectedPatient)

	@handleError
	def loadData(self, index):
		interface = self.screens["Acceuil"]

		if index == 0:
			table = self.screens["Acceuil"].mainToDayList
			
			self.screens["Acceuil"].currentDate.setDate(date.today())
			self.sessionList = self.core._FILTERED_SESSIONS(self.screens["Acceuil"].currentDate.date().toString(PyQt5.QtCore.Qt.ISODate))
			self.patientList = []
			for s in self.sessionList:
				self.patientList += self.core._SELECT_PATIENT(s.ID_patient)
			
			cnt = len(self.sessionList)
			table.setRowCount(cnt)
			for r in range(cnt):
				items = [
				QTableWidgetItem(str(self.sessionList[r].ID_patient)[:-2]+"/"+str(self.sessionList[r].ID_patient)[-2:]).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(self.patientList[r].nom)).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter), 
				 QTableWidgetItem(str(self.patientList[r].prenom)).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(["Thorasique", "Génicologie", "Digestive"][self.sessionList[r].unite-1])).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(["Chimio/traitement", "controle/consultation"][self.sessionList[r].type_traitement-1])).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter), 
				 QTableWidgetItem(str(self.sessionList[r].seance_faite)).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(self.sessionList[r].ID)).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)]
				for c in range(7):
					table.setItem(r,c, items[c])

		if index == 1:
			table = self.screens["Acceuil"].tableRendezVous
			self.screens["Acceuil"].currentDate_2.setDate(self.screens["Acceuil"].calendarWidget.selectedDate())
			dt = self.screens["Acceuil"].currentDate_2.date().toString(PyQt5.QtCore.Qt.ISODate)
			unt = self.screens["Acceuil"].uniteDropListe_2.currentIndex()
			tdt = self.screens["Acceuil"].typeDeTraitementDropListe_2.currentIndex()
			#print(dt, unt, tdt)
			self.sessionList = self.core._FILTERED_SESSIONS(dt, unt, tdt)
			self.patientList = []
			for s in self.sessionList:
				self.patientList += self.core._SELECT_PATIENT(s.ID_patient)

			cnt = len(self.sessionList)
			table.setRowCount(cnt)
			#print("sessions", self.sessionList)
			for r in range(cnt):
				items = [QTableWidgetItem(str(self.sessionList[r].ID_patient)[:-2]+"/"+str(self.sessionList[r].ID_patient)[-2:]).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(self.patientList[r].nom)).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter), 
				 QTableWidgetItem(str(self.patientList[r].prenom)).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(self.sessionList[r].UNITE())).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(self.sessionList[r].TYPE_TRAITEMENT())).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter), 
				 QTableWidgetItem(str(self.sessionList[r].SEANCE_FAITE())).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter),
				 QTableWidgetItem(str(self.sessionList[r].ID)).setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)
				 ]
				for c in range(7):
					table.setItem(r,c, items[c])

		if index == 2:
			table = interface.mainPatientList
			txt = interface.researchLine_1.text()
			unite = interface.uniteDropListe_4.currentIndex()
			self.patientList = []
			self.patientList = self.core._FILTERED_PATIENTS(unite, txt)
			
			cnt = len(self.patientList)
			table.setRowCount(cnt)
			for r in range(cnt):
				paths = self.core.getPathologiesCodes(self.patientList[r].pathologies)
				paths = str(paths[:3]).replace("'", "").replace("[", "").replace("]", "")
				items = [QTableWidgetItem(str(self.patientList[r].ID)[:-2]+"/"+str(self.patientList[r].ID)[-2:]),
				 QTableWidgetItem(str(self.patientList[r].nom)), 
				 QTableWidgetItem(str(self.patientList[r].prenom)),
				 QTableWidgetItem(self.patientList[r].UNITE()),
				 QTableWidgetItem(paths+"..."),
				 QTableWidgetItem(self.patientList[r].SEXE())]
				for c in range(6):
					items[c].setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)
					table.setItem(r,c, items[c])

		if index == 3:
			table = interface.medecinListe
			txt = interface.researchLine_2.text()
			grade = interface.typeDeTraitementDropListe_3.currentIndex()
			unite = interface.uniteDropListe_3.currentIndex()
			self.doctorList = []
			self.doctorList = self.core._FILTERED_DOCTORS(unite, grade, txt)
			
			cnt = len(self.doctorList)
			table.setRowCount(cnt)
			for r in range(cnt):
				items = [QTableWidgetItem(str(self.doctorList[r].nom)),
				 QTableWidgetItem(str(self.doctorList[r].prenom)), 
				 QTableWidgetItem(self.doctorList[r].UNITE()),
				 QTableWidgetItem(str(self.doctorList[r].GRADE())),
				 QTableWidgetItem(str(self.doctorList[r].nom_utilisateur)), 
				 QTableWidgetItem(str(self.doctorList[r].ID))]
				for c in range(6):
					items[c].setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)
					table.setItem(r,c, items[c])

		if index == 4:

			criteres = {"critere":interface.critereDrop.currentIndex(), "unite":interface.critereDrop_2.currentIndex()}
			
			l = self.core.page_statistique(
				interface.dateDebut.date().toString(PyQt5.QtCore.Qt.ISODate),
				interface.dateFin.date().toString(PyQt5.QtCore.Qt.ISODate),
				interface.critereDrop_2.currentIndex(),
				interface.critereDrop.currentIndex(),
				interface.ageDebut.value(),
				interface.ageFin.value(),
				interface.regionSelectDrop.currentIndex(),
				interface.pathologieSelectDrop.currentIndex(),
				interface.tabsStack.currentIndex()
			)
			cnt = len(l)
			idxs=[interface.tabsStack.currentIndex(), 
				criteres["critere"], criteres["unite"]]
			table = [interface.listStatTable, interface.listPatientTable][idxs[0]]
			table.setRowCount(0)
			row = 0
			
			if idxs[0] == 0:
				ttlh = 0
				ttlf = 0
				ttlg = 0
				#table.setHorizontalHeaderItem(1, QTableWidgetItem(["Pathologies", "Age", "Wilaya"][criteres["critere"]-1]))
				table.horizontalHeaderItem(1).setText(["Pathologies", "Age", "Wilaya"][criteres["critere"]-1])
				#print("l[0] = ", l[0])
				#print(l[0][7])
				for r in range(cnt):
					#print("r : ", r)
				
					table.setRowCount(table.rowCount()+1)
					items = [QTableWidgetItem(str(r+1)), 
					QTableWidgetItem(str(l[r][0])),
					QTableWidgetItem(str(l[r][1])),
					QTableWidgetItem(str(l[r][2])),
					QTableWidgetItem(str(l[r][3])),
					QTableWidgetItem(str(l[r][4])),
					QTableWidgetItem(str(l[r][5])),
					QTableWidgetItem(str(l[r][6])),
					QTableWidgetItem(str(l[r][7]))]
					ttlh += l[r][1]+l[r][2]
					ttlf += l[r][3]+l[r][4]
					ttlg += l[r][7]
					for c in range(9):
						items[c].setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)
						table.setItem(row,c, items[c])
					row += 1
				interface.totalHomme.setText("Homme: "+str(ttlh))	
				interface.totalFemme.setText("Femme: "+str(ttlf))
				interface.totalTG.setText(str(ttlg))
			
			if idxs[0] == 1:
				paths = self.core.getAllPathologies()
				for r in range(cnt):		
					table.setRowCount(table.rowCount()+1)
					path = [paths[int(s)-1][1]+paths[int(s)-1][2] for s in l[r].pathologies.split("/")][:3]
					items = [
					QTableWidgetItem(str(l[r].ID//100)+"/"+str(l[r].ID%100)),
					QTableWidgetItem(str(l[r].nom)),
					QTableWidgetItem(str(l[r].prenom)),
					QTableWidgetItem(str(l[r].UNITE())),
					QTableWidgetItem(str(path).replace("[", "").replace("]", "").replace("'", "")+"..."),
					QTableWidgetItem(str(l[r].SEXE()))]
					for c in range(6):
						items[c].setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)
						table.setItem(r,c, items[c])
		
		if index == 6:
			interface = self.screens["Acceuil"]
			list_wilaya = self.core.getAllWilayas()
			
			for i in list_wilaya:
				interface.comboBox_9.addItem(i[1])
			
			if self.selectedPatient != None:
				interface.spinBox_2.setValue(int(self.selectedPatient.ID)//100)
				interface.label_29.setText(self.selectedPatient.pathologies)
				interface.lineEdit.setText(self.selectedPatient.prenom)
				interface.lineEdit_2.setText(self.selectedPatient.nom)
				interface.lineEdit_3.setText(self.selectedPatient.tel_alt)
				interface.lineEdit_4.setText(self.selectedPatient.tel_patient)
				interface.lineEdit_5.setText(self.selectedPatient.commune)
				interface.comboBox_9.setCurrentIndex(self.selectedPatient.wilaya-1)
				interface.comboBox.setCurrentIndex(self.selectedPatient.sexe)
				interface.comboBox_6.setCurrentIndex(self.selectedPatient.rh)
				interface.comboBox_7.setCurrentIndex(self.selectedPatient.groupage)
				interface.comboBox_8.setCurrentIndex(self.selectedPatient.radiotherapie)
				interface.doubleSpinBox.setValue(self.selectedPatient.poids)
				interface.spinBox.setValue(self.selectedPatient.taille)
				interface.dateEdit.setDate(date_it(self.selectedPatient.date_naissance))
				interface.dateEdit_2.setDate(date_it(self.selectedPatient.date_entree))
				interface.dateEdit_3.setDate(date_it(self.selectedPatient.fin) if self.selectedPatient.fin != "" else date.today())
				interface.dateEdit_4.setDate(date_it(self.selectedPatient.debut)if self.selectedPatient.fin != "" else date.today())

			else:
				interface.spinBox_2.setValue(self.IdPatient)
				interface.lineEdit.setText("")
				interface.lineEdit_2.setText("")
				interface.lineEdit_3.setText("")
				interface.lineEdit_4.setText("")
				interface.lineEdit_5.setText("")
				interface.comboBox_9.setCurrentIndex(0)
				interface.comboBox.setCurrentIndex(0)
				interface.comboBox_6.setCurrentIndex(0)
				interface.comboBox_7.setCurrentIndex(0)
				interface.comboBox_8.setCurrentIndex(0)
				interface.doubleSpinBox.setValue(0)
				interface.spinBox.setValue(0)
				interface.dateEdit.setDate(date.today())
				interface.dateEdit_2.setDate(date.today())
				interface.dateEdit_3.setDate(date.today())
				interface.dateEdit_4.setDate(date.today())

			table = interface.tableWidget_2	
			if(self.selectedPatient):
				self.sessionList = self.core._ALL_PATIENT_SESSIONS(self.selectedPatient.ID)
				
			cnt = len(self.sessionList)
			
			table.setRowCount(cnt)
			for r in range(cnt):
				items = [QTableWidgetItem(str(self.sessionList[r].ID)),
				 QTableWidgetItem(str(self.sessionList[r].date_seance)), 
				 QTableWidgetItem(self.sessionList[r].TYPE_TRAITEMENT()),
				 QTableWidgetItem(str(self.sessionList[r].details))]
				for c in range(4):
					items[c].setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)
					table.setItem(r,c, items[c])


			table2 = interface.tableWidget
			if(self.selectedPatient):
				self.testList = self.core._ALL_PATIENT_TESTS(self.selectedPatient.ID)
			
			cnt = len(self.testList)
			table2.setRowCount(cnt)
			for r in range(cnt):
				items = [QTableWidgetItem(str(self.testList[r].ID)),
				QTableWidgetItem(str(self.testList[r].date_test)), 
				QTableWidgetItem(self.testList[r].type),
				QTableWidgetItem(str(self.testList[r].details))]
				for c in range(4):
					items[c].setTextAlignment(PyQt5.QtCore.Qt.AlignHCenter)
					table2.setItem(r,c, items[c])

		if index == 7:
			if self.selectedDoctor != None:		
				interface.lineEdit_10.setText(self.selectedDoctor.nom)
				interface.lineEdit_8.setText(self.selectedDoctor.prenom)
				interface.lineEdit_7.setText(self.selectedDoctor.nom_utilisateur)
				interface.lineEdit_6.setText(self.selectedDoctor.mdp)
				interface.comboBox_10.setCurrentIndex(self.selectedDoctor.unite  - 1)
				interface.comboBox_5.setCurrentIndex(int(self.selectedDoctor.grade)  - 1)
				interface.lineEdit_11.setText(self.selectedDoctor.num_tele)
			else:
				interface.lineEdit_10.setText("")
				interface.lineEdit_8.setText("")
				interface.lineEdit_7.setText("")
				interface.lineEdit_6.setText("")
				interface.comboBox_10.setCurrentIndex(0)
				interface.comboBox_5.setCurrentIndex(0)
				interface.lineEdit_11.setText("")

		if index == 8:
			if self.selectedSession != None:
				if(self.selectedPatient):
					interface.spinBox_4.setValue(self.selectedPatient.ID)
				else: interface.spinBox_4.setValue(0)
				interface.dateEdit_5.setDate(date_it(self.selectedSession.date_seance))
				interface.doubleSpinBox_2.setValue(self.selectedSession.poids)
				interface.comboBox_15.setCurrentIndex(self.selectedSession.unite  - 1)
				interface.comboBox_13.setCurrentIndex(int(self.selectedSession.type_traitement)  - 1)
				interface.comboBox_18.setCurrentIndex(self.selectedSession.seance_faite  - 1)
			
			else:
				if(self.selectedPatient):
					interface.spinBox_4.setValue(self.selectedPatient.ID)
				else: interface.spinBox_4.setValue(0)
				interface.dateEdit_5.setDate(date_it("2000-01-01"))
				interface.doubleSpinBox_2.setValue(0)
				interface.comboBox_15.setCurrentIndex(0)
				interface.comboBox_13.setCurrentIndex(0)
				interface.comboBox_18.setCurrentIndex(0)
		
		if index == 9:
			if self.selectedTest != None:
				interface.dateEdit_6.setDate(date_it(self.selectedTest.date_test))
				interface.lineEdit_9.setText(self.selectedTest.type)
				interface.textEdit.setText(self.selectedTest.details)	
			
			else:
				interface.dateEdit_6.setDate(date_it("2000-01-01"))
				interface.lineEdit_9.setText("")
				interface.textEdit.setText("")

	@handleError
	def showPatientData(self):
		interface = self.screens["Acceuil"]
		r = interface.mainPatientList.currentRow()
		patient = [p for p in self.patientList if p.ID == int(interface.mainPatientList.item(r, 0).text().replace("/", ""))][0]
		self.selectedPatient = patient
		interface.changeSubWindow(self, 6, 0)

	@handleError
	def resetPatientData(self):
		interface = self.screens["Acceuil"]
		interface.spinBox_2.setValue(0)
		interface.lineEdit.setText(None)
		interface.lineEdit_2.setText(None)
		interface.lineEdit_3.setText(None)
		interface.lineEdit_4.setText(None)
		interface.lineEdit_5.setText(None)
		interface.comboBox_9.setCurrentIndex(0)
		interface.comboBox.setCurrentIndex(0)
		interface.comboBox_6.setCurrentIndex(0)
		interface.comboBox_7.setCurrentIndex(0)
		interface.comboBox_8.setCurrentIndex(0)
		interface.doubleSpinBox.setValue(0)
		interface.spinBox.setValue(0)
		interface.dateEdit.setDate(date_it("2000-01-01"))
		interface.dateEdit_2.setDate(date_it("2000-01-01"))
		interface.dateEdit_3.setDate(date_it("2000-01-01"))
		interface.dateEdit_4.setDate(date_it("2000-01-01"))

	@handleError
	def showDoctorData(self, me=False):
		interface = self.screens["Acceuil"]
		if(me):
			self.selectedDoctor = self.user
		else: 
			r = interface.medecinListe.currentRow()
			patient = [p for p in self.doctorList if p.ID == int(interface.medecinListe.item(r, 5).text())][0]
			self.selectedDoctor = patient
		interface.changeSubWindow(self, 7, 0)

	@handleError
	def resetDoctorData(self):
		interface = self.screens["Acceuil"]
		interface.lineEdit_10.setText(None)
		interface.lineEdit_8.setText(None)
		interface.lineEdit_7.setText(None)
		interface.lineEdit_6.setText(None)
		interface.comboBox_10.setCurrentIndex(0)
		interface.comboBox_5.setCurrentIndex(0)
		interface.lineEdit_11.setText(None)

	@handleError
	def showSessionData(self, index=6):
		interface = self.screens["Acceuil"]
		if index == 6:
			r = interface.tableWidget_2.currentRow()
			session = [p for p in self.sessionList if p.ID == int(interface.tableWidget_2.item(r, 0).text().replace("/", ""))][0]
			self.selectedSession = session
			self.openSessionInfoDialog()
		elif index == 1:
			r = interface.tableRendezVous.currentRow()
			session = [p for p in self.sessionList if p.ID == int(interface.tableRendezVous.item(r, 6).text())][0]
			self.selectedSession = session
			self.selectedPatient = self.core._SELECT_PATIENT(self.selectedSession.ID_patient)[0]
			self.openSessionInfoDialog()

		elif index == 0:
			r = interface.mainToDayList.currentRow()
			session = [p for p in self.sessionList if p.ID == int(interface.mainToDayList.item(r, 6).text())][0]
			self.selectedSession = session
			self.selectedPatient = self.core._SELECT_PATIENT(self.selectedSession.ID_patient)[0]
			self.openSessionInfoDialog()

	@handleError			
	def resetSessionData(self):
		interface = self.screens["Acceuil"]
		if(self.selectedPatient):
			interface.spinBox_4.setValue(int(self.selectedPatient.ID))
		else: interface.spinBox_4.setValue(0)
		interface.dateEdit_5.setDate(date_it("2000-01-01"))
		interface.doubleSpinBox_2.setValue(0)
		interface.comboBox_15.setCurrentIndex(0)
		interface.comboBox_13.setCurrentIndex(0)
		interface.comboBox_18.setCurrentIndex(0)
	
	@handleError		
	def showTestData(self):
		interface = self.screens["Acceuil"]
		r = interface.tableWidget.currentRow()
		test = [p for p in self.testList if p.ID == int(interface.tableWidget.item(r, 0).text().replace("/", ""))][0]
		self.selectedTest = test
		interface.changeSubWindow(self, 9, 0)
	
	@handleError	
	def resetTestData(self):
		interface = self.screens["Acceuil"]
		interface.dateEdit_6.setDate(date_it("2000-01-01"))
		interface.lineEdit_9.setText("")
		interface.textEdit.setText("")
	
	@handleError
	def confirmDeletion(self, index):
		self.dialogCont = QDialog()
		self.dialog = DeletionConfirm()
		self.dialog.setupUi(self.dialogCont, self, index)
		self.dialogCont.exec()
		self.goBack()
		return
	
	@handleError
	def deletePatient(self):
		self.core._DELETE_PATIENT(self.selectedPatient.ID)
		self.dialogCont.close()

	@handleError
	def deleteDoctor(self):
		self.core._DELETE_USER(self.selectedDoctor.ID)
		self.dialogCont.close()

	@handleError
	def deleteSession(self):
		self.core._DELETE_SESSION(self.selectedSession.ID)
		self.dialogCont.close()
	
	@handleError
	def deleteTest(self):
		self.core._DELETE_TEST(self.selectedTest.ID)
		self.dialogCont.close()
	
	@handleError
	def openPathologiesList(self, index=0):
		#the index: 0-> read only, 1-> edit
		self.pathologiesDialogCont = QDialog()
		self.pathologiesDialog = PathologiesDialog()
		self.pathologiesDialog.setupUi(self.pathologiesDialogCont, self, index)
		self.pathologiesDialogCont.exec()
	
	@handleError
	def loadPathologies(self, combobox):
		global _DATA_BASE
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()
		cr.execute("select * from Pathologies")
		l = cr.fetchall()
		combobox.addItem("Choisir une pathologie")
		for i in l:
			combobox.addItem(i[3]+" - "+i[1]+i[2])
	
	@handleError
	def selectPathologies(self):
		picker = self.pathologiesDialog
		self.pathologiesList = []
		for i in range(picker.listWidget.count()):
			e = picker.listWidget.item(i).text()
			self.pathologiesList.append(e[e.index("\t"):]+"/")
		self.pathologiesDialogCont.close()

	@handleError
	def openMedicineList(self, index=0):
		#the index: 0-> read only, 1-> edit
		self.medicineDialogCont = QDialog()
		self.medicineDialog = MedicineDialog()
		self.medicineDialog.setupUi(self.medicineDialogCont, self, index)
		self.medicineDialogCont.exec()
	
	@handleError
	def openSessionInfoDialog(self):
		self.sessionInfoDialogCont = QDialog()
		self.sessionInfoDialog = SessionInfoDialog()
		self.sessionInfoDialog.setupUi(self.sessionInfoDialogCont, self)
		self.sessionInfoDialogCont.exec()
	
	@handleError
	def loadMedicines(self):
		combobox = self.medicineDialog.comboBox
		db = sqlite3.connect(_DATA_BASE)
		cr = db.cursor()

		cr.execute("select * from Medicaments")
		fetched = sorted(list(set([x[1] for x in cr.fetchall()])))
		combobox.addItem("Choisir un médicament")
		for i in fetched:
			combobox.addItem(i)
	
	@handleError
	def loadForms(self):
		val = self.medicineDialog.comboBox.currentText()
		combobox = self.medicineDialog.comboBox_2
		combobox.clear()
		if val != "Choisir un médicament":
			l = self.core.getForms(val)
			#print(l)
			for i in l:
				combobox.addItem(i)
		combobox.setCurrentIndex(0)
	
	@handleError
	def selectMedicine(self):
		l = self.medicineDialog.listWidget
		res = ""
		for i in range(l.count()):
			x = l.item(i).text()
			if (y:=x[:x.index("\t")])not in res:
				res += y+"/"
		self.medicinesList = res
		self.medicineDialogCont.close()


main = Main()
main.run()
