from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QDialog, QMessageBox,
                               QHeaderView, QTableView)

import validate
from models import BatteriesModel

from ui_py.ui_batteries import Ui_BatteriesPage
from ui_py.ui_battery_params import Ui_BatteryParamsDialog


class BatteriesPage(QWidget, Ui_BatteriesPage):
    batterySelected = Signal(object)
    
    def __init__(self, parent, batteriesManager):
        super().__init__(parent)
        self.setupUi(self)
        
        self.batteriesManager = batteriesManager
        self.initTable()
        
        self.addBattery_button.clicked.connect(self.addBattery_dialog)
        self.delBattery_button.clicked.connect(self.delBattery)
        self.editBattery_button.clicked.connect(self.editBattery)
        self.testsOpen_button.clicked.connect(self.testsOpen)
        
        
    def initTable(self):
        self.model = BatteriesModel(self.batteriesManager)
        self.tableView.setModel(self.model)
        
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        
    def getSelectedBatteryId(self):
        selection = self.tableView.selectionModel().selectedRows()
        if not selection:
            QMessageBox.warning(self, "Не выбрана батарея",
                        "Выберите (или добавьте) батарею")
            return None
        row = selection[0].row()
        batteryId = self.model.getBatteryId(row)
        return batteryId
                
        
    def addBattery(self, name, numCells, mass):
        self.batteriesManager.add(name, numCells, mass)
        self.model.refresh()
        
        
    def delBattery(self):
        batteryId = self.getSelectedBatteryId()
        if batteryId:
            self.batteriesManager.delete(batteryId)
            self.model.refresh()
            
            
    def editBattery(self):
        batteryId = self.getSelectedBatteryId()
        if batteryId:
            battery = self.batteriesManager.get(batteryId)
            dialog = BatteryParamsDialog(self, battery)
            if dialog.exec() == QDialog.Accepted:
                battery.setParams(*dialog.params())
                self.model.refresh()
            dialog.deleteLater()
        
        
    def addBattery_dialog(self):            
        dialog = BatteryParamsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.addBattery(*dialog.params())
        dialog.deleteLater()
        
        
    def fillTable(self):
        self.model.refresh()
        
        
    def testsOpen(self):
        batteryId = self.getSelectedBatteryId()
        if batteryId:
            battery = self.batteriesManager.get(batteryId)
            self.batterySelected.emit(battery)
        
   
        
class BatteryParamsDialog(QDialog, Ui_BatteryParamsDialog):
    def __init__(self, parent, battery=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.battery = battery
        
        if battery:
            self.nameInput.setText(battery.name)
            self.numCellsInput.setValue(battery.numCells)
            self.massInput.setValue(battery.mass)
            self.setWindowTitle("Изменение параметров АКБ")
        
        else:
            self.nameInput.setText("")
            self.numCellsInput.setValue(1)
            self.massInput.setValue(5.0)
            self.setWindowTitle("Создание новой АКБ")
        
        
    def params(self):
        return (
            self.nameInput.text(),
            self.numCellsInput.value(),
            self.massInput.value(),
        )
        
    
    def accept(self):
        if self.battery:
            oldName = self.battery.name
        else:
            oldName = ""
            
        message = validate.BATTERY_PARAMS(
            *self.params(),
            self.parent().batteriesManager,
            oldName
        )
        
        if message == "ok":
            super().accept()
        
        else:
            QMessageBox.warning(self, "Недопустимые параметры", message)