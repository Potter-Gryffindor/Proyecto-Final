# Importar Paquetes
from PyQt5 import QtCore, QtGui, QtWidgets, uic

import win32com.client
from win32com.client import makepy
import sys
from pathlib import Path
import os

from pandas import read_csv
import pyarrow.feather as feather
import numpy as np
import datetime
import time
from collections import OrderedDict

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.ticker as ticker

# Variables globales
path_Code = Path.cwd()
path_parent = path_Code.parent
path_UI = Path(path_parent, "UI")
path_Imgs = Path(path_parent, "Imgs")
path_TestCase = Path(path_parent, "TestCase")
path_Route = Path(path_parent, "Route")
path_Manual = Path(path_parent, "User_Manual", "User_Manual.pdf")
path_Results = Path(path_parent, "Results")

# Inicializar OpenDSS
sys.argv = ["makepy", "OpenDSSEngine.DSS"]
makepy.main()
DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution
DSSBus = DSSCircuit.ActiveBus
DSSCtrlQueue = DSSCircuit.CtrlQueue
DSSObj.Start(0)


# Clases
class UiAboutWindow(QtWidgets.QDialog):
    # Constructor
    def __init__(self):
        super(UiAboutWindow, self).__init__()
        ruta_ui = str(Path(path_UI, "About.ui"))
        self.__AboutWindow = uic.loadUi(ruta_ui, self)
        self.__AboutWindow.setFixedSize(400, 449)
        self.__AboutWindow.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowStaysOnTopHint
        )


class UiRouteWindow(QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(UiRouteWindow, self).__init__()
        ruta_ui = str(Path(path_UI, "InterfaceRoute.ui"))
        self.__RouteWindow = uic.loadUi(ruta_ui, self)
        self.AboutTab = UiAboutWindow()
        # self.routeData = feather.read_feather('../Route/Template/ROUTE-Template.feather')
        ruta_template = str(Path(path_Route, "Template/ROUTE-Template.feather"))
        self.routeData = feather.read_feather(ruta_template)

        # Llamadas a Métodos
        # Botones de Route Window
        self.__RouteWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__RouteWindow.actionUser_Manual.triggered.connect(self.clicked_manual)
        self.__RouteWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__RouteWindow.OpportunityButton.clicked.connect(self.pressed_opportunity_button)
        self.__RouteWindow.DynamicButton.clicked.connect(self.pressed_dynamic_button)
        self.__RouteWindow.GridButton.clicked.connect(self.pressed_grid_button)
        self.__RouteWindow.SearchFileButton.clicked.connect(self.__pressed_search_file_button)
        self.__RouteWindow.SimulateFileButton.clicked.connect(self.__pressed_simulate_file_button)
        # Setups Gráficas de Route Window
        self.__setup_route_figures()

    # Métodos
    # Abrir Pestaña About
    def clicked_about(self):
        self.AboutTab.show()

    @staticmethod
    def clicked_manual():
        os.startfile(path_Manual)

    # Cambiar a Bus Window
    def pressed_bus_button(self):
        widget.setCurrentIndex(1)
        self.AboutTab.close()

    # Cambiar a Route Window
    def pressed_route_button(self):
        widget.setCurrentIndex(0)
        self.AboutTab.close()

    # Cambiar a Opportunity Window
    def pressed_opportunity_button(self):
        widget.setCurrentIndex(2)
        self.AboutTab.close()

    # Cambiar a Dynamic Window
    def pressed_dynamic_button(self):
        widget.setCurrentIndex(3)
        self.AboutTab.close()

    # Cambiar a Grid Window
    def pressed_grid_button(self):
        widget.setCurrentIndex(4)
        self.AboutTab.close()

    # Buscar y definir la extensión del archivo .feather or .csv
    def __pressed_search_file_button(self):
        file_filter = "feather file (*.feather);;csv file (*.csv)"
        ruta_route = str(path_Route)
        try:
            (filename, extension) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', ruta_route,
                                                                          filter=self.tr(file_filter))
            self.file_type = filename.split('.')[1]
            print("File extension:", self.file_type)
            self.__RouteWindow.RouteFileLine.setText(filename)
        except IndexError as ex:
            print("Error:", ex)

    # Leer y cargar el archivo .feather or .csv
    def __pressed_simulate_file_button(self):
        file = self.__RouteWindow.RouteFileLine.text()
        print("File:", file)
        try:
            if self.file_type == 'feather':
                self.routeData = feather.read_feather(file)
            elif self.file_type == 'csv':
                self.routeData = read_csv(file)
            else:
                raise Exception('File extension not supported')
        except Exception as ex:
            print(ex)
            print('Not a valid data vector')
            self.routeData = None

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
        self.axMapRoute.plot(long.iloc[:, -1].values, lat.iloc[:, -1].values, label='LONG-LAT')
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
        self.axProfRoute.plot(dist.iloc[:, -1].values, alt.iloc[:, -1].values, label='ALT')
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


class UiBusWindow(UiRouteWindow, QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(UiBusWindow, self).__init__()
        ruta_ui = str(Path(path_UI, "InterfaceBus.ui"))
        self.__BusWindow = uic.loadUi(ruta_ui, self)
        self.__BusWindow.BusParametersTab.setCurrentIndex(0)
        self.__BusWindow.PeakTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.StartEndTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.PositionSpeedtabWidget.setCurrentIndex(0)

        # Llamadas a Métodos
        # Botones de Bus Window
        self.__BusWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__BusWindow.actionUser_Manual.triggered.connect(self.clicked_manual)
        self.__BusWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.__BusWindow.OpportunityButton.clicked.connect(self.pressed_opportunity_button)
        self.__BusWindow.DynamicButton.clicked.connect(self.pressed_dynamic_button)
        self.__BusWindow.GridButton.clicked.connect(self.pressed_grid_button)
        self.PlotBusGenDataButton.clicked.connect(self.__pressed_plot_bus_gen_data_button)
        self.__BusWindow.GenOperationDiagramButton.clicked.connect(self.__pressed_gen_operation_diagram_button)
        # Setups Gráficas de Bus Window
        self.__setup_bus_data_figures()
        self.__setup_op_diagram_figures()

    # Métodos
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

        self.__plot_bus_data()

    #    # Calcular y graficar Curvas de Operación Distancia vs Tiempo / Velocidad vs Tiempo
    def __pressed_gen_operation_diagram_button(self):
        def state0func(input_tup_f):
            # State 0: Buses are not in operation
            (time_vector,
             dist_vector,
             speed_vector,
             delta_t_f,
             label_vector,
             stop_vector) = input_tup_f
            # Time Vector
            time_vector = np.append(time_vector, time_vector[-1] + delta_t_f)
            # Distance Vector
            dist_vector = np.append(dist_vector, dist_vector[-1])
            # Speed Vector
            speed_vector = np.append(speed_vector, 0)
            # Label Vector
            label_vector.append('')
            # Stop Vector
            stop_vector.append(0)
            # Out
            out_tup = (time_vector, dist_vector, speed_vector, label_vector, stop_vector)

            return out_tup

        def state1func(input_tup_f):
            # State 1: Buses are stopped
            (time_vector,
             dist_vector,
             speed_vector,
             delta_t_f,
             label_vector,
             stop_vector,
             label_stop_f) = input_tup_f
            # Time Vector
            time_vector = np.append(time_vector, time_vector[-1] + delta_t_f)
            # Distance Vector
            dist_vector = np.append(dist_vector, dist_vector[-1])
            # Speed Vector
            speed_vector = np.append(speed_vector, 0)
            # Label Vector
            label_vector.append(label_stop_f)
            # Stop Vector
            stop_vector.append(1)
            # Out
            out_tup = (time_vector, dist_vector, speed_vector, label_vector, stop_vector)

            if t_ini_pico1 < time_vector[-1] <= t_end_pico1 or t_ini_pico2 < time_vector[-1] < t_end_pico2:
                if dist_vector[-1] == 0:
                    stop_delay_f = 100

            return out_tup

        def state2func(input_tup_f):
            # State 2: buses are accelerating
            (time_vector,
             dist_vector,
             speed_vector,
             delta_t_f,
             accel_bus_f,
             index_accel_f,
             label_vector,
             stop_vector) = input_tup_f
            # Time Vector
            time_vector = np.append(time_vector, time_vector[-1] + delta_t_f)
            # Speed Vector
            speed_vector = np.append(speed_vector, accel_bus_f[index_accel_f])
            # Distance Vector
            append_par = dist_vector[-1] + (speed_vector[-1] + speed_vector[-2]) * 0.5 * delta_t_f
            dist_vector = np.append(dist_vector, append_par)
            # Label Vector
            label_vector.append('')
            # Stop Vector
            stop_vector.append(0)
            # Acceleration Index
            index_accel_f += 1
            # Out
            out_tup = (time_vector, dist_vector, speed_vector, index_accel_f, label_vector, stop_vector)

            return out_tup

        def state3func(input_tup_f):
            # State 3: Constant speed
            (time_vector,
             dist_vector,
             speed_vector,
             delta_t_f,
             max_speed_bus_f,
             label_vector,
             stop_vector) = input_tup_f
            # Time Vector
            time_vector = np.append(time_vector, time_vector[-1] + delta_t_f)
            # Speed Vector
            speed_vector = np.append(speed_vector, max_speed_bus_f)
            # Distance Vector
            append_par = dist_vector[-1] + (speed_vector[-1] + speed_vector[-2]) * 0.5 * delta_t_f
            dist_vector = np.append(dist_vector, append_par)
            # Label Vector
            label_vector.append('')
            # Stop Vector
            stop_vector.append(0)
            # Out
            out_tup = (time_vector, dist_vector, speed_vector, label_vector, stop_vector)

            return out_tup

        def state4func(input_tup_f):
            # State 4: Decelerating
            (time_vector,
             dist_vector,
             speed_vector,
             delta_t_f,
             decel_bus_f,
             index_decel_f,
             label_vector,
             stop_vector) = input_tup_f
            # Time Vector
            time_vector = np.append(time_vector, time_vector[-1] + delta_t_f)
            # Speed Vector
            speed_vector = np.append(speed_vector, decel_bus_f[index_decel_f])
            # Distance Vector
            append_par = dist_vector[-1] + (speed_vector[-1] + speed_vector[-2]) * 0.5 * delta_t_f
            dist_vector = np.append(dist_vector, append_par)
            # Label Vector
            label_vector.append('')
            # Stop Vector
            stop_vector.append(0)
            # Deceleration Index
            index_decel_f += 1
            # Out
            out_tup = (time_vector, dist_vector, speed_vector, index_decel_f, label_vector, stop_vector)

            return out_tup

        def find_next_stop(index_stop_f, bus_stop_routes):
            bus_stop1_f = index_stop_f
            while 1:
                index_stop_f = index_stop_f + 1
                if index_stop_f > len(bus_stop_routes):
                    bus_stop2_f = []
                    break
                if bus_stop_routes.iloc[index_stop_f].values[0] == 1:
                    bus_stop2_f = index_stop_f
                    break
            out_tup = (bus_stop1_f, bus_stop2_f)

            return out_tup

        def calculate_braking_distance(decel_bus_f, delta_t_f):
            dist_brake_f = 0

            for N in range(0, len(decel_bus_f)):
                # dist_brake=dist_brake+(decel_bus[n]+decel_bus[n-1])*0.5*delta_t
                dist_brake_f = dist_brake_f + (decel_bus_f[N]) * delta_t_f

            return dist_brake_f

        def stop_position_labels(dist_routes, bus_stop_routes, label_routes):
            stop_ticks = []
            stop_labels = []
            for N in range(0, len(bus_stop_routes)):
                if bus_stop_routes.iloc[N].values[0] == 1:
                    stop_ticks.append(dist_routes.iloc[N].values[0])
                    stop_labels.append(label_routes.iloc[N].values[0] + '=' + '%0.2f' % stop_ticks[-1] + ' km')
                else:
                    pass
            out_tup = (stop_ticks, stop_labels)

            return out_tup

        # Route parameters
        dist_route = RouteWindow.routeData[['DIST']]
        bus_stop_route = RouteWindow.routeData[['BUS STOP']]
        label_route = RouteWindow.routeData[['LABEL']]

        # Fleet parameters
        fleet_table = self.__BusWindow.FleetParametersTable
        stop_delay = float(fleet_table.item(4, 0).text())
        time_in_terminal = float(fleet_table.item(5, 0).text())
        t_ini_fleet_qt = self.__BusWindow.STFtimeEdit.time()
        t_ini_fleet = t_ini_fleet_qt.hour() * 3600 + t_ini_fleet_qt.minute() * 60 + t_ini_fleet_qt.second()
        self.init_sec = t_ini_fleet
        t_end_fleet_qt = self.__BusWindow.ETFtimeEdit.time()
        t_end_fleet = t_end_fleet_qt.hour() * 3600 + t_end_fleet_qt.minute() * 60 + t_end_fleet_qt.second()
        t_ini_pico1_qt = self.__BusWindow.STPtimeEdit.time()
        t_ini_pico1 = t_ini_pico1_qt.hour() * 3600 + t_ini_pico1_qt.minute() * 60 + t_ini_pico1_qt.second()
        t_end_pico1_qt = self.__BusWindow.ETPtimeEdit.time()
        t_end_pico1 = t_end_pico1_qt.hour() * 3600 + t_end_pico1_qt.minute() * 60 + t_end_pico1_qt.second()

        t_ini_pico2_qt = self.__BusWindow.STMPtimeEdit.time()
        t_ini_pico2 = t_ini_pico2_qt.hour() * 3600 + t_ini_pico2_qt.minute() * 60 + t_ini_pico2_qt.second()
        t_end_pico2_qt = self.__BusWindow.EMPtimeEdit.time()
        t_end_pico2 = t_end_pico2_qt.hour() * 3600 + t_end_pico2_qt.minute() * 60 + t_end_pico1_qt.second()
        num_buses = int(fleet_table.item(6, 0).text())
        dispatch_frequency = int(fleet_table.item(7, 0).text())
        num_buses_peak = int(fleet_table.item(0, 0).text())
        dispatch_frequency_peak = int(fleet_table.item(3, 0).text())

        # Simulation parameters
        delta_t = 0.2
        max_time = t_end_fleet - (num_buses - 1) * dispatch_frequency
        # maxTime2 = t2EndFleet - (num_buses_peak - 1) * dispatch_frequency_peak

        # Bus parameters
        accel_bus = self.accelCurve
        decel_bus = self.decelCurve
        dist_brake = calculate_braking_distance(decel_bus, delta_t)
        max_speed_bus = accel_bus[-1]

        # Initial conditions
        state = 0
        index_stop = 0

        self.timeVector = np.array([t_ini_fleet])
        self.distVector = np.array([0])
        self.labelVector = ['']
        self.stopVector = [0]
        self.speedVector = np.array([0])
        self.stateVector = []

        # Inicializaciones
        time_state0 = 0
        time_state1 = 0
        index_accel = 0
        dist_state2 = 0
        dist_stops = 0
        index_decel = 0
        bus_stop2 = 0

        while 1:

            self.stateVector.append(state)
            if state == 0:

                input_tup = (self.timeVector,
                             self.distVector,
                             self.speedVector,
                             delta_t,
                             self.labelVector,
                             self.stopVector)

                (self.timeVector,
                 self.distVector,
                 self.speedVector,
                 self.labelVector,
                 self.stopVector) = state0func(input_tup)

                if self.timeVector[-1] >= t_ini_fleet:
                    if self.timeVector[-1] <= t_end_fleet:
                        state = 1
                        time_state1 = self.timeVector[-1]

            elif state == 1:
                label_stop = label_route.iloc[index_stop].values[0]
                input_tup = (self.timeVector,
                             self.distVector,
                             self.speedVector,
                             delta_t,
                             self.labelVector,
                             self.stopVector,
                             label_stop)

                (self.timeVector,
                 self.distVector,
                 self.speedVector,
                 self.labelVector,
                 self.stopVector) = state1func(input_tup)

                # Cambio de Velocidad de la flota en tiempo pico
                # Primer if
                condition1 = t_ini_pico1 < self.timeVector[-1] <= t_end_pico1 and self.distVector[-1] == 0
                condition2 = t_ini_pico2 < self.timeVector[-1] < t_end_pico2 and self.distVector[-1] == 0
                # Primer elif
                condition3 = t_ini_pico1 < self.timeVector[-1] <= t_end_pico1
                condition4 = t_ini_pico2 < self.timeVector[-1] < t_end_pico2
                # Segundo elif
                condition5 = self.distVector[-1] == 0
                if condition1 or condition2:
                    stop_delay = dispatch_frequency_peak
                    state = 1
                elif condition3 or condition4:
                    stop_delay = float(fleet_table.item(4, 0).text()) + 33
                    state = 1
                elif condition5:
                    stop_delay = time_in_terminal
                    state = 1
                else:
                    stop_delay = float(fleet_table.item(4, 0).text())
                    state = 1

                if self.timeVector[-1] >= time_state1 + stop_delay:
                    state = 2
                    time_state2 = self.timeVector[-1]
                    dist_state2 = self.distVector[-1]
                    index_accel = 1
                    bus_stop1, bus_stop2 = find_next_stop(index_stop, bus_stop_route)
                    dist_stops = 1000 * (dist_route.iloc[bus_stop2].values[0] - dist_route.iloc[bus_stop1].values[0])
                    dist_stops_accum = dist_stops
                    index_stop = bus_stop2

            elif state == 2:
                input_tup = (self.timeVector,
                             self.distVector,
                             self.speedVector,
                             delta_t, accel_bus,
                             index_accel,
                             self.labelVector,
                             self.stopVector)

                (self.timeVector,
                 self.distVector,
                 self.speedVector,
                 index_accel,
                 self.labelVector,
                 self.stopVector) = state2func(input_tup)

                if self.speedVector[-1] == max_speed_bus:
                    state = 3
                    time_state3 = self.timeVector[-1]

            elif state == 3:
                input_tup = (self.timeVector,
                             self.distVector,
                             self.speedVector,
                             delta_t,
                             max_speed_bus,
                             self.labelVector,
                             self.stopVector)

                (self.timeVector,
                 self.distVector,
                 self.speedVector,
                 self.labelVector,
                 self.stopVector) = state3func(input_tup)

                if self.distVector[-1] - dist_state2 >= dist_stops - dist_brake:
                    state = 4
                    time_state4 = self.timeVector[-1]
                    index_decel = 1

            elif state == 4:
                input_tup = (self.timeVector,
                             self.distVector,
                             self.speedVector,
                             delta_t,
                             decel_bus,
                             index_decel,
                             self.labelVector,
                             self.stopVector)

                (self.timeVector,
                 self.distVector,
                 self.speedVector,
                 index_decel,
                 self.labelVector,
                 self.stopVector) = state4func(input_tup)

                if self.speedVector[-1] == 0:
                    state = 1
                    time_state1 = self.timeVector[-1]

                    if bus_stop2 == len(bus_stop_route) - 1:
                        index_stop = 0
                        self.distVector[-1] = 0
                        dist_stops_accum = 0

            else:
                pass
            self.__BusWindow.BusprogressBar.setValue(int(100 * self.timeVector[-1] / max_time))

            if self.timeVector[-1] > max_time:
                break

        self.timeVectorDT = []
        today = datetime.date.fromtimestamp(time.time())
        date = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
        self.initial_time = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0)
        stamp = datetime.datetime.timestamp(date)

        for n in range(0, len(self.timeVector)):
            self.timeVectorDT.append(datetime.datetime.fromtimestamp(stamp+n))

        self.arrayTime = []
        self.arrayTimeSeconds = []

        for y in range(num_buses):
            time_arr = []
            time_arr_seconds = []
            time_ = []
            frec = 0
            for idx, x in enumerate(self.timeVector):
                if t_ini_pico1 < x <= t_end_pico1 or t_ini_pico2 < x < t_end_pico2:
                    if self.distVector[idx] == 0 and self.stateVector[idx] == 2:
                        frec = dispatch_frequency
                else:
                    if self.distVector[idx] == 0:
                        frec = dispatch_frequency
                time_ap = datetime.datetime.fromtimestamp(stamp+x) + datetime.timedelta(seconds=frec * y)
                time_arr.append(time_ap)
                time_arr_seconds.append((time_ap - self.initial_time).total_seconds())
                time_.append(time_arr[idx].strftime("%H:%M:%S"))
            self.arrayTime.append(time_arr)
            self.arrayTimeSeconds.append(time_arr_seconds)

        self.stopTicks, self.stopLabels = stop_position_labels(dist_route, bus_stop_route, label_route)

        self.__plot_op_diagram()

    # Definir Plots (VELOCIDAD Y DISTANCIA RECORRIDA)
    def __setup_bus_data_figures(self):
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

    # Definir Plots (VELOCIDAD Y POSICIÓN)
    def __setup_op_diagram_figures(self):
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

    # Plotear dos gráficas = Velocidad vs Tiempo / Distancia vs Tiempo
    def __plot_bus_data(self):
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

    # Plotear dos curvas de Operación = Distancia vs Tiempo / Velocidad vs Tiempo
    def __plot_op_diagram(self):
        self.axOPSpeed.cla()
        self.axOPPosition.cla()
        path_results_aux = str(path_Results).replace("\\", "/")
        path_op_diagram = f"{path_results_aux}/Op_Diagram.txt"
        self.txt_matriz_times = np.array(self.arrayTimeSeconds)
        # print(list(map(list, zip(self.arrayTimeSeconds))))
        dist_vector_km = np.array([0.001*self.distVector])
        txt_matriz_op_diagram = np.concatenate((self.txt_matriz_times.T, dist_vector_km.T), axis=1)
        i = 0
        txt_vector_titles = []
        for x in self.arrayTime:
            i += 1
            txt_vector_titles.append('Time' + str(i))
            self.axOPSpeed.plot(x, 3.6 * self.speedVector, label=f'Bus {i}')
            self.axOPPosition.plot(x, 0.001 * self.distVector, label=f'Bus {i}')
        txt_vector_titles.append('Distance')
        txt_matriz_op_diagram = np.concatenate(([txt_vector_titles], txt_matriz_op_diagram), axis=0)
        np.savetxt(path_op_diagram, txt_matriz_op_diagram, delimiter=",", fmt='% s')

        self.axOPSpeed.set_title('Operating curve (Speed)', fontsize=12, fontweight="bold")
        self.axOPSpeed.set_ylabel('Speed [km/h]', fontsize=10, fontweight="bold")
        self.axOPSpeed.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
        self.axOPSpeed.tick_params(labelsize=8)
        self.axOPSpeed.grid()
        self.axOPSpeed.legend(frameon=False, loc='best')
        self.figureOPSpeed.autofmt_xdate()
        self.canvasOPSpeed.draw()

        self.axOPPosition.set_title('Operating curve (Distance)', fontsize=12, fontweight="bold")
        self.axOPPosition.set_ylabel('Distance [km]', fontsize=10, fontweight="bold")
        self.axOPPosition.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
        self.axOPPosition.tick_params(labelsize=8)
        self.axOPPosition.grid(which='minor')
        self.axOPPosition.legend(frameon=False, loc='best')
        self.figureOPPosition.autofmt_xdate()

        self.axOPPosition.yaxis.set_major_locator(ticker.FixedLocator([]))
        self.axOPPosition.yaxis.set_minor_locator(ticker.FixedLocator(self.stopTicks))
        self.axOPPosition.yaxis.set_minor_formatter(ticker.FixedFormatter(self.stopLabels))

        for tick in self.axOPPosition.yaxis.get_minor_ticks():
            tick.label.set_fontsize(7)

        self.canvasOPPosition.draw()


class UiOpportunityWindow(UiBusWindow, QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(UiOpportunityWindow, self).__init__()
        ruta_ui = str(Path(path_UI, "InterfaceOpportunity.ui"))
        self.__OpportunityWindow = uic.loadUi(ruta_ui, self)
        self.__OpportunityWindow.SimulationOpportunityTab.setCurrentIndex(0)
        self.__OpportunityWindow.ElementscomboBox.setCurrentIndex(0)
        self.__OpportunityWindow.VariablescomboBox.setCurrentIndex(0)
        self.group_box_layout = None
        self.group_box = None
        self.charger_sections = None
        self.charger_sections_boxes = None
        self.charger_sections_scroll = None

        # Llamadas a Métodos
        # Botones de Opportunity Window
        self.__OpportunityWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__OpportunityWindow.actionUser_Manual.triggered.connect(self.clicked_manual)
        self.__OpportunityWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.__OpportunityWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__OpportunityWindow.DynamicButton.clicked.connect(self.pressed_dynamic_button)
        self.__OpportunityWindow.GridButton.clicked.connect(self.pressed_grid_button)
        self.__OpportunityWindow.RefreshSectionsButton.clicked.connect(self.__pressed_refresh_sections_button)
        self.__OpportunityWindow.SaveSectionsButton.clicked.connect(self.__pressed_save_sections_button)
        self.__OpportunityWindow.OpportunityLoadSimButton.clicked.connect(self.__pressed_load_sim_opportunity_button)
        self.__OpportunityWindow.OpportunityGraphButton.clicked.connect(self.__pressed_graph_opportunity_button)
        self.__OpportunityWindow.ElementscomboBox.currentTextChanged.connect(self.__selected_elements)
        # Setups Gráficas de Opportunity Window
        self.__setup_opportunity_diagram_figures()

    # Métodos
    # Actualizar secciones electrificadas
    def __pressed_refresh_sections_button(self):
        # Limpiar contenido de Layout
        for i in reversed(range(self.__OpportunityWindow.StopslLayout.count())):
            self.__OpportunityWindow.StopslLayout.itemAt(i).widget().setParent(None)
        # Definir Widgets
        self.group_box = QtWidgets.QGroupBox("List")
        self.group_box.setFont(QtGui.QFont("MS Sans Serif", 10, QtGui.QFont.Bold))
        self.group_box.setStyleSheet("background-color:white;")
        # Layout Interno del Group Box
        self.group_box_layout = QtWidgets.QVBoxLayout()
        # Route Data
        label = RouteWindow.routeData[['LABEL']].iloc[:, -1].values
        # Charger Sections
        self.charger_sections = [label[i] for i in range(len(label)) if label[i] is not None]
        # Check Box List
        self.charger_sections_boxes = []
        for i in range(len(self.charger_sections)):
            self.charger_sections_boxes.append(QtWidgets.QCheckBox(self.charger_sections[i]))
            self.group_box_layout.addWidget(self.charger_sections_boxes[i])
        # Charger Sections GroupBox
        self.group_box.setLayout(self.group_box_layout)
        # Charger Sections Scroll
        self.charger_sections_scroll = QtWidgets.QScrollArea()
        self.charger_sections_scroll.setWidgetResizable(True)
        self.charger_sections_scroll.setWidget(self.group_box)
        # Charger Sections Layout
        self.__OpportunityWindow.StopslLayout.addWidget(self.charger_sections_scroll)

    # Guardar secciones electrificadas
    def __pressed_save_sections_button(self):
        self.section_select = []
        self.charger_list = []
        i = 0
        for section in self.charger_sections_boxes:
            if section.isChecked():
                i += 1
                self.section_select.append(section.text())
                self.charger_list.append(f"C{i}")
        # Convertir la lista de Secciones a String
        text_stops = ','.join(self.section_select)
        # Crear Item de paradas para actualizar la tabla
        stops_item = QtWidgets.QTableWidgetItem(text_stops)
        stops_item.setFont(QtGui.QFont("MS Sans Serif", 8, QtGui.QFont.Bold))
        self.__OpportunityWindow.OppChargingParametersTable.setItem(2, 0, stops_item)

    # Modificar valor de Variables dependiendo el Elemento
    def __selected_elements(self):
        self.__OpportunityWindow.VariablescomboBox.clear()
        bus_variables = ['Energy', 'Power', 'Slope', '(SoC) State of Charge', 'Stop vector', 'Charger vector']
        element_type = self.__OpportunityWindow.ElementscomboBox.currentIndex()
        if element_type == 0:
            self.__OpportunityWindow.VariablescomboBox.addItems(bus_variables)
        elif element_type == 1:
            self.__OpportunityWindow.VariablescomboBox.addItem('Charger vector')

    # Definir Plots (Opportunity Window)
    def __setup_opportunity_diagram_figures(self):
        self.figureOppCharging = Figure(tight_layout=True)
        self.canvasOppCharging = FigureCanvas(self.figureOppCharging)
        self.toolbarOppCharging = NavigationToolbar(self.canvasOppCharging, self)
        self.layoutOppCharging = QtWidgets.QVBoxLayout(self.__OpportunityWindow.OpportunityCurveWidget)
        self.layoutOppCharging.addWidget(self.toolbarOppCharging)
        self.layoutOppCharging.addWidget(self.canvasOppCharging)  #
        self.axOppCharging = self.figureOppCharging.add_subplot(111)

    # Cargar simulación de Oportunidad
    def __pressed_load_sim_opportunity_button(self):
        def calculate_angle(dist_vector_f, dist_route_f, alt_route_f):
            sin_theta_vector_route = []
            for N in range(0, len(dist_route_f) - 1):
                # point route : N
                sin_theta_part1 = alt_route_f.iloc[N + 1].values[0] - alt_route_f.iloc[N].values[0]
                sin_theta_part2 = (1000 * dist_route_f.iloc[N + 1].values[0] - 1000 * dist_route_f.iloc[N].values[0])
                sin_theta = sin_theta_part1 / sin_theta_part2
                sin_theta_vector_route.append(sin_theta)

            sin_theta_vector_route.append(sin_theta_vector_route[-1])
            time.sleep(5)
            sin_theta_vector_f = []
            arr = []
            for N in range(0, len(dist_route_f)):
                arr.append(1000 * dist_route_f.iloc[N].values[0])
            dist_route_np = np.array(arr)

            for N in range(0, len(dist_vector_f) - 1):
                # point1=dist_vector[n]
                point2 = dist_vector_f[N + 1]
                index = np.where(point2 >= dist_route_np)
                k = index[0][-1]
                sin_theta_tot = sin_theta_vector_route[k]
                sin_theta_vector_f.append(sin_theta_tot)

            sin_theta_vector_f.append(sin_theta_vector_f[-1])

            return sin_theta_vector_f

        # Parameters
        # Simulation parameters
        delta_t = 0.2

        # Bus parameters
        bus_table = BusWindow.BusParametersTable
        fric = float(bus_table.item(0, 0).text())
        mass = float(bus_table.item(1, 0).text())
        grav = float(bus_table.item(2, 0).text())
        rho = float(bus_table.item(3, 0).text())
        alpha = float(bus_table.item(4, 0).text())
        area = float(bus_table.item(5, 0).text())
        p_aux = 1000 * float(bus_table.item(6, 0).text())
        n_out = 0.01 * float(bus_table.item(7, 0).text())
        n_in = 0.01 * float(bus_table.item(8, 0).text())

        # Opportunity charge parameters
        charging_table = self.__OpportunityWindow.OppChargingParametersTable
        bc = float(charging_table.item(0, 0).text())
        so_ci = 0.01 * float(charging_table.item(1, 0).text())
        text_stops = charging_table.item(2, 0).text()
        cl = text_stops.split(',')
        cp = float(charging_table.item(3, 0).text())
        n_c = 0.01 * float(charging_table.item(4, 0).text())
        it = float(charging_table.item(5, 0).text())
        dt = float(charging_table.item(6, 0).text())

        # Fleet operation time for extra loads
        fleet_table = BusWindow.FleetParametersTable
        stop_delay = float(fleet_table.item(4, 0).text())
        time_in_terminal = float(fleet_table.item(5, 0).text())
        t_ini_fleet_qt = BusWindow.STFtimeEdit.time()
        t_ini_fleet = t_ini_fleet_qt.hour() * 3600 + t_ini_fleet_qt.minute() * 60 + t_ini_fleet_qt.second()
        t_end_fleet_qt = BusWindow.ETFtimeEdit.time()
        t_end_fleet = t_end_fleet_qt.hour() * 3600 + t_end_fleet_qt.minute() * 60 + t_end_fleet_qt.second()

        t_ini_pico1_qt = BusWindow.STPtimeEdit.time()
        t_ini_pico1 = t_ini_pico1_qt.hour() * 3600 + t_ini_pico1_qt.minute() * 60 + t_ini_pico1_qt.second()
        t_end_pico1_qt = BusWindow.ETPtimeEdit.time()
        t_end_pico1 = t_end_pico1_qt.hour() * 3600 + t_end_pico1_qt.minute() * 60 + t_end_pico1_qt.second()

        t_ini_pico2_qt = BusWindow.STMPtimeEdit.time()
        t_ini_pico2 = t_ini_pico2_qt.hour() * 3600 + t_ini_pico2_qt.minute() * 60 + t_ini_pico2_qt.second()
        t_end_pico2_qt = BusWindow.EMPtimeEdit.time()
        t_end_pico2 = t_end_pico2_qt.hour() * 3600 + t_end_pico2_qt.minute() * 60 + t_end_pico1_qt.second()

        # Fleet operation results
        time_vector = BusWindow.timeVector
        time_vector_dt = BusWindow.timeVectorDT
        speed_vector = BusWindow.speedVector
        dist_vector = BusWindow.distVector
        state_vector = BusWindow.stateVector
        stop_vector = BusWindow.stopVector
        label_vector = BusWindow.labelVector

        # Route Data
        dist_route = RouteWindow.routeData[['DIST']]
        alt_route = RouteWindow.routeData[['ALT']]

        # Angle vector
        sin_theta_vector = calculate_angle(dist_vector, dist_route, alt_route)
        energy_vector = []
        so_c_vector = [so_ci]
        charger_vector = []
        charger_matrix = [[] for _ in range(len(cl))]

        for n in range(0, len(time_vector) - 1):

            if time_vector[n] > t_ini_fleet:
                aux_onoff = 1
            else:
                aux_onoff = 0

            energy = (n_out * (fric * (mass + bc * 11.1) * grav + 0.5 * rho * alpha * area * speed_vector[n] *
                               speed_vector[n]) * speed_vector[n] * delta_t + n_in * mass * grav * sin_theta_vector[n] *
                      speed_vector[n] * delta_t + mass * n_in * (speed_vector[n + 1] - speed_vector[n]) *
                      speed_vector[n] * delta_t + aux_onoff * p_aux * delta_t) / 36e5
            if n == 0:
                energy_vector.append(energy)
            else:
                energy_vector.append(energy_vector[-1] + energy)
            if stop_vector[n] == 1:
                if label_vector[n] in cl:
                    index_stop = cl.index(label_vector[n])
                    ch_onoff = 1
                else:
                    index_stop = None
                    ch_onoff = 0
            else:
                index_stop = None
                ch_onoff = 0

            charger_vector.append(ch_onoff * cp)

            for charger_num in range(len(charger_matrix)):
                if (idx := charger_num) == index_stop:
                    charger_matrix[idx].append(ch_onoff * cp)
                else:
                    charger_matrix[idx].append(0)

            if (soC := (so_c_vector[-1] * bc - energy + charger_vector[-1] * delta_t / 3600) / bc) <= 1:
                so_c_vector.append(soC)
            else:
                so_c_vector.append(1)

            self.__OpportunityWindow.OpportunityprogressBar.setValue(int(100 * n / (len(time_vector) - 2)))

        energy_vector.append(energy_vector[-1])
        charger_vector.append(charger_vector[-1])
        for charger_num in range(len(charger_matrix)):
            charger_matrix[charger_num].append(charger_matrix[charger_num][-1])
        power_vector = [0]

        for n in range(1, len(time_vector) - 1):
            power_vector.append(-(energy_vector[n - 1] - energy_vector[n]) / (delta_t / 3600))
        power_vector.append(power_vector[-1])

        num_chargers = len(charger_matrix)
        inicio = BusWindow.arrayTime[0][0]
        fin = BusWindow.arrayTime[-1][-1]
        lista_tiempo = [inicio + datetime.timedelta(seconds=s) for s in range((fin - inicio).seconds + 1)]
        charger_final_matrix = [[] for _ in range(num_chargers)]
        for t in lista_tiempo:
            sum_c = [0 for _ in range(num_chargers)]
            for c in range(num_chargers):
                for vect_t in BusWindow.arrayTime:
                    try:
                        indice = vect_t.index(t)
                        sum_c[c] += charger_matrix[c][indice]
                    except Exception:
                        continue
                charger_final_matrix[c].append(sum_c[c])

        self.energyVector = energy_vector
        self.powerVector = power_vector
        self.sinThetaVector = sin_theta_vector
        self.SoCVector = so_c_vector
        self.chargerVector = charger_vector
        self.charger_matrix = charger_matrix
        self.lista_tiempo = lista_tiempo
        self.charger_final_matrix = charger_final_matrix

    # Graficar simulación de Oportunidad (Dropdown options)
    def __pressed_graph_opportunity_button(self):
        element_type = self.__OpportunityWindow.ElementscomboBox.currentIndex()
        if element_type == 0:
            plot_type = self.__OpportunityWindow.VariablescomboBox.currentIndex()
            self.axOppCharging.cla()
            if plot_type == 0:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axOppCharging.plot(x, self.energyVector, label=f'Bus {i}')
                self.axOppCharging.set_title('Energy Curve', fontsize=12, fontweight="bold")
                self.axOppCharging.set_ylabel('Energy [kWh]', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 1:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axOppCharging.plot(x, self.powerVector, label=f'Bus {i}')
                self.axOppCharging.set_title('Power Curve', fontsize=12, fontweight="bold")
                self.axOppCharging.set_ylabel('Power [kW]', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 2:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axOppCharging.plot(x, self.sinThetaVector, label=f'Bus {i}')
                self.axOppCharging.set_title('Slope', fontsize=12, fontweight="bold")
                self.axOppCharging.set_ylabel('sin(theta)', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 3:
                path_results_aux = str(path_Results).replace("\\", "/")
                path_soc_diagram = f"{path_results_aux}/SoC_Diagram_Opp.txt"
                soc_vector = np.array([100 * np.array(self.SoCVector)])
                txt_matriz_times = BusWindow.txt_matriz_times.T
                txt_matriz_soc_diagram = np.concatenate((txt_matriz_times, soc_vector.T), axis=1)
                txt_vector_titles = []
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    txt_vector_titles.append('Time' + str(i))
                    self.axOppCharging.plot(x, 100 * np.array(self.SoCVector), label=f'Bus {i}')
                txt_vector_titles.append('SoC')
                txt_matriz_soc_diagram = np.concatenate(([txt_vector_titles], txt_matriz_soc_diagram), axis=0)
                np.savetxt(path_soc_diagram, txt_matriz_soc_diagram, delimiter=",", fmt='% s')
                self.axOppCharging.set_title('State of Charge', fontsize=12, fontweight="bold")
                self.axOppCharging.set_ylabel('%', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 4:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axOppCharging.plot(x, BusWindow.stopVector, label=f'Bus {i}')
                self.axOppCharging.set_title('Stop Vector', fontsize=12, fontweight="bold")
                self.axOppCharging.set_ylabel('', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 5:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axOppCharging.plot(x, self.chargerVector, label=f'Bus {i}')
                self.axOppCharging.set_title('Charger Vector', fontsize=12, fontweight="bold")
                self.axOppCharging.set_ylabel('kW', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
        elif element_type == 1:
            plot_type = self.__OpportunityWindow.VariablescomboBox.currentIndex()
            self.axOppCharging.cla()

            if plot_type == 0:
                i = 0
                for c in self.charger_final_matrix:
                    self.axOppCharging.plot(self.lista_tiempo, c, label=f'C {i + 1}')
                    i += 1
                self.axOppCharging.set_title('Charger Vector', fontsize=12, fontweight="bold")
                self.axOppCharging.set_ylabel('kW', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")

        self.axOppCharging.tick_params(labelsize=10)
        self.axOppCharging.grid()
        self.axOppCharging.legend(frameon=False, loc='best')
        self.figureOppCharging.autofmt_xdate()
        self.canvasOppCharging.draw()


class UiDynamicWindow(UiOpportunityWindow, QtWidgets.QMainWindow):
    # Constructor
    def __init__(self):
        super(UiDynamicWindow, self).__init__()
        ruta_ui = str(Path(path_UI, "InterfaceDynamic.ui"))
        self.__DynamicWindow = uic.loadUi(ruta_ui, self)
        self.__DynamicWindow.SimulationDynamicTab.setCurrentIndex(0)
        self.__DynamicWindow.ElementscomboBox.setCurrentIndex(0)
        self.__DynamicWindow.VariablescomboBox.setCurrentIndex(0)

        # Llamadas a Métodos
        # Botones de Opportunity Window
        self.__DynamicWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__DynamicWindow.actionUser_Manual.triggered.connect(self.clicked_manual)
        self.__DynamicWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.__DynamicWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__DynamicWindow.OpportunityButton.clicked.connect(self.pressed_opportunity_button)
        self.__DynamicWindow.GridButton.clicked.connect(self.pressed_grid_button)
        self.__DynamicWindow.RefreshSectionsButton.clicked.connect(self.__pressed_refresh_sections_button)
        self.__DynamicWindow.SaveSectionsButton.clicked.connect(self.__pressed_save_sections_button)
        self.__DynamicWindow.DynamicLoadSimButton.clicked.connect(self.__pressed_load_sim_imc_button)
        self.__DynamicWindow.DynamicGraphButton.clicked.connect(self.__pressed_graph_imc_button)
        self.__DynamicWindow.ElementscomboBox.currentTextChanged.connect(self.__selected_elements)
        # Setups Gráficas de In Motion Window
        self.__setup_dynamic_diagram_figures()

    # Métodos
    # Actualizar secciones electrificadas
    def __pressed_refresh_sections_button(self):
        # Limpiar contenido de Layout
        for i in reversed(range(self.__DynamicWindow.StopslLayout.count())):
            self.__DynamicWindow.StopslLayout.itemAt(i).widget().setParent(None)
        # Definir Widgets
        self.group_box = QtWidgets.QGroupBox("Charge Sections")
        self.group_box.setFont(QtGui.QFont("MS Sans Serif", 10, QtGui.QFont.Bold))
        self.group_box.setStyleSheet("background-color:white;")
        # Layout Interno del Group Box
        self.group_box_layout = QtWidgets.QVBoxLayout()
        # Route Data
        label = RouteWindow.routeData[['LABEL']].iloc[:, -1].values
        # Charger Sections
        self.stop_list = [label[i] for i in range(len(label)) if label[i] is not None]
        self.charger_sections = [f"{self.stop_list[i]}-{self.stop_list[i + 1]}" for i in range(len(self.stop_list) - 1)]
        # Check Box List
        self.charger_sections_boxes = []
        for i in range(len(self.charger_sections)):
            self.charger_sections_boxes.append(QtWidgets.QCheckBox(self.charger_sections[i]))
            self.group_box_layout.addWidget(self.charger_sections_boxes[i])
        # Charger Sections GroupBox
        self.group_box.setLayout(self.group_box_layout)
        # Charger Sections Scroll
        self.charger_sections_scroll = QtWidgets.QScrollArea()
        self.charger_sections_scroll.setWidgetResizable(True)
        self.charger_sections_scroll.setWidget(self.group_box)
        # Charger Sections Layout
        self.__DynamicWindow.StopslLayout.addWidget(self.charger_sections_scroll)

    # Guardar secciones electrificadas
    def __pressed_save_sections_button(self):
        self.section_select = []
        self.section_list = []
        i = 0
        for section in self.charger_sections_boxes:
            if section.isChecked():
                i += 1
                self.section_select.append(section.text())
        section_select_string = ','.join(self.section_select).replace('-', ',')
        stop_list = section_select_string.split(',')
        new_stop_list = list(OrderedDict.fromkeys(stop_list))
        self.cl_aux = tuple(new_stop_list)
        for i in range(len(stop_list) - 1):
            if (stop := stop_list[i]) == stop_list[i + 1]:
                new_stop_list.remove(stop)
        self.section_select = []
        count = 1
        for i in range(0, len(new_stop_list) - 1, 2):
            self.section_select.append(f"{new_stop_list[i]}-{new_stop_list[i + 1]}")
            self.section_list.append(f"S{count}")
            count += 1
        num_sections = len(self.section_list)
        self.stops_for_section = [[] for _ in range(num_sections)]
        for section in self.section_select:
            inicio_section = section.split('-')[0]
            fin_section = section.split('-')[1]
            for i in range(self.cl_aux.index(inicio_section), self.cl_aux.index(fin_section) + 1):
                self.stops_for_section[self.section_select.index(section)].append(self.cl_aux[i])
        self.cl_list = [x.split('-') for x in self.section_select]
        # Convertir la lista de Secciones a String
        text_stops = ','.join(self.section_select)
        # Crear Item de paradas para actualizar la tabla
        stops_item = QtWidgets.QTableWidgetItem(text_stops)
        stops_item.setFont(QtGui.QFont("MS Sans Serif", 8, QtGui.QFont.Bold))
        self.__DynamicWindow.ImcChargingParametersTable.setItem(2, 0, stops_item)

    # Modificar valor de Variables dependiendo el Elemento
    def __selected_elements(self):
        self.__DynamicWindow.VariablescomboBox.clear()
        bus_variables = ['Energy', 'Power', 'Slope', '(SoC) State of Charge', 'Stop vector', 'Charger vector']
        element_type = self.__DynamicWindow.ElementscomboBox.currentIndex()
        if element_type == 0:
            self.__DynamicWindow.VariablescomboBox.addItems(bus_variables)
        elif element_type == 1:
            self.__DynamicWindow.VariablescomboBox.addItem('Section vector')

    # Definir Plots (Dynamic Window)
    def __setup_dynamic_diagram_figures(self):
        self.figureImcCharging = Figure(tight_layout=True)
        self.canvasImcCharging = FigureCanvas(self.figureImcCharging)
        self.toolbarImcCharging = NavigationToolbar(self.canvasImcCharging, self)
        self.layoutImcCharging = QtWidgets.QVBoxLayout(self.__DynamicWindow.DynamicCurveWidget)
        self.layoutImcCharging.addWidget(self.toolbarImcCharging)
        self.layoutImcCharging.addWidget(self.canvasImcCharging)  #
        self.axImcCharging = self.figureImcCharging.add_subplot(111)

    # Cargar simulación de IMC
    def __pressed_load_sim_imc_button(self):
        def calculate_angle(dist_vector_f, dist_route_f, alt_route_f):
            sin_theta_vector_route = []
            for N in range(0, len(dist_route_f) - 1):
                # point route : N
                sin_theta_part1 = alt_route_f.iloc[N + 1].values[0] - alt_route_f.iloc[N].values[0]
                sin_theta_part2 = (1000 * dist_route_f.iloc[N + 1].values[0] - 1000 * dist_route_f.iloc[N].values[0])
                sin_theta = sin_theta_part1 / sin_theta_part2
                sin_theta_vector_route.append(sin_theta)

            sin_theta_vector_route.append(sin_theta_vector_route[-1])
            time.sleep(5)
            sin_theta_vector_f = []
            arr = []
            for N in range(0, len(dist_route_f)):
                arr.append(1000 * dist_route_f.iloc[N].values[0])
            dist_route_np = np.array(arr)

            for N in range(0, len(dist_vector_f) - 1):
                # point1=dist_vector[n]
                point2 = dist_vector_f[N + 1]
                index = np.where(point2 >= dist_route_np)
                k = index[0][-1]
                sin_theta_tot = sin_theta_vector_route[k]
                sin_theta_vector_f.append(sin_theta_tot)

            sin_theta_vector_f.append(sin_theta_vector_f[-1])

            return sin_theta_vector_f

        # Parameters
        # Simulation parameters
        delta_t = 0.2

        # Bus parameters
        bus_table = BusWindow.BusParametersTable
        fric = float(bus_table.item(0, 0).text())
        mass = float(bus_table.item(1, 0).text())
        grav = float(bus_table.item(2, 0).text())
        rho = float(bus_table.item(3, 0).text())
        alpha = float(bus_table.item(4, 0).text())
        area = float(bus_table.item(5, 0).text())
        p_aux = 1000 * float(bus_table.item(6, 0).text())
        n_out = 0.01 * float(bus_table.item(7, 0).text())
        n_in = 0.01 * float(bus_table.item(8, 0).text())

        # Opportunity charge parameters
        charging_table = self.__DynamicWindow.ImcChargingParametersTable
        bc = float(charging_table.item(0, 0).text())
        so_ci = 0.01 * float(charging_table.item(1, 0).text())
        text_stops = charging_table.item(2, 0).text()
        cl = text_stops.split(',')
        cp = float(charging_table.item(3, 0).text())
        n_c = 0.01 * float(charging_table.item(4, 0).text())
        it = float(charging_table.item(5, 0).text())
        dt = float(charging_table.item(6, 0).text())

        # Fleet operation time for extra loads
        fleet_table = BusWindow.FleetParametersTable
        stop_delay = float(fleet_table.item(4, 0).text())
        time_in_terminal = float(fleet_table.item(5, 0).text())
        t_ini_fleet_qt = BusWindow.STFtimeEdit.time()
        t_ini_fleet = t_ini_fleet_qt.hour() * 3600 + t_ini_fleet_qt.minute() * 60 + t_ini_fleet_qt.second()
        t_end_fleet_qt = BusWindow.ETFtimeEdit.time()
        t_end_fleet = t_end_fleet_qt.hour() * 3600 + t_end_fleet_qt.minute() * 60 + t_end_fleet_qt.second()

        t_ini_pico1_qt = BusWindow.STPtimeEdit.time()
        t_ini_pico1 = t_ini_pico1_qt.hour() * 3600 + t_ini_pico1_qt.minute() * 60 + t_ini_pico1_qt.second()
        t_end_pico1_qt = BusWindow.ETPtimeEdit.time()
        t_end_pico1 = t_end_pico1_qt.hour() * 3600 + t_end_pico1_qt.minute() * 60 + t_end_pico1_qt.second()

        t_ini_pico2_qt = BusWindow.STMPtimeEdit.time()
        t_ini_pico2 = t_ini_pico2_qt.hour() * 3600 + t_ini_pico2_qt.minute() * 60 + t_ini_pico2_qt.second()
        t_end_pico2_qt = BusWindow.EMPtimeEdit.time()
        t_end_pico2 = t_end_pico2_qt.hour() * 3600 + t_end_pico2_qt.minute() * 60 + t_end_pico1_qt.second()

        # Fleet operation results
        time_vector = BusWindow.timeVector
        time_vector_dt = BusWindow.timeVectorDT
        speed_vector = BusWindow.speedVector
        dist_vector = BusWindow.distVector
        state_vector = BusWindow.stateVector
        stop_vector = BusWindow.stopVector
        label_vector = BusWindow.labelVector

        # Route Data
        dist_route = RouteWindow.routeData[['DIST']]
        alt_route = RouteWindow.routeData[['ALT']]

        # Angle vector
        sin_theta_vector = calculate_angle(dist_vector, dist_route, alt_route)
        energy_vector = []
        power_vector = [0]
        so_c_vector = [so_ci]
        charger_vector = []
        charger_matrix = [[] for _ in range(len(cl))]
        active_section = 0
        num_chargers = len(cl)
        section_num = None

        for n in range(0, len(time_vector) - 1):

            if time_vector[n] > t_ini_fleet:
                aux_onoff = 1
            else:
                aux_onoff = 0

            energy = (n_out * (fric * (mass + bc * 11.1) * grav + 0.5 * rho * alpha * area * speed_vector[n] *
                               speed_vector[n]) * speed_vector[n] * delta_t + n_in * mass * grav * sin_theta_vector[n] *
                      speed_vector[n] * delta_t + mass * n_in * (speed_vector[n + 1] - speed_vector[n]) *
                      speed_vector[n] * delta_t + aux_onoff * p_aux * delta_t) / 36e5
            if n == 0:
                energy_vector.append(energy)
            else:
                energy_vector.append(energy_vector[-1] + energy)
            if n > 0:
                power_vector.append(-(energy_vector[n - 1] - energy_vector[n]) / (delta_t / 3600))
            if stop_vector[n] == 1 or active_section == 1:
                if ((label := label_vector[n]) in self.cl_aux) or (active_section == 1):
                    for i in range(len(self.stops_for_section)):
                        if label in self.stops_for_section[i]:
                            section_num = i
                            break
                    if label == self.cl_list[section_num][0]:
                        active_section = 1
                    elif label == self.cl_list[section_num][1]:
                        active_section = 0
                    index_stop = section_num
                    ch_onoff = 1
                else:
                    index_stop = None
                    ch_onoff = 0
            else:
                index_stop = None
                ch_onoff = 0
            if (power := power_vector[n]) >= 0:
                charger_vector.append(ch_onoff * (cp + power))
            else:
                charger_vector.append(ch_onoff * cp)

            for charger_num in range(len(charger_matrix)):
                if charger_num == index_stop:
                    if power_vector[n] >= 0:
                        charger_matrix[charger_num].append(ch_onoff * (cp + power_vector[n]))
                    else:
                        charger_matrix[charger_num].append(ch_onoff * cp)
                else:
                    charger_matrix[charger_num].append(0)
            if (soC := (so_c_vector[-1] * bc - energy + charger_vector[-1] * delta_t / 3600) / bc) <= 1:
                so_c_vector.append(soC)
            else:
                so_c_vector.append(1)
            self.__DynamicWindow.DynamicprogressBar.setValue(int(100 * n / (len(time_vector) - 2)))

        energy_vector.append(energy_vector[-1])
        charger_vector.append(charger_vector[-1])
        power_vector.append(power_vector[-1])
        for charger_num in range(len(charger_matrix)):
            charger_matrix[charger_num].append(charger_matrix[charger_num][-1])

        inicio = BusWindow.arrayTime[0][0]
        fin = BusWindow.arrayTime[-1][-1]
        lista_tiempo = [inicio + datetime.timedelta(seconds=s) for s in range((fin - inicio).seconds + 1)]
        charger_final_matrix = [[] for _ in range(num_chargers)]
        for t in lista_tiempo:
            sum_c = [0 for _ in range(num_chargers)]
            for c in range(num_chargers):
                for vect_t in BusWindow.arrayTime:
                    try:
                        indice = vect_t.index(t)
                        sum_c[c] += charger_matrix[c][indice]
                    except Exception:
                        continue
                charger_final_matrix[c].append(sum_c[c])

        self.energyVector = energy_vector
        self.powerVector = power_vector
        self.sinThetaVector = sin_theta_vector
        self.SoCVector = so_c_vector
        self.chargerVector = charger_vector
        self.charger_matrix = charger_matrix
        self.lista_tiempo = lista_tiempo
        self.charger_final_matrix = charger_final_matrix

    # Graficar simulación de IMC (Dropdown options)
    def __pressed_graph_imc_button(self):
        element_type = self.__DynamicWindow.ElementscomboBox.currentIndex()
        if element_type == 0:
            plot_type = self.__DynamicWindow.VariablescomboBox.currentIndex()
            self.axImcCharging.cla()
            if plot_type == 0:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axImcCharging.plot(x, self.energyVector, label=f'Bus {i}')
                self.axImcCharging.set_title('Energy Curve', fontsize=12, fontweight="bold")
                self.axImcCharging.set_ylabel('Energy [kWh]', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 1:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axImcCharging.plot(x, self.powerVector, label=f'Bus {i}')
                self.axImcCharging.set_title('Power Curve', fontsize=12, fontweight="bold")
                self.axImcCharging.set_ylabel('Power [kW]', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 2:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axImcCharging.plot(x, self.sinThetaVector, label=f'Bus {i}')
                self.axImcCharging.set_title('Slope', fontsize=12, fontweight="bold")
                self.axImcCharging.set_ylabel('sin(theta)', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 3:
                path_results_aux = str(path_Results).replace("\\", "/")
                path_soc_diagram = f"{path_results_aux}/SoC_Diagram_IMC.txt"
                soc_vector = np.array([100 * np.array(self.SoCVector)])
                txt_matriz_times = BusWindow.txt_matriz_times.T
                txt_matriz_soc_diagram = np.concatenate((txt_matriz_times, soc_vector.T), axis=1)
                txt_vector_titles = []
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    txt_vector_titles.append('Time' + str(i))
                    self.axImcCharging.plot(x, 100 * np.array(self.SoCVector), label=f'Bus {i}')
                txt_vector_titles.append('SoC')
                txt_matriz_soc_diagram = np.concatenate(([txt_vector_titles], txt_matriz_soc_diagram), axis=0)
                np.savetxt(path_soc_diagram, txt_matriz_soc_diagram, delimiter=",", fmt='% s')
                self.axImcCharging.set_title('State of Charge', fontsize=12, fontweight="bold")
                self.axImcCharging.set_ylabel('%', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 4:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axImcCharging.plot(x, BusWindow.stopVector, label=f'Bus {i}')
                self.axImcCharging.set_title('Stop Vector', fontsize=12, fontweight="bold")
                self.axImcCharging.set_ylabel('', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
            elif plot_type == 5:
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axImcCharging.plot(x, self.chargerVector, label=f'Bus {i}')
                self.axImcCharging.set_title('Section Vector', fontsize=12, fontweight="bold")
                self.axImcCharging.set_ylabel('kW', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")
        elif element_type == 1:
            plot_type = self.__DynamicWindow.VariablescomboBox.currentIndex()
            self.axImcCharging.cla()

            if plot_type == 0:
                i = 0
                for c in self.charger_final_matrix:
                    self.axImcCharging.plot(self.lista_tiempo, c, label=f'S {i + 1}')
                    i += 1
                self.axImcCharging.set_title('Section Vector', fontsize=12, fontweight="bold")
                self.axImcCharging.set_ylabel('kW', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time [h]', fontsize=10, fontweight="bold")

        self.axImcCharging.tick_params(labelsize=10)
        self.axImcCharging.grid()
        self.axImcCharging.legend(frameon=False, loc='best')
        self.figureImcCharging.autofmt_xdate()
        self.canvasImcCharging.draw()


class UiGridWindow(UiDynamicWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(UiGridWindow, self).__init__()
        ruta_ui = str(Path(path_UI, "InterfaceGrid.ui"))
        self.__GridWindow = uic.loadUi(ruta_ui, self)
        self.__GridWindow.ChargingComboBox.setCurrentIndex(0)
        self.__GridWindow.GridSimulationTab.setCurrentIndex(0)
        # Inicialización OpenDSS
        DSSText.Command = 'clear'
        ruta_file_dss = str(Path(path_TestCase, "i37Bus", "ieee37.dss"))
        DSSText.Command = f'Redirect ({ruta_file_dss})'
        # Ruta de guardado de resultados
        self.save_file_dss = str(path_Results)
        DSSText.Command = f'Set datapath=({self.save_file_dss})'
        # Flujo de carga ficticio para generar la lista de nodos
        DSSText.Command = 'CalcVoltageBases'

        # Llamadas a Métodos
        # Botones de Grid Window
        self.__GridWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__GridWindow.actionUser_Manual.triggered.connect(self.clicked_manual)
        self.__GridWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.__GridWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__GridWindow.OpportunityButton.clicked.connect(self.pressed_opportunity_button)
        self.__GridWindow.DynamicButton.clicked.connect(self.pressed_dynamic_button)
        self.__GridWindow.SearchFileButton.clicked.connect(self.__pressed_search_file_button)
        self.__GridWindow.LoadChargersNodesButton.clicked.connect(self.__pressed_load_charger_nodes_button)
        self.__GridWindow.SaveButton.clicked.connect(self.__pressed_save_button)
        self.__GridWindow.NodeLocationButton.clicked.connect(self.__pressed_node_location_button)
        self.__GridWindow.PowerFlowButton.clicked.connect(self.__pressed_power_flow_button)
        self.__GridWindow.SummaryButton.clicked.connect(self.__pressed_summary_button)
        self.__GridWindow.VoltageProfileButton.clicked.connect(self.__pressed_voltage_profile_button)
        self.__GridWindow.VoltagesGraphButton.clicked.connect(self.__pressed_voltages_graph_button)
        self.__GridWindow.CurrentsGraphButton.clicked.connect(self.__pressed_currents_graph_button)
        # Setups Gráficas de Grid Window
        self.__setup_grid_diagram_figures()

    # Métodos
    # Buscar y definir la extensión del archivo .dss
    def __pressed_search_file_button(self):
        file_filter = "dss file (*.dss)"
        dss_route = str(path_TestCase)
        try:
            (filename, extension) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', dss_route,
                                                                          filter=self.tr(file_filter))
            self.file_type = filename.split('.')[1]
            print("File extension:", self.file_type)
            self.__GridWindow.DssFileLine.setText(filename)

            self.file = self.__GridWindow.DssFileLine.text()
            print("File:", self.file)
            try:
                if self.file_type == 'dss':
                    # Inicialización OpenDSS
                    DSSText.Command = 'clear'
                    DSSText.Command = f'Redirect ({self.file})'
                    # Flujo de carga ficticio para generar la lista de nodos
                    DSSText.Command = 'CalcVoltageBases'
                else:
                    raise Exception('File extension not supported')
            except Exception as ex:
                print(ex)
                print('Not a valid dss file')
        except IndexError as ex:
            print("Error:", ex)

    # Cargar cargadores o secciones y nodos
    def __pressed_load_charger_nodes_button(self):
        # Crear una lista de nodos personalizada
        self.AllBusNames = DSSCircuit.AllBusNames
        # Extraer nombre del sistema
        self.system_name = self.file.split('/')[-1].split('.')[0]
        file_name = f'{self.system_name}_EXP_VOLTAGES.CSV'
        DSSText.Command = f'Export voltages {file_name}'
        # Extraer base de las tensiones de cada nodo
        voltages_bases_file = str(Path(path_Results, file_name))
        try:
            voltages_data = read_csv(voltages_bases_file, usecols=("Bus", " BasekV"))
        except Exception as ex:
            print(ex)
            print('Not a valid data vector')
            voltages_data = None
        self.voltages_bases = list(voltages_data[[' BasekV']].iloc[:, -1].values)
        # Obtener una lista de líneas
        self.AllLineNames = []
        line_index = DSSCircuit.Lines.First
        while line_index > 0:
            self.AllLineNames.append(DSSCircuit.Lines.Name)
            line_index = DSSCircuit.Lines.Next

        # Obtener una lista de transformadores
        self.AllTransformerNames = []
        transformer_index = DSSCircuit.Transformers.First
        while transformer_index > 0:
            self.AllTransformerNames.append(DSSCircuit.Transformers.Name)
            transformer_index = DSSCircuit.Transformers.Next

        # Asignar lista de nodos a combo box correspondiente
        self.NodeListComboBox.clear()
        self.NodeListComboBoxVoltages.clear()
        for i in range(0, len(self.AllBusNames), 1):
            if len(self.NodeListComboBox) < len(self.AllBusNames):
                option = self.AllBusNames[i]
                self.NodeListComboBox.addItem(option)
                self.NodeListComboBoxVoltages.addItem(option)
            else:
                break

        # Asignar lista de líneas a combo box correspondiente
        self.LineListComboBox.clear()
        for i in range(0, len(self.AllLineNames), 1):
            if len(self.LineListComboBox) < len(self.AllLineNames):
                line_name = self.AllLineNames[i]
                self.LineListComboBox.addItem(line_name)
            else:
                break

        # Mostrar cuadro de asignación de nodos dependiendo del tipo de recarga
        if self.ChargingComboBox.currentText() == "Opportunity Charging":
            # Limpiar contenido de Layout
            for i in reversed(range(self.__GridWindow.AssignmentLayout.count())):
                self.__GridWindow.AssignmentLayout.itemAt(i).widget().setParent(None)
            # Definir Widgets
            self.group_box_assignment = QtWidgets.QGroupBox("Assignment")
            self.group_box_assignment.setFont(QtGui.QFont("MS Sans Serif", 10, QtGui.QFont.Bold))
            self.group_box_assignment.setStyleSheet("background-color:white;")
            # Layout Interno del Group Box
            self.group_box_layout = QtWidgets.QFormLayout()
            # Llenar QFormLayout
            self.charger_list = []
            self.nodes_combo_box_list = []
            assignment_labels = OpportunityWindow.charger_list
            for i in range(len(assignment_labels)):
                # Guardar nombres de cargadores
                self.charger_list.append(QtWidgets.QLabel(assignment_labels[i]))
                # Agregar un combo box por cada cargador
                self.nodes_combo_box_list.append(QtWidgets.QComboBox())
                # Agregar nodos al combo box
                self.nodes_combo_box_list[i].addItems(self.AllBusNames)
                GridWindow.group_box_layout.addRow(self.charger_list[i], self.nodes_combo_box_list[i])

            # Assignment GroupBox
            GridWindow.group_box_assignment.setLayout(GridWindow.group_box_layout)
            # Assignment Scroll
            self.assignment_scroll_area = QtWidgets.QScrollArea()
            self.assignment_scroll_area.setWidgetResizable(True)
            self.assignment_scroll_area.setWidget(GridWindow.group_box_assignment)
            # Assignment Layout
            self.__GridWindow.AssignmentLayout.addWidget(self.assignment_scroll_area)

        elif self.ChargingComboBox.currentText() == "In Motion Charging":
            # Limpiar contenido de Layout
            for i in reversed(range(self.__GridWindow.AssignmentLayout.count())):
                self.__GridWindow.AssignmentLayout.itemAt(i).widget().setParent(None)
            # Definir Widgets
            self.group_box_assignment = QtWidgets.QGroupBox("Assignment")
            self.group_box_assignment.setFont(QtGui.QFont("MS Sans Serif", 10, QtGui.QFont.Bold))
            self.group_box_assignment.setStyleSheet("background-color:white;")
            # Layout Interno del Group Box
            self.group_box_layout = QtWidgets.QFormLayout()
            # Llenar QFormLayout
            self.charger_list = []
            self.nodes_combo_box_list = []
            assignment_labels = DynamicWindow.section_list
            for i in range(len(assignment_labels)):
                # Guardar nombres de cargadores
                self.charger_list.append(QtWidgets.QLabel(assignment_labels[i]))
                # Agregar un combo box por cada cargador
                self.nodes_combo_box_list.append(QtWidgets.QComboBox())
                # Agregar nodos al combo box
                self.nodes_combo_box_list[i].addItems(self.AllBusNames)
                self.group_box_layout.addRow(self.charger_list[i], self.nodes_combo_box_list[i])

            # Assignment GroupBox
            self.group_box_assignment.setLayout(self.group_box_layout)
            # Assignment Scroll
            self.assignment_scroll_area = QtWidgets.QScrollArea()
            self.assignment_scroll_area.setWidgetResizable(True)
            self.assignment_scroll_area.setWidget(self.group_box_assignment)
            # Assignment Layout
            self.__GridWindow.AssignmentLayout.addWidget(self.assignment_scroll_area)

    # Guardar ubicación en nodos de los cargadores o secciones
    def __pressed_save_button(self):
        self.node_connection = []
        for i in range(len(self.nodes_combo_box_list)):
            self.node_connection.append(self.nodes_combo_box_list[i].currentText())

    # Graficar posición del nodo seleccionado (OpenDSS)
    def __pressed_node_location_button(self):
        node_selected = self.NodeListComboBox.currentText()
        DSSText.Command = f'AddBusMarker Bus=[{node_selected}] code=16 color=Black size=10'
        DSSText.Command = 'plot daisy Power max=2000 n n C1=$00FF0000'
        DSSText.Command = 'clearBusMarkers'

    # Power Flow de OpenDSS
    def __pressed_power_flow_button(self):

        # Caso recarga de oportunidad
        if self.ChargingComboBox.currentText() == "Opportunity Charging":
            # Limpiar circuitos guardados en la memoria
            DSSText.Command = 'clear'
            DSSText.Command = f'Redirect ({self.file})'
            # Ruta de guardado de resultados
            DSSText.Command = f'Set datapath=({self.save_file_dss})'

            # Agregar carga de valor cero y medidores de corriente y tensión para graficar las tensiones en el tiempo
            for i in range(len(self.AllBusNames)):
                self.node = str(self.AllBusNames[i])
                DSSText.Command = 'New Load.{0} phases=3 Conn=Delta Bus={0}.1.2.3 kV=4.8 kW=0 pf=1'.format(self.node)
                DSSText.Command = 'New monitor.{0} element=load.{0} terminal=1 mode=0'.format(self.node)

            # Agregar medidor de corriente y tensión en todas las líneas
            for i in range(len(self.AllLineNames)):
                self.line = self.AllLineNames[i]
                DSSText.Command = 'New monitor.{0} element=line.{0} terminal=1 mode=0'.format(self.line)

            # Crear LoadShape con intervalos de 1 minuto y asignarlo a una carga a conectar
            for i in range(len(self.charger_list)):
                load_shape = [0.0] * 1440
                self.minute_average = []
                condition = int(((len(OpportunityWindow.lista_tiempo) - 1) / 60))
                for j in range(condition):
                    k = 60 * j
                    self.minute_sum = 0
                    for x in range(60):
                        self.minute_sum = self.minute_sum + OpportunityWindow.charger_final_matrix[i][k + x]
                    self.minute_average.append(self.minute_sum / 60)

                # Normalizar el vector de promedio por minuto
                max_power_charger = max(self.minute_average)
                self.minute_average = list(np.array(self.minute_average) / max_power_charger)

                # Ingresar los promedios calculados dentro del LoadShape haciendo que concuerde con las horas de
                # operación de la flota de buses
                for n in range(condition):
                    load_position = int(BusWindow.init_sec / 60 + n)
                    load_shape[load_position] = self.minute_average[n]

                current_load = str(i)
                current_load_shape = str(load_shape)
                current_node = str(self.node_connection[i])
                current_base = str(self.voltages_bases[i])
                DSSText.Command = f'New LoadShape.Shape_{current_load} npts=1440 minterval=1 mult={current_load_shape}'\
                                  + ' Action=Normalize'
                DSSText.Command = f'New Load.LOAD_{current_load} Phases=3 Conn=Delta Bus1={current_node} ' +\
                                  f'kV={current_base}' + f' kW={max_power_charger} PF=1 Daily=Shape_{current_load}'

            # Modo de simulación y comando para correr la simulación
            DSSText.Command = f'New Energymeter.m1 element=Transformer.{self.AllTransformerNames[0]} terminal=1'
            DSSText.Command = 'set mode=daily stepsize=1m number=1440'
            DSSText.Command = 'Solve'

        # Caso recarga dinámica
        elif self.ChargingComboBox.currentText() == "In Motion Charging":
            DSSText.Command = 'clear'
            DSSText.Command = f'Redirect ({self.file})'
            # Ruta de guardado de resultados
            DSSText.Command = f'Set datapath=({self.save_file_dss})'

            # Agregar carga de valor cero y medidores de corriente y tensión para graficar las tensiones en el tiempo
            for i in range(len(self.AllBusNames)):
                self.node = str(self.AllBusNames[i])
                DSSText.Command = 'New Load.{0} phases=3 Conn=Delta Bus={0}.1.2.3 kV=4.8 kW=0 pf=1'.format(self.node)
                DSSText.Command = 'New monitor.{0} element=load.{0} terminal=1 mode=0'.format(self.node)

            # Agregar medidor de corriente y tensión en todas las líneas
            for i in range(len(self.AllLineNames)):
                self.line = self.AllLineNames[i]
                DSSText.Command = 'New monitor.{0} element=line.{0} terminal=1 mode=0'.format(self.line)

            # Crear LoadShape con intervalos de 1 minuto y asignarlo a una carga a conectar
            for i in range(len(self.charger_list)):
                load_shape = [0.0] * 1440
                self.minute_average = []
                condition = int(((len(DynamicWindow.lista_tiempo) - 1) / 60))
                for j in range(condition):
                    k = 60 * j
                    self.minute_sum = 0
                    for x in range(60):
                        self.minute_sum = self.minute_sum + DynamicWindow.charger_final_matrix[i][k + x]
                    self.minute_average.append(self.minute_sum / 60)

                # Normalizar el vector de promedio por minuto
                max_power_charger = max(self.minute_average)
                self.minute_average = list(np.array(self.minute_average) / max_power_charger)

                # for m in range(1440):
                # load_shape.append(0.0)

                # Ingresar los promedios calculados dentro del LoadShape haciendo que concuerde con las horas de
                # operación de la flota de buses
                for n in range(condition):
                    load_position = int(BusWindow.init_sec / 60 + n)
                    load_shape[load_position] = self.minute_average[n]

                current_load = str(i)
                current_load_shape = str(load_shape)
                current_node = str(self.node_connection[i])
                current_base = str(self.voltages_bases[i])
                DSSText.Command = f'New LoadShape.Shape_{current_load} npts=1440 minterval=1 mult={current_load_shape}'\
                                  + ' Action=Normalize'
                DSSText.Command = f'New Load.LOAD_{current_load} Phases=3 Conn=Delta Bus1={current_node} ' + \
                                  f'kV={current_base}' + f' kW={max_power_charger} PF=1 Daily=Shape_{current_load}'

            # Modo de simulación y comando para correr la simulación
            DSSText.Command = f'New Energymeter.m1 element=Transformer.{self.AllTransformerNames[0]} terminal=1'
            DSSText.Command = 'set mode=daily stepsize=1m number=1440'
            DSSText.Command = 'Solve'

    # Summary de OpenDSS
    def __pressed_summary_button(self):
        DSSText.Command = 'Summary'
        self.results = DSSText.Result
        # Limpiar contenido de Layout
        for i in reversed(range(self.__GridWindow.SummaryLayout.count())):
            self.__GridWindow.SummaryLayout.itemAt(i).widget().setParent(None)
        self.group_box_summary_layout = QtWidgets.QLabel()
        self.group_box_summary_layout.setText(self.results)
        # Assignment Scroll
        self.summary_scroll_area = QtWidgets.QScrollArea()
        self.summary_scroll_area.setWidgetResizable(True)
        self.summary_scroll_area.setWidget(self.group_box_summary_layout)
        self.summary_scroll_area.setFont(QtGui.QFont("MS Sans Serif", 10, QtGui.QFont.Bold))
        self.summary_scroll_area.setStyleSheet("background-color:white;")
        # Assignment Layout
        self.__GridWindow.SummaryLayout.addWidget(self.summary_scroll_area)

    # Perfiles de tensión de OpenDSS
    @staticmethod
    def __pressed_voltage_profile_button():
        DSSText.Command = 'Plot Profile Phases=All'

    # Graficar tensiones por fase del nodo seleccionado
    def __pressed_voltages_graph_button(self):
        # Llamar función para evitar correr numerosas veces la simulación
        self.__pressed_power_flow_button()

        # Plotear canales del 1 al 5 del monitor del nodo seleccionado
        selected_node = str(self.NodeListComboBoxVoltages.currentText())
        node_index = self.NodeListComboBoxVoltages.currentIndex()
        file_name = f'{self.system_name}_Mon_{selected_node}_1.csv'
        DSSText.Command = f'Export monitor object={selected_node}'

        voltages_file = str(Path(path_Results, file_name))
        try:
            voltages_data = read_csv(voltages_file, usecols=(" V1", " VAngle1", " V2", " VAngle2", " V3", " VAngle3"))
        except Exception as ex:
            print(ex)
            print('Not a valid data vector')
            voltages_data = None

        # Tensiones y ángulos de cada fase
        v1 = list(voltages_data[[' V1']].iloc[:, -1].values / (self.voltages_bases[node_index] / np.sqrt(3) * 1000))
        v1_angle = list(voltages_data[[' VAngle1']].iloc[:, -1].values)
        v2 = list(voltages_data[[' V2']].iloc[:, -1].values / (self.voltages_bases[node_index] / np.sqrt(3) * 1000))
        v2_angle = list(voltages_data[[' VAngle2']].iloc[:, -1].values)
        v3 = list(voltages_data[[' V3']].iloc[:, -1].values / (self.voltages_bases[node_index] / np.sqrt(3) * 1000))
        v3_angle = list(voltages_data[[' VAngle3']].iloc[:, -1].values)

        # Crear gráfico de tensión
        self.axVoltages.cla()
        self.axVoltages.plot(range(1440), v1, label='V1')
        self.axVoltages.plot(range(1440), v2, label='V2')
        self.axVoltages.plot(range(1440), v3, label='V3')
        self.axVoltages.set_ylabel('V [pu]', fontsize=10, fontweight="bold")
        self.axVoltages.set_xlabel('Time [m]', fontsize=10, fontweight="bold")
        self.axVoltages.tick_params(labelsize=10)
        self.axVoltages.grid()
        self.axVoltages.legend(frameon=False, loc='best')
        self.canvasVoltages.draw()

        # Crear gráfico de ángulos
        self.axVoltagesAngle.cla()
        self.axVoltagesAngle.plot(range(1440), v1_angle, label='V1')
        self.axVoltagesAngle.plot(range(1440), v2_angle, label='V2')
        self.axVoltagesAngle.plot(range(1440), v3_angle, label='V3')
        self.axVoltagesAngle.set_ylabel('Angle [deg]', fontsize=10, fontweight="bold")
        self.axVoltagesAngle.set_xlabel('Time [m]', fontsize=10, fontweight="bold")
        self.axVoltagesAngle.tick_params(labelsize=10)
        self.axVoltagesAngle.grid()
        self.axVoltagesAngle.legend(frameon=False, loc='best')
        self.canvasVoltagesAngle.draw()

    # Graficar corrientes por fase de la línea seleccionado
    def __pressed_currents_graph_button(self):
        # Llamar función para evitar correr numerosas veces la simulación
        self.__pressed_power_flow_button()

        # Plotear canales del 7 al 11 (corrientes) de línea seleccionada
        selected_line = str(self.LineListComboBox.currentText())
        file_name = f'{self.system_name}_Mon_{selected_line}_1.csv'
        DSSText.Command = f'Export monitor object={selected_line}'
        currents_file = str(Path(path_Results, file_name))
        try:
            currents_data = read_csv(currents_file, usecols=(" I1", " IAngle1", " I2", " IAngle2", " I3", " IAngle3"))
        except Exception as ex:
            print(ex)
            print('Not a valid data vector')
            currents_data = None

        # Corrientes y ángulos de cada fase
        i1 = list(currents_data[[' I1']].iloc[:, -1].values)
        i1_angle = list(currents_data[[' IAngle1']].iloc[:, -1].values)
        i2 = list(currents_data[[' I2']].iloc[:, -1].values)
        i2_angle = list(currents_data[[' IAngle2']].iloc[:, -1].values)
        i3 = list(currents_data[[' I3']].iloc[:, -1].values)
        i3_angle = list(currents_data[[' IAngle3']].iloc[:, -1].values)

        # Crear gráfico de tensión
        self.axCurrents.cla()
        self.axCurrents.plot(range(1440), i1, label='I1')
        self.axCurrents.plot(range(1440), i2, label='I2')
        self.axCurrents.plot(range(1440), i3, label='I3')
        self.axCurrents.set_ylabel('I [A]', fontsize=10, fontweight="bold")
        self.axCurrents.set_xlabel('Time [m]', fontsize=10, fontweight="bold")
        self.axCurrents.tick_params(labelsize=10)
        self.axCurrents.grid()
        self.axCurrents.legend(frameon=False, loc='best')
        self.canvasCurrents.draw()

        # Crear gráfico de ángulos
        self.axCurrentsAngle.cla()
        self.axCurrentsAngle.plot(range(1440), i1_angle, label='I1')
        self.axCurrentsAngle.plot(range(1440), i2_angle, label='I2')
        self.axCurrentsAngle.plot(range(1440), i3_angle, label='I3')
        self.axCurrentsAngle.set_ylabel('Angle [deg]', fontsize=10, fontweight="bold")
        self.axCurrentsAngle.set_xlabel('Time [m]', fontsize=10, fontweight="bold")
        self.axCurrentsAngle.tick_params(labelsize=10)
        self.axCurrentsAngle.grid()
        self.axCurrentsAngle.legend(frameon=False, loc='best')
        self.canvasCurrentsAngle.draw()

    # Definir Plots (Grid Window)
    def __setup_grid_diagram_figures(self):
        # Voltages magnitude figures
        self.figureVoltages = Figure(tight_layout=True)
        self.canvasVoltages = FigureCanvas(self.figureVoltages)
        self.toolbarVoltages = NavigationToolbar(self.canvasVoltages, self)
        self.layoutVoltages = QtWidgets.QVBoxLayout(self.__GridWindow.VoltageCurveWidget)
        self.layoutVoltages.addWidget(self.toolbarVoltages)
        self.layoutVoltages.addWidget(self.canvasVoltages)  #
        self.axVoltages = self.figureVoltages.add_subplot(111)

        # Voltages angle figures
        self.figureVoltagesAngle = Figure(tight_layout=True)
        self.canvasVoltagesAngle = FigureCanvas(self.figureVoltagesAngle)
        self.toolbarVoltagesAngle = NavigationToolbar(self.canvasVoltagesAngle, self)
        self.layoutVoltagesAngle = QtWidgets.QVBoxLayout(self.__GridWindow.VoltageAngleCurveWidget)
        self.layoutVoltagesAngle.addWidget(self.toolbarVoltagesAngle)
        self.layoutVoltagesAngle.addWidget(self.canvasVoltagesAngle)  #
        self.axVoltagesAngle = self.figureVoltagesAngle.add_subplot(111)

        # Currents magnitude figures
        self.figureCurrents = Figure(tight_layout=True)
        self.canvasCurrents = FigureCanvas(self.figureCurrents)
        self.toolbarCurrents = NavigationToolbar(self.canvasCurrents, self)
        self.layoutCurrents = QtWidgets.QVBoxLayout(self.__GridWindow.CurrentCurveWidget)
        self.layoutCurrents.addWidget(self.toolbarCurrents)
        self.layoutCurrents.addWidget(self.canvasCurrents)  #
        self.axCurrents = self.figureCurrents.add_subplot(111)

        # Currents angle figures
        self.figureCurrentsAngle = Figure(tight_layout=True)
        self.canvasCurrentsAngle = FigureCanvas(self.figureCurrentsAngle)
        self.toolbarCurrentsAngle = NavigationToolbar(self.canvasCurrentsAngle, self)
        self.layoutCurrentsAngle = QtWidgets.QVBoxLayout(self.__GridWindow.CurrentAngleCurveWidget)
        self.layoutCurrentsAngle.addWidget(self.toolbarCurrentsAngle)
        self.layoutCurrentsAngle.addWidget(self.canvasCurrentsAngle)  #
        self.axCurrentsAngle = self.figureCurrentsAngle.add_subplot(111)


# Inicio Programa
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    # Definir Ventanas
    RouteWindow = UiRouteWindow()
    BusWindow = UiBusWindow()
    OpportunityWindow = UiOpportunityWindow()
    DynamicWindow = UiDynamicWindow()
    GridWindow = UiGridWindow()

    # Añadir Ventanas
    widget.addWidget(RouteWindow)
    widget.addWidget(BusWindow)
    widget.addWidget(OpportunityWindow)
    widget.addWidget(DynamicWindow)
    widget.addWidget(GridWindow)

    # Setup de widgets
    widget.setFixedSize(964, 677)
    icon = QtGui.QIcon()
    ruta_icon = str(Path(path_Imgs, "iconBus.png"))
    icon.addPixmap(QtGui.QPixmap(ruta_icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    widget.setWindowIcon(icon)
    _translate = QtCore.QCoreApplication.translate
    widget.setWindowTitle(_translate("MainWindow", "Electric Bus Charging Analyzer"))
    widget.setStyleSheet("background-color: #bfbfbf;")

    # Mostrar Aplicación
    widget.show()
    sys.exit(app.exec_())


#%%
