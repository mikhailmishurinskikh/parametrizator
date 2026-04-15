from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QTreeWidget, QHeaderView,
                               QAbstractItemView, QTreeWidgetItem,
                               QTreeWidgetItemIterator)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from ui_py.ui_curves import Ui_CurvesPage



class CurvesPage(QWidget, Ui_CurvesPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        
        self.curves = None
        
        self.list = CurvesList(self)
        self.listLayout.addWidget(self.list)
        self.canvas = CurvesCanvas(self)
        self.graphLayout.addWidget(self.canvas)
        
        self.plot_button.clicked.connect(self.plot)
        
        
    def update(self, batteries):
        self.curves = batteries.curves()
        self.list.update(self.curves)
        self.canvas.figure.clf()
        
        
    def plot(self):
        xlabel = self.oX_comboBox.currentText()
        ylabel = self.oY_comboBox.currentText()
        self.canvas.setLabels(xlabel, ylabel)
        
        selected = self.list.getSelected()
        
        if not(selected):
            self.canvas.finishPlot(empty=True)
            return

        for ids in selected:
            battery_name = self.curves[ids["batteryId"]]["battery"].name
            test = self.curves[ids["batteryId"]]["tests"][ids["testId"]]
            self.canvas.plot(test, battery_name)
        
        self.canvas.finishPlot()
        
        
        
class CurvesList(QTreeWidget):
    class Column:
        header = ["Данные испытаний", "Ёмкость", "Тип кривой", "Выбрано"]
        NAME = 0
        Q = 1
        TYPE = 2
        CHECK = 3
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.initTable()
        
        
    def initTable(self):
        self.setColumnCount(len(self.Column.header))
        self.setHeaderLabels(self.Column.header)
        for i in range(self.columnCount()):
            self.header().setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        
    def update(self, curves):
        for batteryId, batteryData in curves.items():
            batteryItem = QTreeWidgetItem(self)
            batteryItem.setText(0, batteryData["battery"].name)
            
            for testId, test in batteryData["tests"].items():
                testItem = QTreeWidgetItem(batteryItem)
                testItem.setText(self.Column.NAME, test.name)
                testItem.setText(self.Column.Q, f"{test.df["Q,Ah"].abs().max():.2f}")
                testItem.setText(self.Column.TYPE, test.testType)
                
                testItem.setFlags(testItem.flags() | Qt.ItemIsUserCheckable)
                testItem.setCheckState(self.Column.CHECK, Qt.Unchecked)
                
                testItem.setData(self.Column.CHECK, Qt.UserRole, {
                    "testId" : testId,
                    "batteryId" : batteryId
                })
                
                
    def getSelected(self):
        selected = []
        
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()

            ids = item.data(self.Column.CHECK, Qt.UserRole)
            if ids is not None:
                if item.checkState(self.Column.CHECK) == Qt.Checked:
                    selected.append(ids)
            
            iterator += 1
            
        return selected
      
        
        
class CurvesCanvas(FigureCanvas):
    PLOT_LABELS = {
        "Q" : "Емкость батареи, Ач",
        "Q/m" : "Емкость батареи на 1 кг, Ач/кг",
        "V общее" : "Напряжение батареи, В",
        "V на аккум." : "Напряжение на один аккумулятор, В"
    }
    
    def __init__(self, parent):
        super().__init__(plt.Figure())
        self.setParent(parent)
        
        self.xlabel = "Q"
        self.ylabel = "V общее"
        self.axs = None
       
        
    def setLabels(self, xlabel, ylabel):
        self.figure.clf()

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.ax = self.figure.subplots(1)
        self.ax.set_xlabel(self.PLOT_LABELS[xlabel])
        self.ax.set_ylabel(self.PLOT_LABELS[ylabel])
        
    
    def plot(self, test, battery_name):
        self.ax.plot(test.df["Q,Ah"], test.df["U,V"],
                     label=f"Батарея {battery_name}\n"
                     f"{test.name}")
       
        
    def finishPlot(self, empty=False):
        if not empty:
            self.ax.legend()
            
        self.figure.set_tight_layout(True)
        self.draw_idle()