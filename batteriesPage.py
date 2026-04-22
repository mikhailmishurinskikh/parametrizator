import os
import zipfile
import tempfile
import json
from pathvalidate import is_valid_filename

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (QWidget, QDialog,
                               QMessageBox, QTableWidgetItem,
                               QHeaderView, QTableWidget, QPushButton,
                               QFileDialog, QProgressDialog)

from battery import Battery, BatteriesManager

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
        
        self.archiveThread = None
        
        self.addBattery_button.clicked.connect(self.add_battery_dialog)
        self.delBattery_button.clicked.connect(self.delBattery)
        self.changeBatteryParams_button.clicked.connect(self.changeBatteryParams)
        self.saveBattery_button.clicked.connect(self.saveBattery)
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
        
        
    def saveBattery(self):
        if not(self.saveThread is None):
            QMessageBox.warning(self, "Сохранение не завершено",
                        "Дождитесь завершения предыдущего сохранения")
            return
        
        batteryId = self.table.getSelectedId()
        if batteryId < 0:
            QMessageBox.warning(self, "Не выбрана батарея",
                        "Выберите (или добавьте) батарею")
            return
        
        data = self.batteries.get(batteryId).saveData()
        
        default_name = data["name"]
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить данные батареи в архив",
            os.path.join(".", default_name),
            "ZIP архивы (*.zip);;Все файлы (*)"
        )
        
        if not file_path:
            return
        
        self.archiveThread = ArchiveSaveWorker(file_path, data)
        self.archiveThread.finished.connect(lambda message: self.saveBattery_finish(message, file_path, data["name"]))
        self.archiveThread.start()
        
        
    def saveBattery_finish(self, message, path, name):
        self.archiveThread.finished.disconnect()
        self.archiveThread.deleteLater()
        self.archiveThread = None
        if message == "ok":
            QMessageBox.information(self, "Сохранение завершено",
                        f"Данные батареи {name} успешно сохранены в архив по пути: {path}")
            
        else:
            QMessageBox.warning(self, "Ошибка при сохранении",
                        f"Не удалось сохранить данные батареи. Возникла ошибка {message}")
        
        
        
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
        self.tests = {}
        
        self.thread = None
        
        if name:
            self.changing = True
            self.setWindowTitle("Изменение параметров АКБ")
            self.selectFile_button.setText("Недоступно")
        
        else:
            self.changing = False
            self.setWindowTitle("Создание новой АКБ")
            
        self.selectFile_button.clicked.connect(self.loadFromFile)
        
        
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
    
    
    def loadFromFile(self):
        if self.changing:
            QMessageBox.warning("Загрузка батареи из архива недоступна "
                                "при редактировании уже добавленной батареи")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",  # начальная директория
            "ZIP архивы (*.zip);;"
            "Все файлы (*.*)"
        )
        
        if file_path:
            progress = QProgressDialog("Загрузка батареи...", "Отмена", 0, 100, self)
            progress.setWindowTitle("Загрузка")
            progress.setWindowModality(Qt.WindowModality.ApplicationModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            
            self.thread = ArchiveLoadWorker(file_path)
            self.thread.paramsRead.connect(self.setParams)
            self.thread.testsRead.connect(self.setTests)
            self.thread.finished.connect(lambda x: progress.close())
            
            self.thread.start()
            progress.exec()
            
            
        
    def setParams(self, name, mass, numCells, message):
        if name:
            try:
                self.nameInput.setText(name)
            except:
                message += "Не удалось установить название батареи\n"
        
        if mass > 0:
            try:
                self.massInput.setValue(mass)
            except:
                message += "Не удалось установить массу батареи\n"
        
        if numCells > 0:
            try:
                self.numCellsInput.setValue(numCells)
            except:
                message += "Не удалось установить число аккумуляторов\n"
        
        if message:
            QMessageBox.warning(self, "Предупреждение", message)
            
            
    def setTests(self, tests):
        self.tests = tests
            
            
        
            
        

class ArchiveSaveWorker(QThread):
    finished = Signal(str)
    
    def __init__(self, path, data):
        super().__init__()
        self.path = path
        self.data = data
        
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                metadata = {k: v for k, v in self.data.items() if k != 'tests'}
                metadata.update({
                    "tests" : [{
                        "name" : test["name"],
                        "file" : test["file"],
                        "testType" : test["testType"]
                    } for test in self.data["tests"]]
                })
                
                with open(os.path.join(tmpdir, "metadata.json"),
                          "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                    
                tests = self.data.get('tests', [])
                for test in tests:
                    df = test["df"]
                    
                    df.to_csv(os.path.join(tmpdir, f"{test["name"]}.csv"),
                              index=False, encoding="utf-8")
                    
                with zipfile.ZipFile(
                        self.path,
                        "w",
                        compression=zipfile.ZIP_DEFLATED,
                        compresslevel=6) as zipf:
                    
                    for filename in os.listdir(tmpdir):
                        zipf.write(os.path.join(tmpdir, filename), filename)
                
            
            self.finished.emit("ok")
                
                
        except Exception as e:
            self.finished.emit(str(e))
            
            
class ArchiveLoadWorker(QThread):
    paramsRead = Signal(str, float, int, str)
    testsRead = Signal(dict)
    finished = Signal(str)
    
    def __init__(self, path):
        super().__init__()
        self.path = path
        
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(self.path, 'r') as zipf:
                    zipf.extractall(tmpdir)
                
                metadata = None
                metadata_path = os.path.join(tmpdir, "metadata.json")
                messageMetadata = ""                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except:
                        messageMetadata += "Не удалось открыть файл metadata.json\n"
                
                else:
                    messageMetadata += "Файл metadata.json не найден в архиве\n"
                
                if metadata:
                    name = metadata.get('name', "")
                    
                    try:
                        mass = float(metadata.get('mass', 5.0))
                        if mass < 5: raise ValueError()
                    except:
                        mass = -1
                        messageMetadata += "Масса имеет неверный формат\n"
                    
                    try:
                        numCells = int(metadata.get('numCells', 1))
                        if numCells < 1: raise ValueError()
                    except:
                        numCells = -1
                        messageMetadata += "Число ячеек имеет неверный формат\n"
                    
                    self.paramsRead.emit(name, mass, numCells, messageMetadata)
                    
                self.testsRead.emit({})
                
            self.finished.emit("ok")
                    
        except Exception as e:
            self.finished.emit(str(e))