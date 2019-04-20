# VAC Monitor (demo program)
# by Duncan Butler with lots of help from Micah Barnes
# Monitors PVs for the beamline and turns them red if out of tolerance
# April 2019
# Put together in python3

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import epics
import random
from functools import partial
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from numpy import arange, sin, pi


class MyMplCanvas(FigureCanvas):
	"""Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		
		# We want the axes cleared every time plot() is called
		#self.axes.hold(False)
		
		self.compute_initial_figure()

		#
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self,
				QtWidgets.QSizePolicy.Expanding,
				QtWidgets.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

	def compute_initial_figure(self):
		pass

class MyStaticMplCanvas(MyMplCanvas):
	"""Simple canvas with a sine plot."""
	def compute_initial_figure(self):
		t = arange(0.0, 3.0, 0.01)
		s = sin(2*pi*t)
		self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
	"""A canvas that updates itself every ~seconds."""
	def __init__(self, *args, **kwargs):
		MyMplCanvas.__init__(self, *args, **kwargs)
		timer = QtCore.QTimer(self)
		timer.timeout.connect(self.update_figure)
		timer.start(5000)
		
	def compute_initial_figure(self):
		#self.data_x.append(0.0)
		#self.data_y.append(0.0)
		#self.data_x.append(1.0)
		#self.data_y.append(1.0)
		#self.axes.plot(self.data_x, self.data_y, 'r')
		return

	def update_figure(self):
		return
		#self.axes.plot(self.data_x,self.data_y, 'r',color='green', linewidth=1)
		#self.draw()
		


class main(QtWidgets.QMainWindow):
	def __init__(self):
	
		
		# Inititate UI.
		QtWidgets.QMainWindow.__init__(self)
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		# Set up the epics PV's
		self.setupEpics()
		window = QtWidgets.QWidget()
		
		# Create overall, and L and R layouts
		layout = QtWidgets.QHBoxLayout()
		layoutLeft = QtWidgets.QVBoxLayout()
		layoutRight= QtWidgets.QVBoxLayout()
		widgetLeft = QtWidgets.QWidget()
		widgetRight = QtWidgets.QWidget()
		
		# a figure instance to plot on
		self.figureV = plt.figure()
		self.figureW = plt.figure()
		self.figureH = plt.figure()
	
		#arrays for the data
		self.data_t=[]		#an array for the time
		self.data_y=dict() #a dictionary of y value arrays, one for each PV
		
		# this is the Canvas Widget that displays the `figure`
		# it takes the `figure` instance as a parameter to __init__
		self.canvasV = FigureCanvas(self.figureV)
		self.canvasW = FigureCanvas(self.figureW)
		self.canvasH = FigureCanvas(self.figureH)

		self.vac = MyDynamicMplCanvas(self.canvasV, width=5, height=4, dpi=100)
		self.wat = MyDynamicMplCanvas(self.canvasW, width=5, height=4, dpi=100)
		self.hel = MyDynamicMplCanvas(self.canvasH, width=5, height=4, dpi=100)
		#hel.axis.plot(x, y, 'c', linewidth=3.3)
				
		# this is the Navigation widget
		# it takes the Canvas widget and a parent
		#self.toolbar = NavigationToolbar(self.canvasV, self)

		layoutRight.addWidget(self.vac)
		layoutRight.addWidget(self.wat)
		layoutRight.addWidget(self.hel)
		
		
		# Add groups one at a time
		for name, pvs in self.groupList.items():
			group = QtWidgets.QGroupBox(name)
			groupBoxLayout = QtWidgets.QVBoxLayout()
			# Scan through for each epics item in the group.
			for pv, values in pvs.items():
				self.data_y.setdefault(pv, []) #should create empty array for each PV
				# Create new widget for each PV (a row of widgets).
				statusWidget = QtWidgets.QWidget()
				# Create layout for status widget.
				statusWidgetLayout = QtWidgets.QHBoxLayout()
				statusWidgetLayout.setContentsMargins(0,0,0,0)
				# Create individual widgets for status widget.
				labelPV = QtWidgets.QLabel(str(pv))
				labelPV.setMinimumWidth(400)
				labelPV.setStyleSheet('color: '+pvs[pv][1])
				labelText = QtWidgets.QLabel(str(values[0]))
				labelText.setStyleSheet('color: '+pvs[pv][1])
				labelText.setMinimumWidth(120)
				labelText.setToolTip(str(pv))
				#labelBCT_VAL = QtWidgets.QLabel(str(values[1]))
				#labelBCT_VAL.setMinimumWidth(120)
				labelRBV = QtWidgets.QLabel('-1')
				labelRBV.setMinimumWidth(80)
				labelRBV.setStyleSheet('color: '+pvs[pv][1])
				#button = QtWidgets.QPushButton('-')
				self.widgetList[pv] = [labelPV, labelText, labelRBV]
				# Add widgets to status widget.
				#statusWidgetLayout.addWidget(labelPV)
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
			layoutLeft.addWidget(group)
		# Set window layout.
		widgetLeft.setLayout(layoutLeft)
		widgetRight.setLayout(layoutRight)
		layout.addWidget(widgetLeft)
		layout.addWidget(widgetRight)
		window.setLayout(layout)
		# Give the application the window widget.
		self.setCentralWidget(window)
		
		# Set a timer to update GUI every 1 second.
		timer = QtCore.QTimer(self) #must put the self argument in here!
		timer.setInterval(2000)
		timer.timeout.connect(self.tick)
		timer.start()

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
		tm = datetime.now()
		print("Time = ",str(tm))
		self.data_t.append( tm.strftime("%H:%M:%S"))
		for name, pvs in self.groupList.items():
			for pv, values in pvs.items():
				#val=epics.caget(pv)
				val = random.random()
				print("%s : %s : %s = %s" % (name,pv,values,str(val)))
				self.widgetList[pv][2].setText(format(val,'.3f'))
				self.data_y[pv].append(val)
				if name=='Vacuum':
					self.vac.axes.plot(self.data_t,self.data_y[pv], 'r',color=pvs[pv][1], linewidth=1)
					self.vac.axes.xaxis.set_major_locator(plt.MaxNLocator(10))
					self.vac.draw()
				if name=='Cooling water':
					self.wat.axes.plot(self.data_t,self.data_y[pv], 'r',color=pvs[pv][1], linewidth=1)
					self.wat.axes.xaxis.set_major_locator(plt.MaxNLocator(10))
					self.wat.draw()
				if name=='Helium flows':
					self.hel.axes.plot(self.data_t,self.data_y[pv], 'r',color=pvs[pv][1], linewidth=1)
					self.hel.axes.xaxis.set_major_locator(plt.MaxNLocator(10))
					self.hel.draw()
		
	def setupEpics(self):
		# PV_NAME, Desctiption
		self.groupList = {}
		# self.statusList = {}
		
		#Storage ring, wiggler, mono
		vacuum = {}
		vacuum['SR08SCW01:FIELD_MONITOR.VAL'] = ['Wiggler Field','red']
		vacuum['SR11BCM01:CURRENT_MONITOR.VAL'] = ['Ring Current','orange']
		vacuum['SR00:BEAM_ENERGY_MONITOR.VAL'] = ['Electron Energy','purple']

		#Beamline
		waterflows = {}
		waterflows['SR08ID01PSS01:FES_EPS_ENABLE_STS'] = ['Beamline','green']
		waterflows['SR08ID01PSS01:HU01A_MON_SHT_MOD_PERM_STS'] = ['Shutter Mode','gray']
		waterflows['SR08ID01TBL21:Z.VAL'] = ['Mama Table 2A','blue']
		waterflows['SR08ID01DCM01:BRAGG1.VAL'] = ['Mono Bragg 1','lightblue']
		waterflows['SR08ID01DCM01:BRAGG2.VAL'] = ['Mono Bragg 2','lightgreen']
		waterflows['SR08ID01DCM01:X.VAL'] = ['Mono X','yellow']

		#Filters
		heflows = {}
		heflows['SR08ID01FR01:PDL01.VAL'] = ['Paddle 1','brown']
		heflows['SR08ID01FR01:PDL02.VAL'] = ['Paddle 2','black']
		heflows['SR08ID01FR01:PDL03.VAL'] = ['Paddle 3','cyan']
		heflows['SR08ID01FR01:PDL04.VAL'] = ['Paddle 4','pink']
		heflows['SR08ID01FR01:PDL05.VAL'] = ['Paddle 5','darkgreen']




		# Add groups to list.
		self.groupList['Vacuum'] = vacuum
		self.groupList['Cooling water'] = waterflows
		self.groupList['Helium flows'] = heflows


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

