# VAC Monitor (demo program)
# by Duncan Butler with lots of help from Micah Barnes
# Monitors PVs for the beamline and turns them red if out of tolerance
# April 2019
# Put together in python3

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import epics
from functools import partial
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class main(QtWidgets.QMainWindow):
	def __init__(self):
		
		plt.axis()
		plt.figure()
		
		# Inititate UI.
		QtWidgets.QMainWindow.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		# Set up the epics PV's
		self.setupEpics()
		window = QtWidgets.QWidget()
		# Create a layout
		layout = QtWidgets.QVBoxLayout()
		
        #DB edits here...bit of a hack...
		headerWidget = QtWidgets.QWidget()         
		headerLayout = QtWidgets.QHBoxLayout()        
		Head1 = QtWidgets.QLabel("PV")
		Head2 = QtWidgets.QLabel("Description")
		Head3 = QtWidgets.QLabel("Actual")
		#Head4 = QtWidgets.QLabel("OK/FAIL")
		Head1.setMinimumWidth(120)
		Head2.setMinimumWidth(120)
		Head3.setMinimumWidth(80)
		#Head4.setMinimumWidth(80)

		#titleLayout.setContentsMargins(0,0,0,0)		
		headerLayout.addWidget(Head1)
		headerLayout.addWidget(Head2)
		headerLayout.addWidget(Head3)
		#headerLayout.addWidget(Head4)
		headerWidget.setLayout(headerLayout)
		#now add it to the overall layout...
		layout.addWidget(headerWidget)
		
		# Add groups one at a time
		for name, pvs in self.groupList.items():
			group = QtWidgets.QGroupBox(name)
			groupBoxLayout = QtWidgets.QVBoxLayout()
			# Scan through for each epics item in the group.
			for pv, values in pvs.items():
				# Create new widget for each PV (a row of widgets).
				statusWidget = QtWidgets.QWidget()
				# Create layout for status widget.
				statusWidgetLayout = QtWidgets.QHBoxLayout()
				statusWidgetLayout.setContentsMargins(0,0,0,0)
				# Create individual widgets for status widget.
				labelPV = QtWidgets.QLabel(str(pv))
				labelPV.setMinimumWidth(400)
				labelText = QtWidgets.QLabel(str(values[0]))
				labelText.setMinimumWidth(120)
				#labelBCT_VAL = QtWidgets.QLabel(str(values[1]))
				#labelBCT_VAL.setMinimumWidth(120)
				labelRBV = QtWidgets.QLabel('-1')
				labelRBV.setMinimumWidth(80)
				#button = QtWidgets.QPushButton('-')
				self.widgetList[pv] = [labelPV, labelText, labelRBV]
				# Add widgets to status widget.
				statusWidgetLayout.addWidget(labelPV)
				statusWidgetLayout.addWidget(labelText)
				#statusWidgetLayout.addWidget(labelBCT_VAL)
				statusWidgetLayout.addWidget(labelRBV)
				#statusWidgetLayout.addWidget(button)
				statusWidget.setLayout(statusWidgetLayout)
				# Add widgets to screen.
				# layout.addWidget(statusWidget)
				groupBoxLayout.addWidget(statusWidget)
			# Set layout for the whole group.
			group.setLayout(groupBoxLayout)
			layout.addWidget(group)
		# Set window layout.
		window.setLayout(layout)
		# Give the application the window widget.
		self.setCentralWidget(window)
		# Set a timer to update GUI every 1 second.
		timer = QtCore.QTimer(self) #must put the self argument in here!
		timer.setInterval(5000)
		timer.timeout.connect(self.tick)
		timer.start()
		
		#setup history arrays
		self.history = []
		self.histtime = []

		# Connect epics.
		for name, pvs in self.groupList.items():
			for pv, values in pvs.items():
				print("PV to follow = %s : %s : %s" % (name,pv,values))
				# epics.camonitor(pv,callback=partial(self.updateValue)) #doesnt work :(
				#epics.PV(pv,auto_monitor=True,callback=partial(self.updateValue))

	# Callback function every time the PV value changes
	"""
	def updateValue(self,**kwargs):
		value = round(kwargs.get('value',-1),3)
		pvname = kwargs.get('pvname','None')
		units = kwargs.get('units',' ')
		self.widgetList[pvname][3].setText(format(value,'.3f'))
		print("Value changed = ", value,self.widgetList[pvname][3].text())
		# Update button text.
		if  (value > self.widgetList[pvname][5][2]) & (value < self.widgetList[pvname][5][3]):
			self.widgetList[pvname][4].setText('OK')
			self.widgetList[pvname][4].setStyleSheet("background-color: green")
		else:
			self.widgetList[pvname][4].setText('FAIL')
			self.widgetList[pvname][4].setStyleSheet("background-color: red")
		#time.sleep(0.3) causes a crash!!! WTF?
		app.processEvents() 
	"""

	def tick(self):
		tm = str(datetime.now())
		print("Time = ",tm)
		for name, pvs in self.groupList.items():
			for pv, values in pvs.items():
				val=epics.caget(pv)
				#print("%s : %s : %s = %s" % (name,pv,values,str(val)))
				self.widgetList[pv][2].setText(format(val,'.3f'))
				if(pv=='SR11BCM01:CURRENT_MONITOR.VAL'):
					self.history.append(val)
					self.histtime.append(tm)
					plt.scatter(self.histtime,self.history)
					plt.show()
					
		
	def setupEpics(self):
		# PV_NAME, BCT_VAL, MIN, MAX
		self.groupList = {}
		# self.statusList = {}
		
		#Storage ring, wiggler, mono
		vacuum = {}
		vacuum['SR08SCW01:FIELD_MONITOR.VAL'] = ['Wiggler Field']
		vacuum['SR11BCM01:CURRENT_MONITOR.VAL'] = ['Ring Current']
		vacuum['SR00:BEAM_ENERGY_MONITOR.VAL'] = ['Electron Energy']

		#Beamline
		waterflows = {}
		waterflows['SR08ID01PSS01:FES_EPS_ENABLE_STS'] = ['Beamline']
		waterflows['SR08ID01PSS01:HU01A_MON_SHT_MOD_PERM_STS'] = ['Shutter Mode']
		waterflows['SR08ID01TBL21:Z.VAL'] = ['Mama Table 2A']
		waterflows['SR08ID01DCM01:BRAGG1.VAL'] = ['Mono Bragg 1']
		waterflows['SR08ID01DCM01:BRAGG2.VAL'] = ['Mono Bragg 2']
		waterflows['SR08ID01DCM01:X.VAL'] = ['Mono X']
		#beamline['SR00:BEAM_ENERGY_MONITOR.VAL'] = ['Electron Energy','3 GeV',3.01,3.05]

		#Filters
		heflows = {}
		heflows['SR08ID01FR01:PDL01.VAL'] = ['Paddle 1']
		heflows['SR08ID01FR01:PDL02.VAL'] = ['Paddle 2']
		heflows['SR08ID01FR01:PDL03.VAL'] = ['Paddle 3']
		heflows['SR08ID01FR01:PDL04.VAL'] = ['Paddle 4']
		heflows['SR08ID01FR01:PDL05.VAL'] = ['Paddle 5']




		# Add groups to list.
		self.groupList['Vaccum'] = vacuum
		self.groupList['Cooling water'] = waterflows
		self.groupList['He flows'] = heflows


		#beamline
		#self.statusList['SR08ID01PSS01:HU01A_MON_SHT_MOD_PERM_STS'] = ['Shutter mode','Mono',0.999,1.001] #need a boolean type
		
		self.widgetList = {}




if __name__ == "__main__":
	# QApp 
	app = QtWidgets.QApplication(sys.argv)
	# QWidget (MainWindow).
	window = main()
	window.show()
	# App wide event filter.
	app.installEventFilter(window)

	sys.exit(app.exec_())

