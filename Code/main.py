# Importar Paquetes
from PyQt5 import QtCore, QtGui, QtWidgets, uic

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


# Clases
class UiAboutWindow(QtWidgets.QDialog):
    # Constructor
    def __init__(self):
        super(UiAboutWindow, self).__init__()
        self.__AboutWindow = uic.loadUi('../UI/About.ui', self)
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
        self.__RouteWindow = uic.loadUi('../UI/InterfaceRoute.ui', self)
        self.AboutTab = UiAboutWindow()
        self.routeData = feather.read_feather('../Route/Template/ROUTE-Template.feather')

        # Llamadas a Métodos
        # Botones de Route Window
        self.__RouteWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__RouteWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__RouteWindow.OpportunityButton.clicked.connect(self.pressed_opportunity_button)
        self.__RouteWindow.DynamicButton.clicked.connect(self.pressed_dynamic_button)
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

    # Buscar y definir la extensión del archivo .feather or .csv
    def __pressed_search_file_button(self):
        file_filter = "feather file (*.feather);;csv file (*.csv)"
        (filename, extension) = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '../Route/',
                                                                      filter=self.tr(file_filter))
        self.file_type = filename.split('.')[1]
        print("File extension:", self.file_type)
        self.__RouteWindow.RouteFileLine.setText(filename)

    # Leer y cargar el archivo .CSV
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

        print("Route data:")
        print(self.routeData)
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
        self.__BusWindow = uic.loadUi('../UI/InterfaceBus.ui', self)
        self.__BusWindow.BusParametersTab.setCurrentIndex(0)
        self.__BusWindow.PeakTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.StartEndTimesToolBox.setCurrentIndex(0)
        self.__BusWindow.PositionSpeedtabWidget.setCurrentIndex(0)

        # Llamadas a Métodos
        # Botones de Bus Window
        self.__BusWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__BusWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.__BusWindow.OpportunityButton.clicked.connect(self.pressed_opportunity_button)
        self.__BusWindow.DynamicButton.clicked.connect(self.pressed_dynamic_button)
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
        print("Stop Delay: ", stop_delay)
        time_in_terminal = float(fleet_table.item(5, 0).text())
        print("Time in Terminal: ", time_in_terminal)
        t_ini_fleet_qt = self.__BusWindow.STFtimeEdit.time()
        t_ini_fleet = t_ini_fleet_qt.hour() * 3600 + t_ini_fleet_qt.minute() * 60 + t_ini_fleet_qt.second()
        print("Time ini fleet: ", t_ini_fleet)
        t_end_fleet_qt = self.__BusWindow.ETFtimeEdit.time()
        t_end_fleet = t_end_fleet_qt.hour() * 3600 + t_end_fleet_qt.minute() * 60 + t_end_fleet_qt.second()
        print("Time end fleet: ", t_end_fleet)
        t_ini_pico1_qt = self.__BusWindow.STPtimeEdit.time()
        t_ini_pico1 = t_ini_pico1_qt.hour() * 3600 + t_ini_pico1_qt.minute() * 60 + t_ini_pico1_qt.second()
        print("Time ini pico 1: ", t_ini_pico1)
        t_end_pico1_qt = self.__BusWindow.ETPtimeEdit.time()
        t_end_pico1 = t_end_pico1_qt.hour() * 3600 + t_end_pico1_qt.minute() * 60 + t_end_pico1_qt.second()
        print("Time end pico 1: ", t_end_pico1)

        t_ini_pico2_qt = self.__BusWindow.STMPtimeEdit.time()
        t_ini_pico2 = t_ini_pico2_qt.hour() * 3600 + t_ini_pico2_qt.minute() * 60 + t_ini_pico2_qt.second()
        print("Time ini pico 2: ", t_ini_pico2)
        t_end_pico2_qt = self.__BusWindow.EMPtimeEdit.time()
        t_end_pico2 = t_end_pico2_qt.hour() * 3600 + t_end_pico2_qt.minute() * 60 + t_end_pico1_qt.second()
        print("Time end pico 2: ", t_end_pico2)
        num_buses = int(fleet_table.item(6, 0).text())
        print("Number of buses: ", num_buses)
        dispatch_frequency = int(fleet_table.item(7, 0).text())
        print("Dispatch frequency: ", dispatch_frequency)
        num_buses_peak = int(fleet_table.item(0, 0).text())
        print("Number of buses peak: ", num_buses_peak)
        dispatch_frequency_peak = int(fleet_table.item(3, 0).text())
        print("Dispatch frequency peak: ", dispatch_frequency_peak)

        # Simulation parameters
        delta_t = 0.2
        max_time = t_end_fleet - (num_buses - 1) * dispatch_frequency
        # maxTime2 = t2EndFleet - (num_buses_peak - 1) * dispatch_frequency_peak

        # Bus parameters
        accel_bus = self.accelCurve
        print("Acceleration curve: ")
        print(accel_bus)
        decel_bus = self.decelCurve
        print("Deceleration curve: ")
        print(decel_bus)
        dist_brake = calculate_braking_distance(decel_bus, delta_t)
        print("Distance to brake: ", dist_brake)
        max_speed_bus = accel_bus[-1]
        print("Max speed: ", max_speed_bus)

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
        time_zone_colombia = 3600 * 5

        for n in range(0, len(self.timeVector)):
            self.timeVectorDT.append(datetime.datetime.fromtimestamp(self.timeVector[n] + time_zone_colombia))

        self.arrayTime = []

        for y in range(num_buses):
            time_arr = []
            time_ = []
            frec = 0
            print("Número de bus:" + str(y))
            for idx, x in enumerate(self.timeVector):
                # print("self.distVector: "+str(self.distVector[idx]),("self.speedVector: "+str(self.speedVector[idx])))
                if t_ini_pico1 < x <= t_end_pico1 or t_ini_pico2 < x < t_end_pico2:
                    if self.distVector[idx] == 0 and self.stateVector[idx] == 2:
                        frec = dispatch_frequency
                else:
                    if self.distVector[idx] == 0:
                        frec = dispatch_frequency
                time_ap = datetime.datetime.fromtimestamp(x + time_zone_colombia) + datetime.timedelta(seconds=frec * y)
                time_arr.append(time_ap)
                time_.append(time_arr[idx].strftime("%H:%M:%S"))
                # print(time_[idx])
            self.arrayTime.append(time_arr)
            print(np.shape(self.arrayTime))

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
        print("Distance vector:")
        print(self.distVector)
        print('Speed vector:')
        print(self.speedVector)
        i = 0
        for x in self.arrayTime:
            i += 1
            self.axOPSpeed.plot(x, 3.6 * self.speedVector, label=f'Bus {i}')
            self.axOPPosition.plot(x, 0.001 * self.distVector, label=f'Bus {i}')

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
        self.__OpportunityWindow = uic.loadUi('../UI/InterfaceOpportunity.ui', self)
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
        self.__OpportunityWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.__OpportunityWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__OpportunityWindow.DynamicButton.clicked.connect(self.pressed_dynamic_button)
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
        print("Charger Sections: ")
        print(self.charger_sections)
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
        print("Charger Sections Selected: ")
        print(self.section_select)
        print("Charger List: ")
        print(self.charger_list)
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
            print('dist_route_np: ')
            print(dist_route_np)

            for N in range(0, len(dist_vector_f) - 1):
                # point1=dist_vector[n]
                point2 = dist_vector_f[N + 1]
                index = np.where(point2 >= dist_route_np)
                k = index[0][-1]
                sin_theta_tot = sin_theta_vector_route[k]
                sin_theta_vector_f.append(sin_theta_tot)

            sin_theta_vector_f.append(sin_theta_vector_f[-1])

            print('len sin_theta_vector:')
            print(len(sin_theta_vector_route))
            return sin_theta_vector_f

        # Parameters
        # Simulation parameters
        delta_t = 0.2

        # Bus parameters
        bus_table = BusWindow.BusParametersTable
        fric = float(bus_table.item(0, 0).text())
        print('fric: ', fric)
        mass = float(bus_table.item(1, 0).text())
        print('mass: ', mass)
        grav = float(bus_table.item(2, 0).text())
        print('grav: ', grav)
        rho = float(bus_table.item(3, 0).text())
        print('rho: ', rho)
        alpha = float(bus_table.item(4, 0).text())
        print('alpha: ', alpha)
        area = float(bus_table.item(5, 0).text())
        print('area: ', area)
        p_aux = 1000 * float(bus_table.item(6, 0).text())
        print('p_aux: ', p_aux)
        n_out = 0.01 * float(bus_table.item(7, 0).text())
        print('n_out: ', n_out)
        n_in = 0.01 * float(bus_table.item(8, 0).text())
        print('n_in: ', n_in)

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
        print('Chargers Stops Vector:')
        print(cl)

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
        print('time vector:')
        print(time_vector)
        print('t_ini_fleet:', t_ini_fleet)
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
        charger_matrix = [[] for i in range(len(cl))]

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
                if charger_num == index_stop:
                    charger_matrix[charger_num].append(ch_onoff * cp)
                else:
                    charger_matrix[charger_num].append(0)

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
        charger_final_matrix = [[] for i in range(num_chargers)]
        for t in lista_tiempo:
            sum_c = [0 for i in range(num_chargers)]
            for c in range(num_chargers):
                for vect_t in BusWindow.arrayTime:
                    try:
                        indice = vect_t.index(t)
                        sum_c[c] += charger_matrix[c][indice]
                    except Exception as ex:
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
                self.axOppCharging.set_ylabel('Energy (kWh)', fontsize=10, fontweight="bold")
                self.axOppCharging.set_xlabel('Time (h)', fontsize=10, fontweight="bold")
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
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axOppCharging.plot(x, 100 * np.array(self.SoCVector), label=f'Bus {i}')
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
        self.__DynamicWindow = uic.loadUi('../UI/InterfaceDynamic.ui', self)
        self.__DynamicWindow.SimulationDynamicTab.setCurrentIndex(0)
        self.__DynamicWindow.ElementscomboBox.setCurrentIndex(0)
        self.__DynamicWindow.VariablescomboBox.setCurrentIndex(0)

        # Llamadas a Métodos
        # Botones de Opportunity Window
        self.__DynamicWindow.actionAbout.triggered.connect(self.clicked_about)
        self.__DynamicWindow.RouteButton.clicked.connect(self.pressed_route_button)
        self.__DynamicWindow.BusButton.clicked.connect(self.pressed_bus_button)
        self.__DynamicWindow.OpportunityButton.clicked.connect(self.pressed_opportunity_button)
        self.__DynamicWindow.RefreshSectionsButton.clicked.connect(self.__pressed_refresh_sections_button)
        self.__DynamicWindow.SaveSectionsButton.clicked.connect(self.__pressed_save_sections_button)
        self.__DynamicWindow.DynamicLoadSimButton.clicked.connect(self.__pressed_load_sim_imc_button)
        self.__DynamicWindow.DynamicGraphButton.clicked.connect(self.__pressed_graph_imc_button)
        self.__DynamicWindow.ElementscomboBox.currentTextChanged.connect(self.__selected_elements)
        # Setups Gráficas de Opportunity Window
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
        print("Charger Sections: ")
        print(self.charger_sections)
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
        print("Active Stops:")
        print(self.cl_aux)
        for i in range(len(stop_list)-1):
            if stop_list[i] == stop_list[i+1]:
                new_stop_list.remove(stop_list[i])
        self.section_select = []
        count = 1
        for i in range(0, len(new_stop_list)-1, 2):
            self.section_select.append(f"{new_stop_list[i]}-{new_stop_list[i+1]}")
            self.section_list.append(f"S{count}")
            count += 1
        num_sections = len(self.section_list)
        print("Charger Sections Selected: ")
        print(self.section_select)
        self.stops_for_section = [[] for i in range(num_sections)]
        for section in self.section_select:
            inicio_section = section.split('-')[0]
            fin_section = section.split('-')[1]
            for i in range(self.cl_aux.index(inicio_section), self.cl_aux.index(fin_section)+1):
                self.stops_for_section[self.section_select.index(section)].append(self.cl_aux[i])
        print("Stops for Section: ")
        print(self.stops_for_section)
        self.cl_list = [x.split('-') for x in self.section_select]
        print("Charger Sections: ")
        print(self.section_list)
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
            print('dist_route_np: ')
            print(dist_route_np)

            for N in range(0, len(dist_vector_f) - 1):
                # point1=dist_vector[n]
                point2 = dist_vector_f[N + 1]
                index = np.where(point2 >= dist_route_np)
                k = index[0][-1]
                sin_theta_tot = sin_theta_vector_route[k]
                sin_theta_vector_f.append(sin_theta_tot)

            sin_theta_vector_f.append(sin_theta_vector_f[-1])

            print('len sin_theta_vector:')
            print(len(sin_theta_vector_route))
            return sin_theta_vector_f

        # Parameters
        # Simulation parameters
        delta_t = 0.2

        # Bus parameters
        bus_table = BusWindow.BusParametersTable
        fric = float(bus_table.item(0, 0).text())
        print('fric: ', fric)
        mass = float(bus_table.item(1, 0).text())
        print('mass: ', mass)
        grav = float(bus_table.item(2, 0).text())
        print('grav: ', grav)
        rho = float(bus_table.item(3, 0).text())
        print('rho: ', rho)
        alpha = float(bus_table.item(4, 0).text())
        print('alpha: ', alpha)
        area = float(bus_table.item(5, 0).text())
        print('area: ', area)
        p_aux = 1000 * float(bus_table.item(6, 0).text())
        print('p_aux: ', p_aux)
        n_out = 0.01 * float(bus_table.item(7, 0).text())
        print('n_out: ', n_out)
        n_in = 0.01 * float(bus_table.item(8, 0).text())
        print('n_in: ', n_in)

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
        print('Chargers Stops Vector:')
        print(cl)

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
        print('time vector:')
        print(time_vector)
        print('t_ini_fleet:', t_ini_fleet)
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
        charger_matrix = [[] for i in range(len(cl))]
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
                if (label_vector[n] in self.cl_aux) or (active_section == 1):
                    for i in range(len(self.stops_for_section)):
                        if label_vector[n] in self.stops_for_section[i]:
                            section_num = i
                            break
                    if label_vector[n] == self.cl_list[section_num][0]:
                        active_section = 1
                    elif label_vector[n] == self.cl_list[section_num][1]:
                        active_section = 0
                    index_stop = section_num
                    ch_onoff = 1
                else:
                    index_stop = None
                    ch_onoff = 0
            else:
                index_stop = None
                ch_onoff = 0
            if power_vector[n] >= 0:
                charger_vector.append(ch_onoff * (cp + power_vector[n]))
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
        charger_final_matrix = [[] for i in range(num_chargers)]
        for t in lista_tiempo:
            sum_c = [0 for i in range(num_chargers)]
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
                self.axImcCharging.set_ylabel('Energy (kWh)', fontsize=10, fontweight="bold")
                self.axImcCharging.set_xlabel('Time (h)', fontsize=10, fontweight="bold")
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
                i = 0
                for x in BusWindow.arrayTime:
                    i += 1
                    self.axImcCharging.plot(x, 100 * np.array(self.SoCVector), label=f'Bus {i}')
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

    # Añadir Ventanas
    widget.addWidget(RouteWindow)
    widget.addWidget(BusWindow)
    widget.addWidget(OpportunityWindow)
    widget.addWidget(DynamicWindow)

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

#%%
