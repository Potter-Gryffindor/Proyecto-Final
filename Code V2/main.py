# Importar Paquetes
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from pandas import read_csv
import numpy as np
import datetime
# import time

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.ticker as ticker


# Clases
class UiAboutwindow(QtWidgets.QDialog):
    # Constructor
    def __init__(self):
        super(UiAboutwindow, self).__init__()
        self.__AboutWindow = uic.loadUi('../UI/About.ui', self)
        self.__AboutWindow.setFixedSize(400, 449)
        self.__AboutWindow.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowStaysOnTopHint
        )


class UiRoutewindow(QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(UiRoutewindow, self).__init__()
        self.__RouteWindow = uic.loadUi('../UI/InterfaceRoute.ui', self)
        self.AboutTab = UiAboutwindow()
        self.routeData = read_csv('../Route/ROUTE-Template.csv')

        # Llamadas a Métodos
        # Botones de Route Window
        self.__RouteWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__RouteWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__RouteWindow.SearchFileButton.clicked.connect(self.__pressed_search_file_button)
        self.__RouteWindow.SimulateFileButton.clicked.connect(self.__pressed_simulate_file_button)
        # Setups Gráficas de Route Window
        self.__setup_route_figures()

    # Métodos 
    # Abrir Pestaña About
    def clicked_about(self):
        self.AboutTab.show()

    # Cambiar a Bus Window
    def pressed_bus_button(self):
        widget.setCurrentIndex(1)
        self.AboutTab.close()

    # Buscar y definir la extensión del archivo .CSV
    def __pressed_search_file_button(self):
        (filename, extension) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '../Route/',
                                                                      filter=self.tr("csv file (*.csv)"))
        self.__RouteWindow.RouteFileLine.setText(filename)

    # Leer y cargar el archivo .CSV
    def __pressed_simulate_file_button(self):
        csv_file = self.__RouteWindow.RouteFileLine.text()
        try:
            self.routeData = read_csv(csv_file)
        except Exception as ex:
            print(ex)
            print('Not a valid data vector')
            return
        # print(self.routeData)
        self.__plot_route()

    # Definir Plots (MAPA Y PERFIL)
    def __setup_route_figures(self):
        self.figureMapRoute = Figure(tight_layout=True)
        self.figureProfRoute = Figure(tight_layout=True)
        self.canvasMapRoute = FigureCanvas(self.figureMapRoute)
        self.canvasProfRoute = FigureCanvas(self.figureProfRoute)
        self.toolbarMapRoute = NavigationToolbar(self.canvasMapRoute, self)
        self.toolbarProfRoute = NavigationToolbar(self.canvasProfRoute, self)
        self.layoutMapRoute = QtWidgets.QVBoxLayout(self.__RouteWindow.RouteMapWidget)
        self.layoutProfRoute = QtWidgets.QVBoxLayout(self.__RouteWindow.ProfileMapWidget)
        self.layoutMapRoute.addWidget(self.toolbarMapRoute)
        self.layoutMapRoute.addWidget(self.canvasMapRoute)
        self.layoutProfRoute.addWidget(self.toolbarProfRoute)
        self.layoutProfRoute.addWidget(self.canvasProfRoute)
        self.axMapRoute = self.figureMapRoute.add_subplot(111)
        self.axProfRoute = self.figureProfRoute.add_subplot(111)

    # Plotear dos gráficas = Latitud vs Longitud / Altitud vs Distancia
    def __plot_route(self):
        # Map Figure
        long = self.routeData[['LONG']]
        lat = self.routeData[['LAT']]
        self.axMapRoute.cla()
        self.axMapRoute.plot(long, lat, label='LONG-LAT')
        self.axMapRoute.set_title('Route Map', fontsize=12, fontweight="bold")
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
        count_stops = 0
        for n in range(0, len(bus_stop)):
            if bus_stop.iloc[n].values[0] == 1:
                count_stops += 1
                if count_stops == 1:
                    self.axMapRoute.plot(long.iloc[n].values[0], lat.iloc[n].values[0], label='STOP', marker='^',
                                         color='red')
                    self.axProfRoute.plot(dist.iloc[n].values[0], alt.iloc[n].values[0], label='STOP', marker='^',
                                          color='red')
                else:
                    self.axMapRoute.plot(long.iloc[n].values[0], lat.iloc[n].values[0], marker='^', color='red')
                    self.axProfRoute.plot(dist.iloc[n].values[0], alt.iloc[n].values[0], marker='^', color='red')

                self.axMapRoute.annotate(label.iloc[n].values[0], (long.iloc[n].values[0], lat.iloc[n].values[0]),
                                         fontsize=7)
                self.axProfRoute.annotate(label.iloc[n].values[0], (dist.iloc[n].values[0], alt.iloc[n].values[0]),
                                          fontsize=7)

        self.axMapRoute.legend(frameon=False, loc='best')
        self.canvasMapRoute.draw()
        self.axProfRoute.legend(frameon=False, loc='best')
        self.canvasProfRoute.draw()


class UiBuswindow(UiRoutewindow, QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(UiBuswindow, self).__init__()
        self.__BusWindow = uic.loadUi('../UI/InterfaceBus.ui', self)
        self.__BusWindow.BusParametersTab.setCurrentIndex(0)
        self.__BusWindow.PeakTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.StartEndTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.PositionSpeedtabWidget.setCurrentIndex(0)

        # Llamadas a Métodos 
        # Botones de Bus Window
        self.__BusWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__BusWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.PlotBusGenDataButton.clicked.connect(self.__pressed_plot_bus_gen_data_button)
        self.__BusWindow.GenOperationDiagramButton.clicked.connect(self.__pressed_gen_operation_diagram_button)
        # Setups Gráficas de Bus Window
        self.__setupBusDataFigures()
        self.__setupOpDiagramFigures()

    # Métodos
    # Cambiar a Route Window
    def pressed_route_button(self):
        widget.setCurrentIndex(0)
        self.AboutTab.close()

    # Calcular y graficar Velocidad vs Tiempo / Distancia vs Tiempo
    def __pressed_plot_bus_gen_data_button(self):
        speed_table = self.SpeedCurveTable
        acceleration = float(speed_table.item(0, 0).text())
        braking = float(speed_table.item(1, 0).text())
        max_speed = float(speed_table.item(2, 0).text())

        t = np.array([0])
        speed = np.array([0])
        accel = np.array([0])
        decel = np.array([0])
        dist = np.array([0])
        delta_t = 0.5

        for _ in range(0, 600):
            t = np.append(t, t[-1] + delta_t)
            if t[-1] < 150:
                speed = np.append(speed, speed[-1] + acceleration * delta_t)
                if speed[-1] > max_speed / 3.6:
                    speed[-1] = max_speed / 3.6
                else:
                    accel = speed
                decel[0] = float(speed[-1])

            else:
                speed = np.append(speed, speed[-1] - braking * delta_t)
                if speed[-1] < 0:
                    speed[-1] = 0
                else:
                    decel = np.append(decel, speed[-1])

            dist = np.append(dist, dist[-1] + (speed[-1] + speed[-2]) * delta_t / 2)
        accel = np.append(accel, max_speed / 3.6)
        decel = np.append(decel, speed[-1])

        self.speedCurve = speed
        self.accelCurve = accel
        self.decelCurve = decel
        self.timeCurve = t
        self.distanceCurve = dist

        self.__plotBusData()

    #    # Calcular y graficar Curvas de Operación Distancia vs Tiempo / Velocidad vs Tiempo 
    def __pressed_gen_operation_diagram_button(self):
        def state0func(input_tup):
            # State 0: Buses are not in operation
            out_tup = list(input_tup)
            out_tup.pop(3)
            # Time Vector
            out_tup[0] = np.append(input_tup[0], input_tup[0][-1] + input_tup[3])
            # Distance Vector
            out_tup[1] = np.append(input_tup[1], input_tup[1][-1])
            # Speed Vector
            out_tup[2] = np.append(input_tup[2], 0)
            # Label Vector
            out_tup[3].append('')
            # Stop Vector
            out_tup[4].append(0)

            return tuple(out_tup)

        def state1func(input_tup):
            # State 1: Buses are stopped
            out_tup = list(input_tup)
            out_tup.pop(3)
            out_tup.pop(5)
            # Time Vector
            out_tup[0] = np.append(input_tup[0], input_tup[0][-1] + input_tup[3])
            # Distance Vector
            out_tup[1] = np.append(input_tup[1], input_tup[1][-1])
            # Speed Vector
            out_tup[2] = np.append(input_tup[2], 0)
            # Label Vector
            out_tup[3].append(input_tup[6])
            # Stop Vector
            out_tup[4].append(1)

            if tIniPico1 < out_tup[0][-1] <= tEndPico1 or tIniPico2 < out_tup[0][-1] < tEndPico2:
                if out_tup[1][-1] == 0:
                    stop_delay = 100

            return tuple(out_tup)

        def state2func(input_tup):
            # State 2: buses are accelerating
            out_tup = list(input_tup)
            out_tup.pop(3)
            out_tup.pop(3)
            # Time Vector
            out_tup[0] = np.append(input_tup[0], input_tup[0][-1] + input_tup[3])
            # Speed Vector
            out_tup[2] = np.append(input_tup[2], input_tup[4][input_tup[5]])
            # Distance Vector
            out_tup[1] = np.append(input_tup[1], input_tup[1][-1]+(out_tup[2][-1]+out_tup[2][-2])*0.5*input_tup[3])
            # Label Vector
            out_tup[4].append('')
            # Stop Vector
            out_tup[5].append(0)
            # Acceleration Index
            out_tup[3] += 1

            return tuple(out_tup)

        def state3func(input_tup):
            # State 3: Constant speed
            out_tup = list(input_tup)
            out_tup.pop(3)
            out_tup.pop(3)
            # Time Vector
            out_tup[0] = np.append(input_tup[0], input_tup[0][-1] + input_tup[3])
            # Speed Vector
            out_tup[2] = np.append(input_tup[2], input_tup[4])
            # Distance Vector
            out_tup[1] = np.append(input_tup[1], input_tup[1][-1]+(out_tup[2][-1]+out_tup[2][-2])*0.5*input_tup[3])
            # Label Vector
            out_tup[3].append('')
            # Stop Vector
            out_tup[4].append(0)

            return tuple(out_tup)

        def state4func(input_tup):
            # State 4: Decelerating
            out_tup = list(input_tup)
            out_tup.pop(3)
            out_tup.pop(3)
            # Time Vector
            out_tup[0] = np.append(input_tup[0], input_tup[0][-1] + input_tup[3])
            # Speed Vector
            out_tup[2] = np.append(input_tup[2], input_tup[4][input_tup[5]])
            # Distance Vector
            out_tup[1] = np.append(input_tup[1], input_tup[1][-1] + (out_tup[2][-1]+out_tup[2][-2])*0.5*input_tup[3])
            # Label Vector
            out_tup[4].append('')
            # Stop Vector
            out_tup[5].append(0)
            # Deceleration Index
            out_tup[3] += 1

            return tuple(out_tup)

        def find_next_stop(index_stop, bus_stop_route):
            bus_stop1 = index_stop
            while 1:
                index_stop = index_stop + 1
                if index_stop > len(bus_stop_route):
                    bus_stop2 = []
                    break
                if bus_stop_route.iloc[index_stop].values[0] == 1:
                    bus_stop2 = index_stop
                    break
            out_tup = (bus_stop1, bus_stop2)

            return out_tup

        def calculate_braking_distance(decel_bus, delta_t):
            dist_brake = 0

            for N in range(0, len(decel_bus)):
                # distBrake=distBrake+(decel_bus[n]+decel_bus[n-1])*0.5*delta_t
                dist_brake = dist_brake + (decel_bus[N]) * delta_t

            return dist_brake

        def stop_position_labels(dist_route, bus_stop_route, label_route):
            stop_ticks = []
            stop_labels = []
            for N in range(0, len(bus_stop_route)):
                if bus_stop_route.iloc[N].values[0] == 1:
                    stop_ticks.append(dist_route.iloc[N].values[0])
                    stop_labels.append(label_route.iloc[N].values[0] + '=' + '%0.2f' % stop_ticks[-1] + ' km')
                else:
                    pass
            out_tup = (stop_ticks, stop_labels)

            return out_tup

        # Route parameters
        distRoute = RouteWindow.routeData[['DIST']]
        busStopRoute = RouteWindow.routeData[['BUS STOP']]
        labelRoute = RouteWindow.routeData[['LABEL']]

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
        # maxTime2 = t2EndFleet - (numBusesPeak - 1) * dispatchFrequencyPeak

        ## Bus parameters
        accelBus = self.speedCurve
        decelBus = self.decelCurve
        distBrake = calculate_braking_distance(decelBus, deltaT)
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

                inputTup = (
                    self.timeVector, self.distVector, self.speedVector, deltaT, self.labelVector, self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, self.labelVector, self.stopVector) = state0func(
                    inputTup)

                if self.timeVector[-1] >= tIniFleet:
                    if self.timeVector[-1] <= tEndFleet:
                        state = 1
                        timeState1 = self.timeVector[-1]

            elif state == 1:
                labelStop = labelRoute.iloc[indexStop].values[0]
                inputTup = (
                    self.timeVector, self.distVector, self.speedVector, deltaT, self.labelVector, self.stopVector,
                    labelStop)
                (self.timeVector, self.distVector, self.speedVector, self.labelVector, self.stopVector) = state1func(
                    inputTup)

                # Cambio de Velocidad de la Flota en tiempo pico
                if (tIniPico1 < self.timeVector[-1] <= tEndPico1 and self.distVector[-1] == 0) or (
                        tIniPico2 < self.timeVector[-1] < tEndPico2 and self.distVector[-1] == 0):
                    stopDelay = dispatchFrequencyPeak
                    state = 1
                elif (tIniPico1 < self.timeVector[-1] <= tEndPico1) or (tIniPico2 < self.timeVector[-1] < tEndPico2):
                    stopDelay = float(fleetTable.item(4, 0).text()) + 33
                    state = 1
                elif self.distVector[-1] == 0:
                    stopDelay = TimeInTerminal
                    state = 1
                else:
                    stopDelay = float(fleetTable.item(4, 0).text())
                    state = 1

                if self.timeVector[-1] >= timeState1 + stopDelay:
                    state = 2
                    timeState2 = self.timeVector[-1]
                    distState2 = self.distVector[-1]
                    indexAccel = 1
                    busStop1, busStop2 = find_next_stop(indexStop, busStopRoute)
                    distStops = 1000 * (distRoute.iloc[busStop2].values[0] - distRoute.iloc[busStop1].values[0])
                    distStopsAccum = distStops
                    indexStop = busStop2

            elif state == 2:

                inputTup = (
                    self.timeVector, self.distVector, self.speedVector, deltaT, accelBus, indexAccel, self.labelVector,
                    self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, indexAccel, self.labelVector,
                 self.stopVector) = state2func(inputTup)

                if self.speedVector[-1] == maxSpeedBus:
                    state = 3
                    timeState3 = self.timeVector[-1]


            elif state == 3:
                inputTup = (self.timeVector, self.distVector, self.speedVector, deltaT, maxSpeedBus, self.labelVector,
                            self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, self.labelVector, self.stopVector) = state3func(
                    inputTup)

                if self.distVector[-1] - distState2 >= distStops - distBrake:
                    state = 4
                    timeState4 = self.timeVector[-1]
                    indexDecel = 1

            elif state == 4:
                inputTup = (
                    self.timeVector, self.distVector, self.speedVector, deltaT, decelBus, indexDecel, self.labelVector,
                    self.stopVector)
                (self.timeVector, self.distVector, self.speedVector, indexDecel, self.labelVector,
                 self.stopVector) = state4func(inputTup)

                if self.speedVector[-1] == 0:
                    state = 1
                    timeState1 = self.timeVector[-1]

                    if busStop2 == len(busStopRoute) - 1:
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
            # print("Numero de bus:"+str(y))
            for idx, x in enumerate(self.timeVector):
                # print("self.distVector: " + str(self.distVector[idx]),("self.speedVector: " + str(self.speedVector[idx])))
                if tIniPico1 < x <= tEndPico1 or tIniPico2 < x < tEndPico2:
                    if self.distVector[idx] == 0 and self.stateVector[idx] == 2:
                        frec = dispatchFrequency
                else:
                    if self.distVector[idx] == 0:
                        frec = dispatchFrequency

                time_arr.append(
                    datetime.datetime.fromtimestamp(x + timeZoneColombia) + datetime.timedelta(seconds=frec * y))
                time_.append(time_arr[idx].strftime("%I:%M:%S %p"))
                # print(time_[idx])
            self.arrayTime.append(time_arr)
            print(np.shape(self.arrayTime))

        self.stopTicks, self.stopLabels = stop_position_labels(distRoute, busStopRoute, labelRoute)

        self.__plotOpDiagram()

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
    RouteWindow = UiRoutewindow()
    global BusWindow
    BusWindow = UiBuswindow()

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
