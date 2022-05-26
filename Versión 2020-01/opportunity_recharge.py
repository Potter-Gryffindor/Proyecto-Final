import random

from PyQt5 import QtGui, uic
from PyQt5 import QtCore, QtWidgets
import time
import csv
import math
import datetime
import numpy as np
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pandas import read_csv
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.ticker as ticker


class charger_window(QtWidgets.QMainWindow):
    #Demas partes de la interfaz gráfica
    def __init__(self):
        super(charger_window, self).__init__()
        self.main_win = uic.loadUi('interfaz_grafica.ui', self)
        self.main_win.pushButtonRouteSearch.clicked.connect(self.pushButton_route_search_clicked)
        self.main_win.pushButtonRouteLoad.clicked.connect(self.pushButton_route_load_clicked)
        self.main_win.pushButtonSimGenCurve.clicked.connect(self.pushButtonSimGenCurve_clicked)
        self.main_win.pushButtonOperDiagram.clicked.connect(self.pushButtonOperDiagram_clicked)
        self.main_win.pushButtonOppChargeSim.clicked.connect(self.pushButtonOppChargeSim_clicked)
        self.main_win.pushButtonPlotOppChargeSim.clicked.connect(self.pushButtonPlotOppChargeSim_clicked)
        self.route_figure_init()
        self.bus_figure_init()
        self.operation_figure_init()
        self.oppChargSim_figure_init()

    def route_figure_init(self):
        self.figure_route_1 = Figure(tight_layout=True)  #
        self.figure_route_2 = Figure(tight_layout=True)  #
        self.canvas_route_1 = FigureCanvas(self.figure_route_1)  #
        self.canvas_route_2 = FigureCanvas(self.figure_route_2)
        self.toolbar_route_1 = NavigationToolbar(self.canvas_route_1, self)
        self.toolbar_route_2 = NavigationToolbar(self.canvas_route_2, self)
        self.layout_route_1 = QtWidgets.QVBoxLayout(self.main_win.widgetRoute1)  #
        self.layout_route_2 = QtWidgets.QVBoxLayout(self.main_win.widgetRoute2)  #
        self.layout_route_1.addWidget(self.toolbar_route_1)  #
        self.layout_route_1.addWidget(self.canvas_route_1)  #
        self.layout_route_2.addWidget(self.toolbar_route_2)  #
        self.layout_route_2.addWidget(self.canvas_route_2)  #
        self.ax_route_1 = self.figure_route_1.add_subplot(111)  #
        self.ax_route_2 = self.figure_route_2.add_subplot(111)  #

    def bus_figure_init(self):
        self.figure_bus_1 = Figure(tight_layout=True)
        self.figure_bus_2 = Figure(tight_layout=True)
        self.canvas_bus_1 = FigureCanvas(self.figure_bus_1)
        self.canvas_bus_2 = FigureCanvas(self.figure_bus_2)
        self.toolbar_bus_1 = NavigationToolbar(self.canvas_bus_1, self)
        self.toolbar_bus_2 = NavigationToolbar(self.canvas_bus_2, self)
        self.layout_bus_1 = QtWidgets.QVBoxLayout(self.main_win.widgetBusCurve1)
        self.layout_bus_2 = QtWidgets.QVBoxLayout(self.main_win.widgetBusCurve2)
        self.layout_bus_1.addWidget(self.toolbar_bus_1)
        self.layout_bus_1.addWidget(self.canvas_bus_1)  #
        self.layout_bus_2.addWidget(self.toolbar_bus_2)
        self.layout_bus_2.addWidget(self.canvas_bus_2)  #
        self.ax_bus_1 = self.figure_bus_1.add_subplot(111)
        self.ax_bus_2 = self.figure_bus_2.add_subplot(111)

    def operation_figure_init(self):
        self.figure_operation_1 = Figure(tight_layout=True)
        self.canvas_operation_1 = FigureCanvas(self.figure_operation_1)
        self.toolbar_operation_1 = NavigationToolbar(self.canvas_operation_1, self)
        self.layout_operation_1 = QtWidgets.QVBoxLayout(self.main_win.widgetOperationDiagram)
        self.layout_operation_1.addWidget(self.toolbar_operation_1)
        self.layout_operation_1.addWidget(self.canvas_operation_1)  #
        self.ax_operation_1 = self.figure_operation_1.add_subplot(111)
        self.figure_operation_2 = Figure()
        self.canvas_operation_2 = FigureCanvas(self.figure_operation_2)
        self.toolbar_operation_2 = NavigationToolbar(self.canvas_operation_2, self)
        self.layout_operation_2 = QtWidgets.QVBoxLayout(self.main_win.widgetOperationDiagram2)
        self.layout_operation_2.addWidget(self.toolbar_operation_2)
        self.layout_operation_2.addWidget(self.canvas_operation_2)  #
        self.ax_operation_2 = self.figure_operation_2.add_subplot(111)

    def oppChargSim_figure_init(self):
        self.figure_oppChargSim_1 = Figure(tight_layout=True)
        self.canvas_oppChargSim_1 = FigureCanvas(self.figure_oppChargSim_1)
        self.toolbar_oppChargSim_1 = NavigationToolbar(self.canvas_oppChargSim_1, self)
        self.layout_oppChargSim_1 = QtWidgets.QVBoxLayout(self.main_win.widgetOppChargSim)
        self.layout_oppChargSim_1.addWidget(self.toolbar_oppChargSim_1)
        self.layout_oppChargSim_1.addWidget(self.canvas_oppChargSim_1)  #
        self.ax_oppChargSim_1 = self.figure_oppChargSim_1.add_subplot(111)

    #Buscar y definir la extensión del archivo .CSV
    def pushButton_route_search_clicked(self):
        filename, extension = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '.',
                                                                    filter=self.tr("csv file (*.csv)"))
        self.main_win.lineEditRouteFile.setText(filename)

    #Leer y cargar el archivo .CSV
    def pushButton_route_load_clicked(self):
        csv_file = self.main_win.lineEditRouteFile.text()
        try:
            self.route_data = read_csv(csv_file)
        except:
            print('Not a valid data vector')
            return

        print(self.route_data)
        self.plot_route()

    #Plotear dos gráficas = Latitud vs Longitud / Altitud vs Distancia
    def plot_route(self):
        long = self.route_data[['LONG']]
        lat = self.route_data[['LAT']]
        self.ax_route_1.cla()
        self.ax_route_1.plot(long.iloc[:, -1].values, lat.iloc[:, -1].values)
        self.ax_route_1.set_title('Mapa de la Ruta',  fontsize=12, fontweight="bold")
        self.ax_route_1.set_xlabel('Longitud', fontsize=10, fontweight="bold")
        self.ax_route_1.set_ylabel('Latitud', fontsize=10, fontweight="bold")
        self.ax_route_1.tick_params(labelsize=8)
        self.ax_route_1.grid()
        self.canvas_route_1.draw()
        dist = self.route_data[['DIST']]
        alt = self.route_data[['ALT']]

        self.ax_route_2.cla()
        self.ax_route_2.plot(dist.iloc[:, -1].values, alt.iloc[:, -1].values)
        self.ax_route_2.set_title('Perfil de Ruta', fontsize=12, fontweight="bold")
        self.ax_route_2.set_xlabel('Distancia (km)', fontsize=10, fontweight="bold")
        self.ax_route_2.set_ylabel('Altitud (m)', fontsize=10, fontweight="bold")
        self.ax_route_2.tick_params(labelsize=9)
        self.ax_route_2.grid()
        self.canvas_route_2.draw()
        bus_stop = self.route_data[['BUS STOP']]
        label = self.route_data[['LABEL']]

        for n in range(0, len(bus_stop)):

            if bus_stop.iloc[n].values[0] == 1:
                self.ax_route_1.plot(long.iloc[n].values[0], lat.iloc[n].values[0], marker='^', color='red')
                self.ax_route_1.annotate(label.iloc[n].values[0], (long.iloc[n].values[0], lat.iloc[n].values[0]),
                                         fontsize=7)
                self.ax_route_2.plot(dist.iloc[n].values[0], alt.iloc[n].values[0], marker='^', color='red')
                self.ax_route_2.annotate(label.iloc[n].values[0], (dist.iloc[n].values[0], alt.iloc[n].values[0]),
                                         fontsize=7)

        self.canvas_route_1.draw()  #
        self.canvas_route_2.draw()  #


    #Plotear dos gráficas = Curva de velocidad y Distancia recorrida
    #Dentro de se definen la velocidad, aceleración y desaceleración
    def pushButtonSimGenCurve_clicked(self):
        table2 = self.main_win.tableWidgetSpeedPar
        acceleration = float(table2.item(0, 0).text())
        braking = float(table2.item(1, 0).text())
        max_speed = float(table2.item(2, 0).text())
        t = np.array([0])
        speed = np.array([0])
        accel = np.array([0])
        decel = np.array([0])
        dist = np.array([0])
        deltaT = 0.5

        for n in range(0, 600):
            t = np.append(t, t[-1] + deltaT)
            if t[-1] < 150:
                speed = np.append(speed, speed[-1] + acceleration * deltaT)
                if speed[-1] > max_speed / 3.6:
                    speed[-1] = max_speed / 3.6
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
        accel = np.append(accel, max_speed / 3.6)
        decel = np.append(decel, speed[-1])

        self.speed_curve = speed
        self.accel_curve = accel
        self.decel_curve = decel
        self.ax_bus_1.cla()
        self.ax_bus_1.plot(t, 3.6 * speed)
        self.ax_bus_1.set_title('Curva de velocidad', fontsize=12, fontweight="bold")
        self.ax_bus_1.set_ylabel('Velocidad (km/h)', fontsize=10, fontweight="bold")
        self.ax_bus_1.set_xlabel('Tiempo (s)', fontsize=10, fontweight="bold")
        self.ax_bus_1.tick_params(labelsize=8)
        self.ax_bus_1.grid()
        self.ax_bus_2.cla()
        self.ax_bus_2.plot(t, 0.001 * dist)
        self.ax_bus_2.set_title('Distancia Recorrida', fontsize=12, fontweight="bold")
        self.ax_bus_2.set_ylabel('Distancia (km)', fontsize=10, fontweight="bold")
        self.ax_bus_2.set_xlabel('Tiempo (s)', fontsize=10, fontweight="bold")
        self.ax_bus_2.tick_params(labelsize=8)
        self.ax_bus_2.grid()
        self.canvas_bus_1.draw()  #
        self.canvas_bus_2.draw()  #

    #Operación de los buses = Definición de los estados y llenado de vectores tiempo, paradas, velocidad, distancia
    def pushButtonOperDiagram_clicked(self):
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
            # State1: Buses are stopped
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

        def state3func(inputTup):  # Constant speed
            timeVector, distVector, speedVector, deltaT, maxSpeedBus, labelVector, stopVector = inputTup
            timeVector = np.append(timeVector, timeVector[-1] + deltaT)
            speedVector = np.append(speedVector, maxSpeedBus)
            distVector = np.append(distVector, distVector[-1] + (speedVector[-1] + speedVector[-2]) * 0.5 * deltaT)
            labelVector.append('')
            stopVector.append(0)
            outTup = (timeVector, distVector, speedVector, labelVector, stopVector)
            return (outTup)

        def state4func(inputTup):  # Decelerating
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
            while True:
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
                #               distBrake=distBrake+(decelBus[n]+decelBus[n-1])*0.5*deltaT
                distBrake = distBrake + (decelBus[n]) * deltaT
            return (distBrake)

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

        # Route parameters
        distRoute = self.route_data[['DIST']]
        print("Distance")
        print(distRoute)
        busStopRoute = self.route_data[['BUS STOP']]
        labelRoute = self.route_data[['LABEL']]

        # Fleet parameters
        table3 = self.main_win.tableWidgetFleetPar
        stopDelay = float(table3.item(6, 0).text())
        print("Stop Delay", stopDelay)
        TimeInTerminal = float(table3.item(7, 0).text())
        print("Time in Terminal", TimeInTerminal)
        tIniFleetQt = self.main_win.timeEditStart.time()
        tIniFleet = tIniFleetQt.hour() * 3600 + tIniFleetQt.minute() * 60 + tIniFleetQt.second()
        print("Initial time", tIniFleet)
        tEndFleetQt = self.main_win.timeEditEnd.time()
        tEndFleet = tEndFleetQt.hour() * 3600 + tEndFleetQt.minute() * 60 + tEndFleetQt.second()
        print("End time", tEndFleet)
        tIniPico1Qt = self.main_win.timeEdit.time()
        tIniPico1 = tIniPico1Qt.hour() * 3600 + tIniPico1Qt.minute() * 60 + tIniPico1Qt.second()
        print("Initial time pico 1", tIniPico1)
        tEndPico1Qt = self.main_win.timeEdit_7.time()
        tEndPico1 = tEndPico1Qt.hour() * 3600 + tEndPico1Qt.minute() * 60 + tEndPico1Qt.second()
        print("End time pico 1", tEndPico1)

        tIniPico2Qt = self.main_win.timeEdit_10.time()
        tIniPico2 = tIniPico2Qt.hour() * 3600 + tIniPico2Qt.minute() * 60 + tIniPico2Qt.second()
        print("Initial time pico 2", tIniPico2)
        tEndPico2Qt = self.main_win.timeEdit_22.time()
        tEndPico2 = tEndPico2Qt.hour() * 3600 + tEndPico2Qt.minute() * 60 + tEndPico1Qt.second()
        print("End time pico 2", tEndPico2)
        numero_buses = int(self.main_win.tableWidgetFleetPar.item(0, 0).text())
        print("Number of buses", numero_buses)
        frecuencia_despacho = int(self.main_win.tableWidgetFleetPar.item(5, 0).text())
        print("Dispatch frequency", frecuencia_despacho)
        numero_buses_pico = int(self.main_win.tableWidgetFleetPar.item(8, 0).text())
        print("Number of buses pico", numero_buses_pico)
        frecuencia_despacho_pico = int(self.main_win.tableWidgetFleetPar.item(9, 0).text())
        print("Dispatch frequency pico", frecuencia_despacho_pico)

        # Simulation parameters
        deltaT = 0.2
        maxTime = tEndFleet - (numero_buses - 1) * frecuencia_despacho
        #maxTime2 = t2EndFleet - (numero_buses_pico - 1) * frecuencia_despacho_pico

        ## Bus parameters
        accelBus = self.accel_curve
        print("Acceleration curve", accelBus)
        decelBus = self.decel_curve
        print("Deceleration curve", decelBus)
        print("len Decel:", len(decelBus))
        distBrake = calculateBrakingDistance(decelBus, deltaT)
        print("Braking distance", distBrake)
        maxSpeedBus = accelBus[-1]
        print("Max speed", maxSpeedBus)

        # Initial conditions
        state = 0
        indexStop = 0

        timeVector = np.array([tIniFleet])
        print("Time vector")
        print(timeVector)
        distVector = np.array([0])
        labelVector = ['']
        stopVector = [0]
        speedVector = np.array([0])
        stateVector = []
        timeState0 = 0

        while 1:

            stateVector.append(state)
            if state == 0:

                inputTup = (timeVector, distVector, speedVector, deltaT, labelVector, stopVector)
                timeVector, distVector, speedVector, labelVector, stopVector = state0func(inputTup)

                if timeVector[-1] >= tIniFleet:
                    if timeVector[-1] <= tEndFleet:
                        state = 1
                        timeState1 = timeVector[-1]

            elif state == 1:
                labelStop = labelRoute.iloc[indexStop].values[0]
                inputTup = (timeVector, distVector, speedVector, deltaT, labelVector, stopVector, labelStop)
                timeVector, distVector, speedVector, labelVector, stopVector = state1func(inputTup)

                # Cambio de Velocidad de la Flota en tiempo pico
                if (tIniPico1 < timeVector[-1] <= tEndPico1 and distVector[-1] == 0) or (tIniPico2 < timeVector[-1] < tEndPico2 and distVector[-1] == 0):
                    stopDelay=frecuencia_despacho_pico
                    state = 1
                elif (tIniPico1 < timeVector[-1] <= tEndPico1 ) or (tIniPico2 < timeVector[-1] < tEndPico2):
                    stopDelay=float(table3.item(6, 0).text()) + 33
                    state=1
                elif distVector[-1] == 0:
                    stopDelay = TimeInTerminal
                    state = 1
                else:
                    stopDelay=float(table3.item(6, 0).text())
                    state = 1

                if timeVector[-1] >= timeState1 + stopDelay:
                    state = 2
                    timeState2 = timeVector[-1]
                    distState2 = distVector[-1]
                    indexAccel = 1
                    busStop1, busStop2 = findNextStop(indexStop, busStopRoute)
                    distStops = 1000 * (distRoute.iloc[busStop2].values[0] - distRoute.iloc[busStop1].values[0])
                    distStopsAccum = distStops
                    indexStop = busStop2

            elif state == 2:

                inputTup = (timeVector, distVector, speedVector, deltaT, accelBus, indexAccel, labelVector, stopVector)
                timeVector, distVector, speedVector, indexAccel, labelVector, stopVector = state2func(inputTup)

                if speedVector[-1] == maxSpeedBus:
                    state = 3
                    timeState3 = timeVector[-1]


            elif state == 3:
                inputTup = (timeVector, distVector, speedVector, deltaT, maxSpeedBus, labelVector, stopVector)
                timeVector, distVector, speedVector, labelVector, stopVector = state3func(inputTup)

                if distVector[-1] - distState2 >= distStops - distBrake:
                    state = 4
                    timeState4 = timeVector[-1]
                    indexDecel = 1

            elif state == 4:
                inputTup = (timeVector, distVector, speedVector, deltaT, decelBus, indexDecel, labelVector, stopVector)
                timeVector, distVector, speedVector, indexDecel, labelVector, stopVector = state4func(inputTup)

                if speedVector[-1] == 0:
                    state = 1
                    timeState1 = timeVector[-1]

                    if busStop2 == len(busStopRoute) - 1:
                        indexStop = 0
                        distVector[-1] = 0
                        distStopsAccum = 0

            else:
                pass
            self.main_win.progressBarRoute.setValue(int(100 * timeVector[-1] / maxTime))

            if timeVector[-1] > maxTime:
                break

        timeVectorDT = []
        timeZoneColombia = 3600 * 5

        for n in range(0, len(timeVector)):
            timeVectorDT.append(datetime.datetime.fromtimestamp(timeVector[n] + timeZoneColombia))

        self.array_tiempos = []

        for y in range(numero_buses):
            time_arr = []
            time_ = []
            print(f"Numero de bus: {str(y)}")
            for idx, x in enumerate(timeVector):
                #print("distVector: " + str(distVector[idx]),("speedVector: " + str(speedVector[idx])))
                if tIniPico1 < x <= tEndPico1 or tIniPico2 < x < tEndPico2:
                    if distVector[idx]==0 and stateVector[idx]==2:
                        frec=frecuencia_despacho
                else:
                    if distVector[idx] == 0:
                        frec = frecuencia_despacho

                time_arr.append(
                    datetime.datetime.fromtimestamp(x + timeZoneColombia ) + datetime.timedelta(seconds=frec*y))
                time_.append(time_arr[idx].strftime("%I:%M:%S %p"))
                #print(time_[idx])
            self.array_tiempos.append(time_arr)
            print(np.shape(self.array_tiempos))

        self.ax_operation_1.cla()
        print("distVector")
        print(distVector)
        with open('distVector.txt', 'w') as f:
            for item in distVector:
                f.write("%s\n" % item)
        print("speedVector")
        with open('speedVector.txt', 'w') as f:
            for item in speedVector:
                f.write("%s\n" % item)
        print(speedVector)
        for x in self.array_tiempos:
            self.ax_operation_1.plot(x, 3.6 * speedVector)
        self.ax_operation_1.set_title('Curva de operación (Velocidad)', fontsize=12, fontweight="bold")
        self.ax_operation_1.set_ylabel('Velocidad (km/h)', fontsize=10, fontweight="bold")
        self.ax_operation_1.set_xlabel('Tiempo (h)', fontsize=10, fontweight="bold")
        self.ax_operation_1.tick_params(labelsize=8)
        self.ax_operation_1.grid()
        self.figure_operation_1.autofmt_xdate()
        self.canvas_operation_1.draw()  #
        self.ax_operation_2.cla()
        for x in self.array_tiempos:
            self.ax_operation_2.plot(x, 0.001 * distVector)
        self.ax_operation_2.set_title('Curva de operación (Distancia)', fontsize=12, fontweight="bold")
        self.ax_operation_2.set_ylabel('Distancia (km)', fontsize=10, fontweight="bold")
        self.ax_operation_2.set_xlabel('Tiempo (h)', fontsize=10, fontweight="bold")
        self.ax_operation_2.tick_params(labelsize=8)
        self.ax_operation_2.grid(which='minor')
        self.figure_operation_2.autofmt_xdate()
        stopTicks, stopLabels = StopPositionLabels(distRoute, busStopRoute, labelRoute)
        
        self.ax_operation_2.yaxis.set_major_locator(ticker.FixedLocator([]))
        self.ax_operation_2.yaxis.set_minor_locator(ticker.FixedLocator(stopTicks))
        self.ax_operation_2.yaxis.set_minor_formatter(ticker.FixedFormatter(stopLabels))

        for tick in self.ax_operation_2.yaxis.get_minor_ticks():
            tick.label.set_fontsize(7)

        self.canvas_operation_2.draw()  #
        self.timeVector = timeVector
        self.speedVector = speedVector
        self.distVector = distVector
        self.stateVector = stateVector
        self.timeVectorDT = timeVectorDT
        self.labelVector = labelVector
        self.stopVector = stopVector


    #Llama demás funciones de consumo energético
    def pushButtonOppChargeSim_clicked(self):

        def calculateAngle(distVector, distRoute, altRoute):

            sinThetaVectorRoute = []
            print(len(distRoute) - 1)
            for n in range(0, len(distRoute) - 1):
                point1Route = n
                point2Route = n + 1
                sinTheta = (altRoute.iloc[point2Route].values[0] - altRoute.iloc[point1Route].values[0]) / (
                            1000 * distRoute.iloc[point2Route].values[0] - 1000 * distRoute.iloc[point1Route].values[0])
                sinThetaVectorRoute.append(sinTheta)

            sinThetaVectorRoute.append(sinThetaVectorRoute[-1])
            time.sleep(5)
            sinThetaVector = []
            arr = []
            for n in range(0, len(distRoute)):
                arr.append(1000 * distRoute.iloc[n].values[0])
            distRouteNP = np.array(arr)
            print(distRouteNP)
            print('*******************************')
            k = 1

            for n in range(0, len(distVector) - 1):
                # point1=distVector[n]
                point2 = distVector[n + 1]
                index = np.where(point2 >= distRouteNP)
                k = index[0][-1]
                sinThetaTot = sinThetaVectorRoute[k]
                sinThetaVector.append(sinThetaTot)

            sinThetaVector.append(sinThetaVector[-1])

            print('*********************')
            print(len(sinThetaVectorRoute))
            print('**********************')
            return (sinThetaVector)

        # Parameters
        # Simulation parameters
        deltaT = 0.2

        # Bus parameters
        table1 = self.main_win.tableWidgetBusSimParameters
        fric = float(table1.item(0, 0).text())
        print('fric', fric)
        mass = float(table1.item(1, 0).text())
        print('mass', mass)
        grav = float(table1.item(2, 0).text())
        print('grav', grav)
        rho = float(table1.item(3, 0).text())
        print('rho', rho)
        alpha = float(table1.item(4, 0).text())
        print('alpha', alpha)
        Area = float(table1.item(5, 0).text())
        print('Area', Area)
        Paux = 1000 * float(table1.item(6, 0).text())
        print('Paux', Paux)
        nout = 0.01 * float(table1.item(7, 0).text())
        print('nout', nout)
        nin = 0.01 * float(table1.item(8, 0).text())
        print('nin', nin)

        # Opportunity charge parameters
        table4 = self.main_win.tableWidgetOppCharParameters
        BC = float(table4.item(0, 0).text())
        SoCi = 0.01 * float(table4.item(1, 0).text())
        text = table4.item(2, 0).text()
        CL = text.split(',')
        CP = float(table4.item(3, 0).text())
        nC = 0.01 * float(table4.item(4, 0).text())
        IT = float(table4.item(5, 0).text())
        DT = float(table4.item(6, 0).text())

        print(CL)
        # Fleet operation time for extra loads
        table6 = self.main_win.tableWidgetFleetPar
        stopDelay = float(table6.item(6, 0).text())
        TimeInTerminal = float(table6.item(7, 0).text())
        tIniFleetQt = self.main_win.timeEditStart.time()
        tIniFleet = tIniFleetQt.hour() * 3600 + tIniFleetQt.minute() * 60 + tIniFleetQt.second()
        tEndFleetQt = self.main_win.timeEditEnd.time()
        tEndFleet = tEndFleetQt.hour() * 3600 + tEndFleetQt.minute() * 60 + tEndFleetQt.second()

        tIniPico1Qt = self.main_win.timeEdit.time()
        tIniPico1 = tIniPico1Qt.hour() * 3600 + tIniPico1Qt.minute() * 60 + tIniPico1Qt.second()
        tEndPico1Qt = self.main_win.timeEdit_7.time()
        tEndPico1 = tEndPico1Qt.hour() * 3600 + tEndPico1Qt.minute() * 60 + tEndPico1Qt.second()

        tIniPico2Qt = self.main_win.timeEdit_10.time()
        tIniPico2 = tIniPico2Qt.hour() * 3600 + tIniPico2Qt.minute() * 60 + tIniPico2Qt.second()
        tEndPico2Qt = self.main_win.timeEdit_22.time()
        tEndPico2 = tEndPico2Qt.hour() * 3600 + tEndPico2Qt.minute() * 60 + tEndPico1Qt.second()

        # Fleet operation results
        timeVector = self.timeVector
        print('time vector:')
        print(timeVector)
        print('t_ini_fleet:', tIniFleet)   
        timeVectorDT = self.timeVectorDT
        speedVector = self.speedVector
        distVector = self.distVector
        stateVector = self.stateVector
        stopVector = self.stopVector
        labelVector = self.labelVector

        # Route Data
        distRoute = self.route_data[['DIST']]
        altRoute = self.route_data[['ALT']]

        # Angle vector
        sinThetaVector = calculateAngle(distVector, distRoute, altRoute)
        energyVector = []
        SoCVector = [SoCi]
        chargerVector = []

        for n in range(0, len(timeVector) - 1):

            if timeVector[n] > tIniFleet:
                AuxONOFF = 1
            else:
                AuxONOFF = 0

            energy = (nout * (fric * (mass+BC*11.1) * grav + 0.5 * rho * alpha * Area * speedVector[n] * speedVector[n]) *
                      speedVector[n] * deltaT \
                      + nin * mass * grav * sinThetaVector[n] * speedVector[n] * deltaT + mass * nin * (
                                  speedVector[n + 1] - speedVector[n]) * speedVector[n] * deltaT \
                      + AuxONOFF * Paux * deltaT) / 3600000
            if n == 0:
                energyVector.append(energy)
            else:
                energyVector.append(energyVector[-1] + energy)
            if stopVector[n] == 1 :
                if labelVector[n] in CL:
                    CHONOFF = 1
                else:
                    CHONOFF = 0
            else:
                CHONOFF = 0

            chargerVector.append(CHONOFF * CP)

            SoCVector.append((SoCVector[-1] * BC - energy + chargerVector[-1] * deltaT / 3600) / BC)

            self.main_win.progressBarOppCharg.setValue(int(100*n/(len(timeVector)-2)))

        energyVector.append(energyVector[-1])
        chargerVector.append(chargerVector[-1])
        powerVector = [0]

        for n in range(1, len(timeVector) - 1):
            powerVector.append(-(energyVector[n - 1] - energyVector[n]) / (deltaT / 3600))
        powerVector.append(powerVector[-1])

        self.energyVector = energyVector
        self.powerVector = powerVector
        self.sinThetaVector = sinThetaVector
        self.SoCVector = SoCVector
        self.chargerVector = chargerVector

    #Plotea datos del consumo energético mediante Dropdown list
    def pushButtonPlotOppChargeSim_clicked(self):
        plotType = self.main_win.comboBoxOppChargeSimVar.currentIndex()
        self.ax_oppChargSim_1.cla()
        if plotType == 0:
            for x in self.array_tiempos:
                self.ax_oppChargSim_1.plot(x, self.energyVector)
            self.ax_oppChargSim_1.set_title('Curva de Energía', fontsize=12, fontweight="bold")
            self.ax_oppChargSim_1.set_ylabel('Energía (kWh)', fontsize=10, fontweight="bold")
            self.ax_oppChargSim_1.set_xlabel('Tiempo (h)', fontsize=10, fontweight="bold")
        elif plotType == 1:
            for x in self.array_tiempos:
                self.ax_oppChargSim_1.plot(x, self.powerVector)

            self.ax_oppChargSim_1.set_title('Curva de Potencia', fontsize=12, fontweight="bold")
            self.ax_oppChargSim_1.set_ylabel('Potencia (kW)', fontsize=10, fontweight="bold")
            self.ax_oppChargSim_1.set_xlabel('Tiempo (h)', fontsize=10, fontweight="bold")
        elif plotType == 2:
            for x in self.array_tiempos:
                self.ax_oppChargSim_1.plot(x, self.sinThetaVector)
            self.ax_oppChargSim_1.set_title('Pendiente', fontsize=12, fontweight="bold")
            self.ax_oppChargSim_1.set_ylabel('Seno(Theta)', fontsize=10, fontweight="bold")
            self.ax_oppChargSim_1.set_xlabel('Tiempo (h)', fontsize=10, fontweight="bold")
        elif plotType == 3:
            for x in self.array_tiempos:
                self.ax_oppChargSim_1.plot(x, 100 * np.array(self.SoCVector))
            self.ax_oppChargSim_1.set_title('Estado de Carga', fontsize=12, fontweight="bold")
            self.ax_oppChargSim_1.set_ylabel('%', fontsize=10, fontweight="bold")
            self.ax_oppChargSim_1.set_xlabel('Tiempo (h)', fontsize=10,fontweight="bold" )
        elif plotType == 4:
            for x in self.array_tiempos:
                self.ax_oppChargSim_1.plot(x, self.stopVector)
            self.ax_oppChargSim_1.set_title('Vector de Parada', fontsize=12, fontweight="bold")
            self.ax_oppChargSim_1.set_ylabel('', fontsize=10, fontweight="bold")
            self.ax_oppChargSim_1.set_xlabel('Tiempo (h)', fontsize=10, fontweight="bold")
        elif plotType == 5:
            for x in self.array_tiempos:
                self.ax_oppChargSim_1.plot(x, self.chargerVector)
            self.ax_oppChargSim_1.set_title('Vector de cargador', fontsize=12, fontweight="bold")
            self.ax_oppChargSim_1.set_ylabel('kW', fontsize=10, fontweight="bold")
            self.ax_oppChargSim_1.set_xlabel('Tiempo (h)', fontsize=10, fontweight="bold")

        self.ax_oppChargSim_1.tick_params(labelsize=10)
        self.ax_oppChargSim_1.grid()
        self.figure_oppChargSim_1.autofmt_xdate()
        self.canvas_oppChargSim_1.draw()

app = QtWidgets.QApplication(sys.argv)
app.setStyle('Fusion')
widget = charger_window()  ####here
widget.show()
sys.exit(app.exec_())