import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QTreeWidget, QHeaderView,
                               QAbstractItemView, QTreeWidgetItem,
                               QTreeWidgetItemIterator, QFileDialog,
                               QMessageBox)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

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
        self.save_button.clicked.connect(self.canvas.save)
        
        
    def updatePage(self, batteries):
        self.curves = batteries.curves()
        self.list.updateList(self.curves)
        self.canvas.clearAll(draw=True)
        
        
    def plot(self):
        xlabel = self.oX_comboBox.currentText()
        ylabel = self.oY_comboBox.currentText()
        
        selected = self.list.getSelected()
        
        if not selected:
            self.canvas.finishPlot(empty=True)
            return
        
        self.canvas.setLabels(xlabel, ylabel)
        
        for ids in selected:
            battery = self.curves[ids["batteryId"]]["battery"]
            test = self.curves[ids["batteryId"]]["tests"][ids["testId"]]
            self.canvas.plot(test, battery)
        
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
        
        
    def updateList(self, curves):
        self.clear()
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
        super().__init__(Figure(constrained_layout=True))
        self.setParent(parent)
        
        self.xlabel = "Q"
        self.ylabel = "V общее"
        
        self.graphEnabled = False


    def clearAll(self, draw=False):
        self.figure.clf()
        if draw:
            self.draw_idle()
        
        self.graphEnabled = False
       
        
    def setLabels(self, xlabel, ylabel):
        self.clearAll()

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.ax = self.figure.subplots(1)
        self.ax.set_xlabel(self.PLOT_LABELS[xlabel])
        self.ax.set_ylabel(self.PLOT_LABELS[ylabel])
        
    
    def plot(self, test, battery):
        if self.xlabel == "Q":
            x = test.df["Q,Ah"].abs()

        elif self.xlabel == "Q/m":
            x = (test.df["Q,Ah"] / (battery.mass / 1000)).abs()

        if self.ylabel == "V общее":
            y = test.df["U,V"]

        elif self.ylabel == "V на аккум.":
            y = test.df["U,V"] / battery.numCells
            

        self.ax.plot(x, y,
                     label=f"Батарея {battery.name}\n"
                     f"{test.name}")
       
        
    def finishPlot(self, empty=False):
        self.ax.legend()
        self.ax.grid()
        self.ax.xaxis.set_major_locator(MultipleLocator(1))
        self.draw_idle()
        
        self.graphEnabled = True


    def save(self):
        if not self.graphEnabled:
            QMessageBox.warning(self, "Ошибка сохранения", "График пуст. Сначала выберите в списке выше кривые и постройте их")
            return
        
        default_name = "unnamed.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить график",
            os.path.join(".", default_name),
            "SVG файлы (*.svg);;PDF файлы (*.pdf);;PNG файлы (*.png);;JPEG файлы (*.jpeg);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            original_size = self.figure.get_size_inches()
            self.figure.set_size_inches(11.69, 8.27)
        
            self.figure.savefig(file_path, dpi=150, bbox_inches="tight")

            self.figure.set_size_inches(original_size)
            
            QMessageBox.information(self, "График сохранён", f"График сохранён по пути:\n{file_path}")
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить график.\nОшибка: {e}")