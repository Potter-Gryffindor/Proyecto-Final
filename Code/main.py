# Importar Ventanas
import InterfaceRoute  
import About 

#Importar Paquetes
from PyQt5 import QtCore, QtGui, QtWidgets


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    RouteWindow = QtWidgets.QMainWindow()
    AboutWindow = QtWidgets.QDialog()
    widget = QtWidgets.QStackedWidget()
    

    # Definir Ventanas
    RouteTab = InterfaceRoute.Ui_MainWindow()
    RouteTab.setupUi(RouteWindow)
    
    AboutTab = About.Ui_AboutWindow()
    AboutTab.setupUi(AboutWindow)
    

    # Añadir Ventanas
    widget.addWidget(RouteWindow)
    widget.addWidget(AboutWindow)

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