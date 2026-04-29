import sys

import matplotlib
matplotlib.use('qtagg')

from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget)

from ui_py.ui_main_window import Ui_MainWindow

from testsPage import TestsPage
from batteriesPage import BatteriesPage
from curvesPage import CurvesPage
from bpaLoader import saveDialog, loadDialog



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):        
        super().__init__()
        self.setupUi(self)
         
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.batteriesPage = BatteriesPage(self)
        self.curvesPage = CurvesPage(self)
        self.testsPage = TestsPage(self)
            
        self.stacked_widget.addWidget(self.batteriesPage)
        self.stacked_widget.addWidget(self.curvesPage)
        self.stacked_widget.addWidget(self.testsPage)
        
        self.batteriesAction.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.curvesAction.triggered.connect(self.curvesPageOpen)
        
        self.saveAllAction.triggered.connect(self.saveAllToBPA)
        self.loadAllAction.triggered.connect(self.loadAllFromBPA)
        
        self.testsPage.battariesPage_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        self.batteriesPage.batterySelected.connect(lambda battery: self.testsPageOpen(battery))
        
        
    def testsPageOpen(self, battery):
        self.testsPage.setBattery(battery)
        self.stacked_widget.setCurrentIndex(2)
        
        
    def curvesPageOpen(self):
        self.curvesPage.updatePage(self.batteriesPage.batteries)
        self.stacked_widget.setCurrentIndex(1)
        
        
    def saveAllToBPA(self):
        saveDialog(self, self.batteriesPage.batteries.BPAdata())
    
    
    def loadAllFromBPA(self):
        self.stacked_widget.setCurrentIndex(0)
        loadDialog(self, self.batteriesPage.batteries)
        self.batteriesPage.fillTable()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())