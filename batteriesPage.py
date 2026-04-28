import os
import zipfile
import tempfile
from pathvalidate import is_valid_filename

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (QWidget, QDialog,
                               QMessageBox, QTableWidgetItem,
                               QHeaderView, QTableWidget, QPushButton,
                               QFileDialog, QProgressDialog)

from battery import Battery, BatteriesManager, to_pandas

from ui_py.ui_batteries import Ui_BatteriesPage
from ui_py.ui_battery_params import Ui_BatteryParamsDialog


class BatteriesPage(QWidget, Ui_BatteriesPage):
    batterySelected = Signal(Battery)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        
        self.table = BatteriesTable(self)
        self.tableLayout.addWidget(self.table)
        
        self.batteries = BatteriesManager()
        
        self.addBattery_button.clicked.connect(self.add_battery_dialog)
        self.delBattery_button.clicked.connect(self.delBattery)
        self.changeBatteryParams_button.clicked.connect(self.changeBatteryParams)
        self.table.batterySelected.connect(
            lambda battery_id: self.batterySelected.emit(self.batteries.get(battery_id))
        )
        
        
    def addBattery(self, name, numCells, mass):
        battery = self.batteries.add(name, numCells, mass)
        self.table.addBattery(battery)
        
        
    def delBattery(self):
        batteryId = self.table.deleteSelected()
        if batteryId < 0:
            QMessageBox.warning(self, "Не выбрана батарея",
                        "Выберите (или добавьте) батарею")
            return
        
        self.batteries.delete(batteryId)        
        
        
    def add_battery_dialog(self):            
        dialog = BatteryParamsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.addBattery(*dialog.params())
        dialog.deleteLater()
            
            
    def changeBatteryParams(self):
        batteryId = self.table.getSelectedId()
        if batteryId < 0:
            QMessageBox.warning(self, "Не выбрана батарея",
                        "Выберите (или добавьте) батарею")
            return
        
        battery = self.batteries.get(batteryId)
        
        dialog = BatteryParamsDialog(self, battery.name, battery.numCells, battery.mass)
        if dialog.exec() == QDialog.Accepted:
            battery.setParams(*dialog.params())
            self.table.setParams(*dialog.params())
        dialog.deleteLater()
        
        
    def fillTable(self):
        self.table.setRowCount(0)
        for battery in self.batteries.BPAdata():
            self.table.addBattery(battery)
        
    
class BatteriesTable(QTableWidget):
    class Column:
        header = ["id АКБ", "Название", "Число аккумуляторов", "Масса, г", "Данные испытаний"]
        ID = 0
        NAME = 1
        NUM_CELLS = 2
        MASS = 3
        BUTTON = 4
        
    batterySelected = Signal(int)
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setColumnCount(len(self.Column.header))
        self.setHorizontalHeaderLabels(self.Column.header)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        self.horizontalHeader().hideSection(self.Column.ID)
        
        self.itemChanged.connect(self.batteryParamsChanged)
        
        
    def getBatteryId(self, row):
        return int(self.item(row, self.Column.ID).text())
    
    
    def getSelectedId(self):
        row = self.currentRow()
        if row < 0:
            return -1
        return int(self.item(self.currentRow(), self.Column.ID).text())
        
        
    def addBattery(self, battery):
        self.blockSignals(True)
        
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        self.setItem(row_position, self.Column.ID, QTableWidgetItem(f"{battery.id}"))
        self.setItem(row_position, self.Column.NAME, QTableWidgetItem(battery.name))
        self.setItem(row_position, self.Column.NUM_CELLS, QTableWidgetItem(f"{battery.numCells}"))
        self.setItem(row_position, self.Column.MASS, QTableWidgetItem(f"{battery.mass}"))
        
        for i in [self.Column.NAME, self.Column.NUM_CELLS, self.Column.MASS]:
            item = self.item(row_position, i)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setToolTip(item.text())
        
        openTestsButton = QPushButton("Просмотр")
        self.setCellWidget(row_position, self.Column.BUTTON, openTestsButton)
        openTestsButton.clicked.connect(
            lambda: self.batterySelected.emit(battery.id)
        )
        
        self.blockSignals(False)
        
        
    def setParams(self, name, numCells, mass):
        self.blockSignals(True)
        row_position = self.currentRow()
        self.item(row_position, self.Column.NAME).setText(name)
        self.item(row_position, self.Column.NUM_CELLS).setText(f"{numCells}")
        self.item(row_position, self.Column.MASS).setText(f"{mass}")
        self.blockSignals(False)
        
    
    def batteryParamsChanged(self, item):
        self.blockSignals(True)
        battery_id = self.getBatteryId(item.row())
        param = self.horizontalHeaderItem(item.column()).text()
        item.setText(self.parent().getBattery(battery_id).changeParams(param, item.text()))
        self.blockSignals(False)
        
    
    def deleteSelected(self):
        if self.currentRow() < 0:
            return -1
        
        self.blockSignals(True)
        battery_id = self.getBatteryId(self.currentRow())
        self.removeRow(self.currentRow())
        self.blockSignals(False)
        return battery_id
        
        
        
class BatteryParamsDialog(QDialog, Ui_BatteryParamsDialog):
    def __init__(self, parent=None, name="", numCells=1, mass=5):
        super().__init__(parent)
        self.setupUi(self)
        
        self.nameInput.setText(name)
        self.numCellsInput.setValue(numCells)
        self.massInput.setValue(mass)
        
        self.thread = None
        
        if name:
            self.changing = True
            self.setWindowTitle("Изменение параметров АКБ")
        
        else:
            self.changing = False
            self.setWindowTitle("Создание новой АКБ")
        
        
    def params(self):
        return (
            self.nameInput.text(),
            self.numCellsInput.value(),
            self.massInput.value(),
        )
        
    
    def accept(self):
        if self.validate(*self.params()):
            super().accept()
        
        
    def validate(self, name, numCells, mass):
        if not name:
            QMessageBox.warning(self, "Название не задано",
                                "Вы не ввели название АКБ")
            return False
            
        batteriesNames = self.parent().batteries.names()
        if not self.changing and name in batteriesNames:
            QMessageBox.warning(self, "Название занято",
                                "Уже добавлена АКБ с таким названием.\n"
                                "Выберите другое название")
            return False
        
        if mass < 5:
            QMessageBox.warning(self, "Неверная масса батареи",
                                "Масса батареи менее 5 грамм\n"
                                "Введите реалистичную массу")
            return False
        
        if not is_valid_filename(name):
            QMessageBox.warning(self, "Недопустимое имя",
                                "Ваша операционная система не позволяет "
                                "создавать файлы с таким именем")
            return False
        
        return True