import sys

import matplotlib
matplotlib.use('qtagg')

from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget)

from ui_py.ui_main_window import Ui_MainWindow

from battery import BatteriesManager
from testsPage import TestsPage
from batteriesPage import BatteriesPage
from curvesPage import CurvesPage
import workers



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):        
        super().__init__()
        self.setupUi(self)
         
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.batteriesManager = BatteriesManager()
        
        self.batteriesPage = BatteriesPage(self, self.batteriesManager)
        self.curvesPage = CurvesPage(self, self.batteriesManager)
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
        self.curvesPage.updatePage()
        self.stacked_widget.setCurrentIndex(1)
        
        
    def saveAllToBPA(self):
        thread = workers.SaveBPAWorker(self.batteriesManager.batteriesList())
        workers.saveDialog(self, thread)
    
    
    def loadAllFromBPA(self):
        self.stacked_widget.setCurrentIndex(0)
        thread = workers.LoadBPAWorker(self.batteriesManager)
        workers.loadDialog(self, thread, self.batteriesPage.fillTable)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    if len(sys.argv) > 1:
        thread = workers.LoadBPAWorker(window.batteriesManager)
        workers.loadDialog(window, thread, window.batteriesPage.fillTable, sys.argv[1])
        
    sys.exit(app.exec())