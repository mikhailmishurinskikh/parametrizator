import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QTreeWidget, QHeaderView,
                               QAbstractItemView, QTreeWidgetItem,
                               QTreeWidgetItemIterator, QFileDialog,
                               QMessageBox, QDialog)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

from battery import calcQ

from ui_py.ui_curves import Ui_CurvesPage
from ui_py.ui_graph_params import Ui_GraphParams


FIGSIZE = {
    "А4 (альбомн.)" : (11.69, 8.27),
    "А4 (книжн.)" : (8.27, 11.69),
    "По умолчанию" : (6.5, 4.0)
}
    
DEFAULT_SETTINGS = {
    'Q': "Емкость батареи, Ач",
    'V общее': "Напряжение батареи, В",
    'Q/m': "Уд. ёмкость батареи, Ач/кг",
    'V на аккум.': "Напряжение на один аккумулятор, В",
    'title': "",
    'size': "По умолчанию",
    'default_ticksX': True,
    'default_ticksY': True
}


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
        self.settings_button.clicked.connect(self.canvas.settingsDialog)
        
        self.oX_comboBox.currentTextChanged.connect(lambda text: self.list.updateQItems(text, self.curves))
        
        
    def updatePage(self, batteries):
        self.curves = batteries.curves()
        self.list.updateList(self.curves, self.oX_comboBox.currentText())
        self.canvas.clearAll(draw=True)
        
        
    def plot(self):
        xlabel = self.oX_comboBox.currentText()
        ylabel = self.oY_comboBox.currentText()
        
        selected = self.list.getSelected()
        
        if not selected:
            self.canvas.finishPlot(empty=True)
            return
        
        self.canvas.setSettings(xlabel, ylabel)
        
        for ids in selected:
            battery = self.curves[ids["batteryId"]]["battery"]
            test = self.curves[ids["batteryId"]]["tests"][ids["testId"]]
            self.canvas.plot(test, battery)
        
        self.canvas.finishPlot()
        
        
        
class CurvesList(QTreeWidget):
    class Column:
        header = ["Данные испытаний", "Ёмкость, Ач", "Тип кривой", "Выбрано"]
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
        
        
    def updateList(self, curves, xlabel):
        self.clear()
        for batteryId, batteryData in curves.items():
            batteryItem = QTreeWidgetItem(self)
            batteryItem.setText(0, batteryData["battery"].name)
            
            for testId, test in batteryData["tests"].items():
                testItem = QTreeWidgetItem(batteryItem)
                testItem.setText(self.Column.NAME, test.name)
                testItem.setText(self.Column.TYPE, test.testType)
                
                testItem.setData(self.Column.CHECK, Qt.UserRole, {
                    "testId" : testId,
                    "batteryId" : batteryId
                })
                
                testItem.setFlags(testItem.flags() | Qt.ItemIsUserCheckable)
                testItem.setCheckState(self.Column.CHECK, Qt.Unchecked)
        self.updateQItems(xlabel, curves)
                
                
    def updateQItems(self, xlabel, curves):
        if xlabel == "Q":
            self.headerItem().setText(self.Column.Q, "Емкость, Ач")
        
        elif xlabel == "Q/m":
            self.headerItem().setText(self.Column.Q, "Уд. емкость, Ач/кг")
            
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            iterator += 1
            
            ids = item.data(self.Column.CHECK, Qt.UserRole)
            if ids is None: continue
            
            battery = curves[ids["batteryId"]]["battery"]
            test = curves[ids["batteryId"]]["tests"][ids["testId"]]
            
            x = calcQ(test, battery, xlabel)
            
            item.setText(self.Column.Q, f"{x.max():.2f}")
                
                
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
    def __init__(self, parent):
        super().__init__(Figure(constrained_layout=True))
        self.setParent(parent)
        
        self.xlabel = "Q"
        self.ylabel = "V общее"
        self.settings = DEFAULT_SETTINGS
        
        self.graphEnabled = False


    def clearAll(self, draw=False):
        self.figure.clf()
        if draw:
            self.draw_idle()
        
        self.graphEnabled = False
       
        
    def setSettings(self, xlabel, ylabel):
        self.clearAll()

        self.xlabel = xlabel
        self.ylabel = ylabel
        self.ax = self.figure.subplots(1)
        self.ax.set_xlabel(self.settings[xlabel])
        self.ax.set_ylabel(self.settings[ylabel])
        
        if self.settings["title"]:
            self.ax.set_title(self.settings["title"])
        
    
    def plot(self, test, battery):
        x, y = calcQ(test, battery, self.xlabel, self.ylabel)

        self.ax.plot(x, y,
                     label=f"Батарея {battery.name}\n"
                     f"{test.name}")
       
        
    def finishPlot(self, empty=False):
        if empty:
            self.clearAll(draw=True)
            self.graphEnabled = False
            return
            
        self.ax.legend()
        if not self.settings["default_ticksX"]:
            x_min, x_max = self.ax.get_xlim()
            xstep = self.settings["xstep"]
            
            XticksNum = (x_max - x_min) / xstep
            if XticksNum > 100:
                QMessageBox.warning(self, "Ошибка в шаге сетки",
                                    "Вы выбрали слишком малый шаг сетки по оси X.\n"
                                    "График будет построен с шагом по умолчанию")
            else:
                self.ax.xaxis.set_major_locator(MultipleLocator(xstep))
        
        if not self.settings["default_ticksY"]:
            y_min, y_max = self.ax.get_ylim()
            ystep = self.settings["ystep"]
            
            YticksNum = (y_max - y_min) / ystep
            if YticksNum > 100:
                QMessageBox.warning(self, "Ошибка в шаге сетки",
                                    "Вы выбрали слишком малый шаг сетки по оси Y.\n"
                                    "График будет построен с шагом по умолчанию")
            else:
                self.ax.yaxis.set_major_locator(MultipleLocator(ystep))
        
        self.ax.grid()
        self.draw_idle()
        
        self.graphEnabled = True


    def save(self):
        if not self.graphEnabled:
            QMessageBox.warning(self, "Ошибка сохранения", "График пуст. Сначала выберите в списке выше кривые и постройте их")
            return
        
        default_name = "unnamed"
        file_path, selected_ext = QFileDialog.getSaveFileName(
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
            self.figure.set_size_inches(FIGSIZE[self.settings["size"]])
        
            self.figure.savefig(file_path)

            self.figure.set_size_inches(original_size)
            
            QMessageBox.information(self, "График сохранён", f"График сохранён по пути:\n{file_path}")
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить график.\nОшибка: {e}")
            
            
    def settingsDialog(self):
        dialog = GraphParamsDialog(self, self.settings)
        
        if dialog.exec() == QDialog.Accepted:
            self.settings = dialog.settings()
        dialog.deleteLater()
                        
            
            
class GraphParamsDialog(QDialog, Ui_GraphParams):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.setupUi(self)
        self.setSettings(settings)
        
        self.reset_button.clicked.connect(self.resetSettings)
        self.stepX_checkBox.toggled.connect(self.enableStepX)
        self.stepY_checkBox.toggled.connect(self.enableStepY)
        
    
    def setSettings(self, settings):
        self.Qlabel_input.setText(settings["Q"])
        self.Vlabel_input.setText(settings["V общее"])
        self.Qmlabel_input.setText(settings["Q/m"])
        self.Vcelllabel_input.setText(settings["V на аккум."])
        self.title_input.setText(settings["title"])
        self.size_comboBox.setCurrentText(settings["size"])
        if settings["default_ticksX"]:
            self.stepX_checkBox.setChecked(True)
            self.stepX_input.setValue(0)
        else:
            self.stepX_checkBox.setChecked(False)
            self.stepX_input.setEnabled(True)
            self.stepX_input.setValue(settings["xstep"])
            
        if settings["default_ticksY"]:
            self.stepY_checkBox.setChecked(True)
            self.stepY_input.setValue(0)
        else:
            self.stepY_checkBox.setChecked(False)
            self.stepY_input.setEnabled(True)
            self.stepY_input.setValue(settings["ystep"])
        
        
    
    def resetSettings(self):
        self.setSettings(DEFAULT_SETTINGS)
        
    
    def enableStepX(self, state):
        self.stepX_input.setValue(0)
        self.stepX_input.setEnabled(not state)
        
        
    def enableStepY(self, state):
        self.stepY_input.setValue(0)
        self.stepY_input.setEnabled(not state)
        
        
    def settings(self):
        settings = {
            'Q': self.Qlabel_input.text(),
            'V общее': self.Vlabel_input.text(),
            'Q/m': self.Qmlabel_input.text(),
            'V на аккум.': self.Vcelllabel_input.text(),
            'title': self.title_input.text(),
            "size" : self.size_comboBox.currentText(),
            "default_ticksX" : self.stepX_checkBox.isChecked(),
            "default_ticksY" : self.stepY_checkBox.isChecked(),
        }
        
        if not self.stepX_checkBox.isChecked():
            settings['xstep'] = self.stepX_input.value()
            
        if not self.stepY_checkBox.isChecked():
            settings['ystep'] = self.stepY_input.value()
        
        return settings
    
    
    def accept(self):
        if not self.stepX_checkBox.isChecked():
            if self.stepX_input.value() == 0:
                QMessageBox.warning("Размер шага по оси X не может быть нулевым")
                return
            
        if not self.stepY_checkBox.isChecked():
            if self.stepY_input.value() == 0:
                QMessageBox.warning("Размер шага по оси Y не может быть нулевым")
                return
        
        super().accept()
                