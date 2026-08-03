import os
import pandas as pd

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QTableView, QHeaderView,
                               QFileDialog, QMessageBox)

from battery import calcQ
from models import CurvesModel

from ui_py.ui_curves import Ui_CurvesPage
from ui_py.ui_filter import Ui_FilterBox



class CurvesPage(QWidget, Ui_CurvesPage):
    def __init__(self, parent, batteriesManager):
        super().__init__(parent)
        self.setupUi(self)
        
        self.curves = None
        
        self.initTable(batteriesManager)
        
        self.selectAll_button.clicked.connect(self.model.selectAll)
        self.deselectAll_button.clicked.connect(self.model.deselectAll)
        self.showChecked_button.clicked.connect(self.showChecked)
        
        self.plot_button.clicked.connect(self.plot)
        self.save_button.clicked.connect(self.save)
        self.settings_button.clicked.connect(self.canvas.settingsDialog)
        
        self.tableView.activated.connect(self.model.setCheck)
        
        self.oX_comboBox.currentTextChanged.connect(self.model.setXlabel)
        
        self.addFilter_button.clicked.connect(self.addFilter)
        self.applyFilter_button.clicked.connect(self.applyFilter)
        
        
    def updatePage(self):
        self.canvas.clearAll(draw=True)
        self.model.refresh()
        self.model.deselectAll()
        self.showChecked_button.setText("Показать только выбранное")
        
        
    def initTable(self, batteriesManager):
        self.model = CurvesModel(batteriesManager,
                                 self.oX_comboBox.currentText())
        self.tableView.setModel(self.model)
        
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        
    def showChecked(self):
        if self.showChecked_button.text() == "Показать только выбранное":
            self.showChecked_button.setText("Показать все")
            self.model.showChecked()
        elif self.showChecked_button.text() == "Показать все":
            self.showChecked_button.setText("Показать только выбранное")
            self.model.refresh()
            
            
    def addFilter(self):
        newFilterBox = FilterBox(self)
        self.filtersLayout.insertWidget(0, newFilterBox)
        newFilterBox.selfDel_signal.connect(self.delFilter)
        
        
    def delFilter(self, filterBox):
        self.filtersLayout.removeWidget(filterBox)
        filterBox.setParent(None)
        filterBox.deleteLater()
            
            
    def applyFilter(self):
        self.model.deselectAll()
        for i in range(self.filtersLayout.count()):
            widget = self.filtersLayout.itemAt(i).widget()
            if isinstance(widget, FilterBox):
                self.model.filter(*widget.filterParams())
    
        
    def plot(self):
        xlabel = self.oX_comboBox.currentText()
        ylabel = self.oY_comboBox.currentText()
        
        selected = self.model.getSelected()
        
        if not selected:
            self.canvas.finishPlot(empty=True)
            return
        
        self.canvas.setSettings(xlabel, ylabel)
        
        for battery, test in selected:
            if (battery, test) in self.model.labels:
                label = self.model.labels[(battery, test)]
            else:
                label = f"{battery.name} {test.name}"
            self.canvas.plot(test, battery, label)
        
        self.canvas.finishPlot()
        
        
    def save(self):
        if not self.canvas.graphEnabled:
            QMessageBox.warning(self, "Ошибка сохранения", "График пуст. Сначала выберите в списке выше кривые и постройте их")
            return
        
        default_name = "unnamed"
        file_path, filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить данные",
            os.path.join(".", default_name),
            "CSV файлы (*.csv);;"
            "PDF файлы (*.pdf);;PNG файлы (*.png);;JPEG файлы (*.jpeg);;Все файлы (*)"
            "Все файлы (*)"
        )
        
        if not file_path:
            return
        
        if filter == "CSV файлы (*.csv)":
            xlabel = self.oX_comboBox.currentText()
            ylabel = self.oY_comboBox.currentText()
            selected = self.model.getSelected()
        
            if not selected:
                QMessageBox.warning(self, "Ничего не выбрано", "Выберите в списке выше испытания для сохранения")
        
            if len(selected) == 1:                
                battery, test = selected[0]
                x, y = calcQ(test, battery, xlabel, ylabel)
                pd.DataFrame({xlabel : x, ylabel : y}).to_csv(file_path, index=False, encoding="utf-8")
                QMessageBox.information(self, "Данные сохранены", f"Данные сохранены по пути:\n{file_path}")
                
            else:
                QMessageBox.warning(self, "Выбрано более одного испытания", "Возможно сохранять в CSV только одно испытание")
        
        else:
            self.canvas.save(file_path)
            
    
            
class FilterBox(QWidget, Ui_FilterBox):
    selfDel_signal = Signal(QWidget)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        
        self.filterComboBox.addItems(["Емкость ном, Ач", "Емкость эксп, Ач", "Энергоемкость, Вт ч", "Число аккумуляторов", "Уд. емкость, Ач/кг", "Уд. энергоемкость, Вт ч/кг"])
        self.selfDel_button.clicked.connect(lambda: self.selfDel_signal.emit(self))
        
        
    def filterParams(self):
        column = self.filterComboBox.currentText()
        fromValue = self.fromSpinBox.value()
        toValue = self.toSpinBox.value()
        
        return column, fromValue, toValue