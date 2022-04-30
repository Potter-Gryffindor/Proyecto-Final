# Importar Paquetes
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from pandas import read_csv
import numpy as np
import datetime
import time

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.ticker as ticker

# Funciones
def clickedAbout(Ui_AboutWindow):
    AboutWindow = QtWidgets.QDialog()
    AboutTab = Ui_AboutWindow()
    AboutTab.show()

# Clases
class Ui_AboutWindow(QtWidgets.QDialog):
    # Constructor
    def __init__(self):
        super(Ui_AboutWindow, self).__init__()
        self.__AboutWindow = uic.loadUi('../UI/About.ui', self)
        self.__AboutWindow.setFixedSize(400, 449)
        self.__AboutWindow.setWindowFlags(
        QtCore.Qt.Window |
        QtCore.Qt.CustomizeWindowHint |
        QtCore.Qt.WindowTitleHint |
        QtCore.Qt.WindowCloseButtonHint |
        QtCore.Qt.WindowStaysOnTopHint
        )

class Ui_RouteWindow(QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(Ui_RouteWindow, self).__init__()
        self.__RouteWindow = uic.loadUi('../UI/InterfaceRoute.ui', self)
        self.AboutTab = Ui_AboutWindow()
        self.routeData = read_csv('../Route/ROUTE-Template.csv')

        # Llamadas a Métodos
        ## Botones de Route Window  
        self.__RouteWindow.actionAbout.triggered.connect(self.clickedAbout)
        self.__RouteWindow.BusButton.clicked.connect(self.pressedBusButton)
        self.__RouteWindow.SearchFileButton.clicked.connect(self.__pressedSearchFileButton)
        self.__RouteWindow.SimulateFileButton.clicked.connect(self.__pressedSimulateFileButton)
        ## Setups Gráficas de Route Window
        self.__setupRouteFigures()
        
    # Métodos 
    ## Abrir Pestaña About
    def clickedAbout(self):
        self.AboutTab.show()    
    
    ## Cambiar a Bus Window 
    def pressedBusButton(self):
        widget.setCurrentIndex(1)
        self.AboutTab.close()

    ## Buscar y definir la extensión del archivo .CSV
    def __pressedSearchFileButton(self):
        (filename, extension) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '../Route/', filter=self.tr("csv file (*.csv)"))
        self.__RouteWindow.RouteFileLine.setText(filename)

    ## Leer y cargar el archivo .CSV
    def __pressedSimulateFileButton(self):
        csvFile = self.__RouteWindow.RouteFileLine.text()
        try:
            self.routeData = read_csv(csvFile)
        except:
            print('Not a valid data vector')
            return
        #print(self.routeData)
        self.__plotRoute()

    ## Definir Plots (MAPA Y PERFIL)
    def __setupRouteFigures(self):
        self.figureMapRoute = Figure(tight_layout=True)  
        self.figureProfRoute = Figure(tight_layout=True)  
        self.canvasMapRoute = FigureCanvas(self.figureMapRoute)  
        self.canvasProfRoute = FigureCanvas(self.figureProfRoute)
        self.toolbarMaproute = NavigationToolbar(self.canvasMapRoute, self)
        self.toolbarProfRoute = NavigationToolbar(self.canvasProfRoute, self)
        self.layoutMapRoute = QtWidgets.QVBoxLayout(self.__RouteWindow.RouteMapWidget)  
        self.layoutProfRoute = QtWidgets.QVBoxLayout(self.__RouteWindow.ProfileMapWidget)  
        self.layoutMapRoute.addWidget(self.toolbarMaproute)  
        self.layoutMapRoute.addWidget(self.canvasMapRoute)  
        self.layoutProfRoute.addWidget(self.toolbarProfRoute)  
        self.layoutProfRoute.addWidget(self.canvasProfRoute)  
        self.axMapRoute = self.figureMapRoute.add_subplot(111)  
        self.axProfRoute = self.figureProfRoute.add_subplot(111) 

    ## Plotear dos gráficas = Latitud vs Longitud / Altitud vs Distancia
    def __plotRoute(self):
        # Map Figure
        long = self.routeData[['LONG']]
        lat = self.routeData[['LAT']]
        self.axMapRoute.cla()
        self.axMapRoute.plot(long, lat, label='LONG-LAT')
        self.axMapRoute.set_title('Route Map',  fontsize=12, fontweight="bold")
        self.axMapRoute.set_xlabel('Longitude', fontsize=10, fontweight="bold")
        self.axMapRoute.set_ylabel('Latitude', fontsize=10, fontweight="bold")
        self.axMapRoute.tick_params(labelsize=8)
        self.axMapRoute.grid()
        self.canvasMapRoute.draw()
        
        # Profile Figure
        dist = self.routeData[['DIST']]
        alt = self.routeData[['ALT']]
        self.axProfRoute.cla()
        self.axProfRoute.plot(dist, alt, label='ALT')
        self.axProfRoute.set_title('Route Profile', fontsize=12, fontweight="bold")
        self.axProfRoute.set_xlabel('Distance [km]', fontsize=10, fontweight="bold")
        self.axProfRoute.set_ylabel('Altitude [m]', fontsize=10, fontweight="bold")
        self.axProfRoute.tick_params(labelsize=9)
        self.axProfRoute.grid()
        self.canvasProfRoute.draw()
        bus_stop = self.routeData[['BUS STOP']]
        label = self.routeData[['LABEL']]

        # Marcar Paradas
        countStops = 0;
        for n in range(0, len(bus_stop)):
            if bus_stop.iloc[n].values[0] == 1:
                countStops += 1    
                if (countStops == 1):
                    self.axMapRoute.plot(long.iloc[n].values[0], lat.iloc[n].values[0], label='STOP', marker='^', color='red')
                    self.axProfRoute.plot(dist.iloc[n].values[0], alt.iloc[n].values[0], label='STOP',marker='^', color='red')   
                else:
                    self.axMapRoute.plot(long.iloc[n].values[0], lat.iloc[n].values[0], marker='^', color='red')
                    self.axProfRoute.plot(dist.iloc[n].values[0], alt.iloc[n].values[0], marker='^', color='red')                     
                
                self.axMapRoute.annotate(label.iloc[n].values[0], (long.iloc[n].values[0], lat.iloc[n].values[0]), fontsize=7)
                self.axProfRoute.annotate(label.iloc[n].values[0], (dist.iloc[n].values[0], alt.iloc[n].values[0]), fontsize=7)

        self.axMapRoute.legend(frameon=False, loc='best')
        self.canvasMapRoute.draw()
        self.axProfRoute.legend(frameon=False, loc='best')
        self.canvasProfRoute.draw()

class Ui_BusWindow(Ui_RouteWindow, QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(Ui_BusWindow, self).__init__()
        self.__BusWindow = uic.loadUi('../UI/InterfaceBus.ui', self)
        self.__BusWindow.BusParametersTab.setCurrentIndex(0)
        self.__BusWindow.PeakTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.StartEndTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.PositionSpeedtabWidget.setCurrentIndex(0)

        # Llamadas a Métodos 
        ## Botones de Bus Window  
        self.__BusWindow.actionAbout.triggered.connect(self.clickedAbout)
        self.__BusWindow.RouteButton.clicked.connect(self.pressedRouteButton)
        self.PlotBusGenDataButton.clicked.connect(self.__pressedPlotBusGenDataButton)
        self.__BusWindow.GenOperationDiagramButton.clicked.connect(self.__pressedGenOperationDiagramButton)
        ## Setups Gráficas de Bus Window  
        self.__setupBusDataFigures()
        self.__setupOpDiagramFigures()

    # Métodos
    ## Cambiar a Route Window 
    def pressedRouteButton(self):
        widget.setCurrentIndex(0)
        self.AboutTab.close()

    ## Calcular y graficar Velocidad vs Tiempo / Distancia vs Tiempo
    def __pressedPlotBusGenDataButton(self):
        speedTable = self.SpeedCurveTable
        acceleration = float(speedTable.item(0, 0).text())
        braking = float(speedTable.item(1, 0).text())
        maxSpeed = float(speedTable.item(2, 0).text())
        
        t = np.array([0])
        speed = np.array([0])
        accel = np.array([0])
        decel = np.array([0])
        dist = np.array([0])
        deltaT = 0.5

        for _ in range(0, 600):
            t = np.append(t, t[-1] + deltaT)
            if t[-1] < 150:
                speed = np.append(speed, speed[-1] + acceleration * deltaT)
                if speed[-1] > maxSpeed / 3.6:
                    speed[-1] = maxSpeed / 3.6
                else:
                    accel = speed
                decel[0] = float(speed[-1])

            else:
                speed = np.append(speed, speed[-1] - braking * deltaT)
                if speed[-1] < 0:
                    speed[-1] = 0
                else:
                    decel = np.append(decel, speed[-1])

            dist = np.append(dist, dist[-1] + (speed[-1] + speed[-2]) * deltaT / 2)
        accel = np.append(accel, maxSpeed / 3.6)
        decel = np.append(decel, speed[-1])

        self.speedCurve = speed
        self.accelCurve = accel
        self.decelCurve = decel
        self.timeCurve = t
        self.distanceCurve = dist

        self.__plotBusData()

    #    # Calcular y graficar Curvas de Operación Distancia vs Tiempo / Velocidad vs Tiempo 
    def __pressedGenOperationDiagramButton(self):
        def state0func(inputTup):
            # State 0: Buses are not in operation
            timeVector, distVector, speedVector, deltaT, labelVector, stopVector = inputTup
            timeVector = np.append(timeVector, timeVector[-1] + deltaT)
            distVector = np.append(distVector, distVector[-1])
            speedVector = np.append(speedVector, 0)
            labelVector.append('')
            stopVector.append(0)
            outTup = (timeVector, distVector, speedVector, labelVector, stopVector)
            return (outTup)

        def state1func(inputTup):
            # State 1: Buses are stopped
            timeVector, distVector, speedVector, deltaT, labelVector, stopVector, labelStop = inputTup
            timeVector = np.append(timeVector, timeVector[-1] + deltaT)
            distVector = np.append(distVector, distVector[-1])
            speedVector = np.append(speedVector, 0)
            labelVector.append(labelStop)
            stopVector.append(1)
            outTup = (timeVector, distVector, speedVector, labelVector, stopVector)
            if tIniPico1 < timeVector[-1] <= tEndPico1 or tIniPico2 < timeVector[-1] < tEndPico2:
                if distVector[-1] == 0:
                    stopDelay=100

            return (outTup)

        def state2func(inputTup):
            # State 2: buses are accelerating
            timeVector, distVector, speedVector, deltaT, accelBus, indexAccel, labelVector, stopVector = inputTup
            timeVector = np.append(timeVector, timeVector[-1] + deltaT)
            speedVector = np.append(speedVector, accelBus[indexAccel])
            distVector = np.append(distVector, distVector[-1] + (speedVector[-1] + speedVector[-2]) * 0.5 * deltaT)
            labelVector.append('')
            stopVector.append(0)
            indexAccel += 1
            outTup = (timeVector, distVector, speedVector, indexAccel, labelVector, stopVector)

            return (outTup)

        def state3func(inputTup):  
            # State 3: Constant speed
            timeVector, distVector, speedVector, deltaT, maxSpeedBus, labelVector, stopVector = inputTup
            timeVector = np.append(timeVector, timeVector[-1] + deltaT)
            speedVector = np.append(speedVector, maxSpeedBus)
            distVector = np.append(distVector, distVector[-1] + (speedVector[-1] + speedVector[-2]) * 0.5 * deltaT)
            labelVector.append('')
            stopVector.append(0)
            outTup = (timeVector, distVector, speedVector, labelVector, stopVector)
            return (outTup)

        def state4func(inputTup):  
            # State 4: Decelerating
            timeVector, distVector, speedVector, deltaT, decelBus, indexDecel, labelVector, stopVector = inputTup
            timeVector = np.append(timeVector, timeVector[-1] + deltaT)
            speedVector = np.append(speedVector, decelBus[indexDecel])
            distVector = np.append(distVector, distVector[-1] + (speedVector[-1] + speedVector[-2]) * 0.5 * deltaT)
            labelVector.append('')
            stopVector.append(0)

            indexDecel += 1
            outTup = (timeVector, distVector, speedVector, indexDecel, labelVector, stopVector)

            return (outTup)

        def findNextStop(indexStop, busStopRoute):
            busStop1 = indexStop
            while 1:
                indexStop = indexStop + 1
                if indexStop > len(busStopRoute):
                    busStop2 = []
                    break
                if busStopRoute.iloc[indexStop].values[0] == 1:
                    busStop2 = indexStop
                    break
            outTup = (busStop1, busStop2)

            return (outTup)

        def calculateBrakingDistance(decelBus, deltaT):
            distBrake = 0
            n = 1
            for n in range(0, len(decelBus)):
                #distBrake=distBrake+(decelBus[n]+decelBus[n-1])*0.5*deltaT
                distBrake = distBrake + (decelBus[n]) * deltaT

            return (distBrake)

        # Route parameters
        self.distRoute = RouteWindow.routeData[['DIST']]
        self.busStopRoute = RouteWindow.routeData[['BUS STOP']]
        self.labelRoute = RouteWindow.routeData[['LABEL']]
        
        # Fleet parameters
        fleetTable = self.__BusWindow.FleetParametersTable
        stopDelay = float(fleetTable.item(4, 0).text())
        TimeInTerminal = float(fleetTable.item(5, 0).text())
        tIniFleetQt = self.__BusWindow.STFtimeEdit.time()
        tIniFleet = tIniFleetQt.hour() * 3600 + tIniFleetQt.minute() * 60 + tIniFleetQt.second()
        tEndFleetQt = self.__BusWindow.ETFtimeEdit.time()
        tEndFleet = tEndFleetQt.hour() * 3600 + tEndFleetQt.minute() * 60 + tEndFleetQt.second()
        tIniPico1Qt = self.__BusWindow.STPtimeEdit.time()
        tIniPico1 = tIniPico1Qt.hour() * 3600 + tIniPico1Qt.minute() * 60 + tIniPico1Qt.second()
        tEndPico1Qt = self.__BusWindow.ETPtimeEdit.time()
        tEndPico1 = tEndPico1Qt.hour() * 3600 + tEndPico1Qt.minute() * 60 + tEndPico1Qt.second()

        tIniPico2Qt = self.__BusWindow.STMPtimeEdit.time()
        tIniPico2 = tIniPico2Qt.hour() * 3600 + tIniPico2Qt.minute() * 60 + tIniPico2Qt.second()
        tEndPico2Qt = self.__BusWindow.EMPtimeEdit.time()
        tEndPico2 = tEndPico2Qt.hour() * 3600 + tEndPico2Qt.minute() * 60 + tEndPico1Qt.second()
        numBuses = int(fleetTable.item(6, 0).text())
        dispatchFrequency = int(fleetTable.item(7, 0).text())
        numBusesPeak = int(fleetTable.item(0, 0).text())
        dispatchFrequencyPeak = int(fleetTable.item(3, 0).text())

        # Simulation parameters
        deltaT = 0.2
        maxTime = tEndFleet - (numBuses - 1) * dispatchFrequency
        #maxTime2 = t2EndFleet - (numBusesPeak - 1) * dispatchFrequencyPeak

        ## Bus parameters
        accelBus = self.speedCurve
        decelBus = self.decelCurve
        distBrake = calculateBrakingDistance(decelBus, deltaT)
        maxSpeedBus = accelBus[-1]

        # Initial conditions
        state = 0
        indexStop = 0

        self.timeVector = np.array([tIniFleet])
        self.distVector = np.array([0])
        self.labelVector = ['']
        self.stopVector = [0]
        self.speedVector = np.array([0])
        self.stateVector = []
        timeState0 = 0

        while 1:

            self.stateVector.append(state)
            if state == 0:

                inputTup = (self.timeVector, self.distVector, self.speedVector, deltaT, self.labelVector, self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, self.labelVector, self.stopVector) = state0func(inputTup)

                if self.timeVector[-1] >= tIniFleet:
                    if self.timeVector[-1] <= tEndFleet:
                        state = 1
                        timeState1 = self.timeVector[-1]

            elif state == 1:
                labelStop = self.labelRoute.iloc[indexStop].values[0]
                inputTup = (self.timeVector, self.distVector, self.speedVector, deltaT, self.labelVector, self.stopVector, labelStop)
                (self.timeVector, self.distVector, self.speedVector, self.labelVector, self.stopVector) = state1func(inputTup)

                # Cambio de Velocidad de la Flota en tiempo pico
                if (tIniPico1 < self.timeVector[-1] <= tEndPico1 and self.distVector[-1] == 0) or (tIniPico2 < self.timeVector[-1] < tEndPico2 and self.distVector[-1] == 0):
                    stopDelay = dispatchFrequencyPeak
                    state = 1
                elif (tIniPico1 < self.timeVector[-1] <= tEndPico1 ) or (tIniPico2 < self.timeVector[-1] < tEndPico2):
                    stopDelay = float(fleetTable.item(4, 0).text()) + 33
                    state=1
                elif self.distVector[-1] == 0:
                    stopDelay = TimeInTerminal
                    state = 1
                else:
                    stopDelay=float(fleetTable.item(4, 0).text())
                    state = 1

                if self.timeVector[-1] >= timeState1 + stopDelay:
                    state = 2
                    timeState2 = self.timeVector[-1]
                    distState2 = self.distVector[-1]
                    indexAccel = 1
                    busStop1, busStop2 = findNextStop(indexStop, self.busStopRoute)
                    distStops = 1000 * (self.distRoute.iloc[busStop2].values[0] - self.distRoute.iloc[busStop1].values[0])
                    distStopsAccum = distStops
                    indexStop = busStop2

            elif state == 2:

                inputTup = (self.timeVector, self.distVector, self.speedVector, deltaT, accelBus, indexAccel, self.labelVector, self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, indexAccel, self.labelVector, self.stopVector) = state2func(inputTup)

                if self.speedVector[-1] == maxSpeedBus:
                    state = 3
                    timeState3 = self.timeVector[-1]


            elif state == 3:
                inputTup = (self.timeVector, self.distVector, self.speedVector, deltaT, maxSpeedBus, self.labelVector, self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, self.labelVector, self.stopVector) = state3func(inputTup)

                if self.distVector[-1] - distState2 >= distStops - distBrake:
                    state = 4
                    timeState4 = self.timeVector[-1]
                    indexDecel = 1

            elif state == 4:
                inputTup = (self.timeVector, self.distVector, self.speedVector, deltaT, decelBus, indexDecel, self.labelVector, self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, indexDecel, self.labelVector, self.stopVector) = state4func(inputTup)

                if self.speedVector[-1] == 0:
                    state = 1
                    timeState1 = self.timeVector[-1]

                    if busStop2 == len(self.busStopRoute) - 1:
                        indexStop = 0
                        self.distVector[-1] = 0
                        distStopsAccum = 0

            else:
                pass
            self.__BusWindow.BusprogressBar.setValue(int(100 * self.timeVector[-1] / maxTime))

            if self.timeVector[-1] > maxTime:
                break

        self.timeVectorDT = []
        timeZoneColombia = 3600 * 5

        for n in range(0, len(self.timeVector)):
            self.timeVectorDT.append(datetime.datetime.fromtimestamp(self.timeVector[n] + timeZoneColombia))

        self.arrayTime = []

        for y in range(numBuses):
            time_arr = []
            time_ = []
            #print("Numero de bus:"+str(y))
            for idx, x in enumerate(self.timeVector):
                #print("self.distVector: " + str(self.distVector[idx]),("self.speedVector: " + str(self.speedVector[idx])))
                if tIniPico1 < x <= tEndPico1 or tIniPico2 < x < tEndPico2:
                    if self.distVector[idx]==0 and self.stateVector[idx]==2:
                        frec=dispatchFrequency
                else:
                    if self.distVector[idx] == 0:
                        frec = dispatchFrequency

                time_arr.append(
                    datetime.datetime.fromtimestamp(x + timeZoneColombia ) + datetime.timedelta(seconds=frec*y))
                time_.append(time_arr[idx].strftime("%I:%M:%S %p"))
                #print(time_[idx])
            self.arrayTime.append(time_arr)
            print(np.shape(self.arrayTime))
        
        
        self.__plotOpDiagram()
        self.timeVector = self.timeVector
        self.speedVector = self.speedVector
        self.distVector = self.distVector
        self.stateVector = self.stateVector
        self.timeVectorDT = self.timeVectorDT
        self.labelVector = self.labelVector
        self.stopVector = self.stopVector

    ## Definir Plots (VELOCIDAD Y DISTANCIA RECORRIDA)
    def __setupBusDataFigures(self):
        self.figureSpeedBus = Figure(tight_layout=True)  
        self.figureDistanceBus = Figure(tight_layout=True)  
        self.canvasSpeedBus = FigureCanvas(self.figureSpeedBus)  
        self.canvasDistanceBus = FigureCanvas(self.figureDistanceBus)
        self.toolbarSpeedBus = NavigationToolbar(self.canvasSpeedBus, self)
        self.toolbarDistanceBus = NavigationToolbar(self.canvasDistanceBus, self)
        self.layoutSpeedBus = QtWidgets.QVBoxLayout(self.__BusWindow.SpeedCurveWidget)  
        self.layoutDistanceBus = QtWidgets.QVBoxLayout(self.__BusWindow.DistanceCurveWidget)  
        self.layoutSpeedBus.addWidget(self.toolbarSpeedBus)  
        self.layoutSpeedBus.addWidget(self.canvasSpeedBus)  
        self.layoutDistanceBus.addWidget(self.toolbarDistanceBus)  
        self.layoutDistanceBus.addWidget(self.canvasDistanceBus)  
        self.axSpeedBus = self.figureSpeedBus.add_subplot(111)  
        self.axDistanceBus = self.figureDistanceBus.add_subplot(111)

    ## Definir Plots (VELOCIDAD Y POSICIÓN)
    def __setupOpDiagramFigures(self):
        self.figureOPPosition = Figure(tight_layout=True)  
        self.canvasOPPosition = FigureCanvas(self.figureOPPosition) 
        self.toolbarOPPosition = NavigationToolbar(self.canvasOPPosition, self)
        self.layoutOPPosition = QtWidgets.QVBoxLayout(self.__BusWindow.OPPositionCurveWidget)
        self.layoutOPPosition.addWidget(self.toolbarOPPosition)  
        self.layoutOPPosition.addWidget(self.canvasOPPosition)
        self.axOPPosition = self.figureOPPosition.add_subplot(111)

        self.figureOPSpeed = Figure(tight_layout=True)    
        self.canvasOPSpeed = FigureCanvas(self.figureOPSpeed)   
        self.toolbarOPSpeed = NavigationToolbar(self.canvasOPSpeed, self)     
        self.layoutOPSpeed = QtWidgets.QVBoxLayout(self.__BusWindow.OPSpeedCurveWidget)
        self.layoutOPSpeed.addWidget(self.toolbarOPSpeed)  
        self.layoutOPSpeed.addWidget(self.canvasOPSpeed)
        self.axOPSpeed = self.figureOPSpeed.add_subplot(111)

    ## Plotear dos gráficas = Velocidad vs Tiempo / Distancia vs Tiempo
    def __plotBusData(self):
        # Speed Figure
        self.axSpeedBus.cla()
        self.axSpeedBus.plot(self.timeCurve, 3.6 * self.speedCurve)
        self.axSpeedBus.set_title('Speed Curve', fontsize=12, fontweight="bold")
        self.axSpeedBus.set_ylabel('Speed [km/h]', fontsize=10, fontweight="bold")
        self.axSpeedBus.set_xlabel('Time [s]', fontsize=10, fontweight="bold")
        self.axSpeedBus.tick_params(labelsize=8)
        self.axSpeedBus.grid()
        self.canvasSpeedBus.draw()

        # Distance Figure
        self.axDistanceBus.cla()
        self.axDistanceBus.plot(self.timeCurve, 0.001 * self.distanceCurve)
        self.axDistanceBus.set_title('Distance Traveled ', fontsize=12, fontweight="bold")
        self.axDistanceBus.set_ylabel('Distance [km]', fontsize=10, fontweight="bold")
        self.axDistanceBus.set_xlabel('Time [s]', fontsize=10, fontweight="bold")
        self.axDistanceBus.tick_params(labelsize=8)
        self.axDistanceBus.grid()          
        self.canvasDistanceBus.draw()    

    ## Plotear dos curvas de Operación = Distancia vs Tiempo / Velocidad vs Tiempo 
    def __plotOpDiagram(self):
        
        def StopPositionLabels(distRoute, busStopRoute, labelRoute):
            stopTicks = []
            stopLabels = []
            for n in range(0, len(busStopRoute)):
                if busStopRoute.iloc[n].values[0] == 1:
                    stopTicks.append(distRoute.iloc[n].values[0])
                    stopLabels.append(labelRoute.iloc[n].values[0] + '=' + '%0.2f' % stopTicks[-1] + ' km')
                else:
                    pass
            outTup = (stopTicks, stopLabels)

            return (outTup)

        self.axOPSpeed.cla()
        self.axOPPosition.cla()
        print("distVector")
        print(self.distVector)
        print('speedVector')
        print(self.speedVector)
        for x in self.arrayTime:
            self.axOPSpeed.plot(x, 3.6 * self.speedVector)
            self.axOPPosition.plot(x, 0.001 * self.distVector)
        
        self.axOPSpeed.set_title('Operating curve (Speed)', fontsize=12, fontweight="bold")
        self.axOPSpeed.set_ylabel('Speed [km/h]', fontsize=10, fontweight="bold")
        self.axOPSpeed.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
        self.axOPSpeed.tick_params(labelsize=8)
        self.axOPSpeed.grid()
        self.figureOPSpeed.autofmt_xdate()
        self.canvasOPSpeed.draw()  
            
        self.axOPPosition.set_title('Operating curve (Distace)', fontsize=12, fontweight="bold")
        self.axOPPosition.set_ylabel('Distance [km]', fontsize=10, fontweight="bold")
        self.axOPPosition.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
        self.axOPPosition.tick_params(labelsize=8)
        self.axOPPosition.grid(which='minor')
        self.figureOPPosition.autofmt_xdate()
        self.stopTicks, self.stopLabels = StopPositionLabels(self.distRoute, self.busStopRoute, self.labelRoute)
        self.axOPPosition.yaxis.set_major_locator(ticker.FixedLocator([]))
        self.axOPPosition.yaxis.set_minor_locator(ticker.FixedLocator(self.stopTicks))
        self.axOPPosition.yaxis.set_minor_formatter(ticker.FixedFormatter(self.stopLabels))

        for tick in self.axOPPosition.yaxis.get_minor_ticks():
            tick.label.set_fontsize(7)

        self.canvasOPPosition.draw()
 

# Inicio Programa
if __name__ == "__main__":
    import sys
    global app
    app = QtWidgets.QApplication(sys.argv)
    global widget
    widget = QtWidgets.QStackedWidget()

    # Definir Ventanas
    global RouteWindow
    RouteWindow  = Ui_RouteWindow()
    global BusWindow 
    BusWindow = Ui_BusWindow()
        
    # Añadir Ventanas
    widget.addWidget(RouteWindow)
    widget.addWidget(BusWindow)


    # Setup de widgets
    widget.setFixedSize(964, 677)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("../Imgs/iconBus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    widget.setWindowIcon(icon)
    _translate = QtCore.QCoreApplication.translate
    widget.setWindowTitle(_translate("MainWindow", "Electric Bus Charging Analyzer"))
    widget.setStyleSheet("background-color: #bfbfbf;")


    # Mostrar Aplicación
    widget.show()
    sys.exit(app.exec_())
