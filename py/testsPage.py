import tempfile
import zipfile
import os

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (QWidget, QFileDialog, QDialog,
                               QMessageBox, QDialogButtonBox, QHeaderView,
                               QTableView, QComboBox, QProgressDialog)

import pyqtgraph as pg
pg.setConfigOptions(background='w', foreground='k')

from readers import read
from models import TestsModel
from separateTestDialog import SeparateTest_dialog
from plotItems import makeCurve
import validate

from ui_py.ui_test_add_dialog import Ui_TestAddDialog
from ui_py.ui_test_edit_dialog import Ui_TestEditDialog
from ui_py.ui_tests import Ui_TestsPage



class TestsPage(QWidget, Ui_TestsPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        
        self.battery = None
        self.archiveThread = None
        
        self.initTable()
        
        self.addTest_button.clicked.connect(self.addTest_dialog)
        self.delTest_button.clicked.connect(self.delTest)
        self.editTest_button.clicked.connect(self.editTest)
        self.addArchive_button.clicked.connect(self.add_from_archive)
        self.saveArchive_button.clicked.connect(self.save_to_archive)
        self.separateTest_button.clicked.connect(self.separateTest)
        self.tableView.selectionModel().selectionChanged.connect(self.plot)
        
        
    def initTable(self):
        self.model = TestsModel()
        self.tableView.setModel(self.model)
        
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        
    def getSelectedTest(self, warning=True):
        selection = self.tableView.selectionModel().selectedRows()
        if not selection:
            if warning:
                QMessageBox.warning(self, "Не выбрана батарея",
                            "Выберите (или добавьте) батарею")
            return None
        row = selection[0].row()
        testId = self.model.getId(row)
        test = self.battery.getTest(testId)
        return test
        
        
    def setBattery(self, battery):
        self.battery = battery
        self.batteryLabel.setText(f"{battery.name}")
        self.model.setBattery(battery)
        
        
    def addTest_dialog(self):            
        dialog = TestAddDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.battery.addTest(dialog.name, dialog.testType, dialog.df)
        dialog.deleteLater()
        self.model.refresh()
        
        
    def delTest(self):
        test = self.getSelectedTest()
        if test:
            self.battery.deleteTest(test.id)
            self.model.refresh()
        
        
    def editTest(self):
        test = self.getSelectedTest()
        if test:
            dialog = TestEditDialog(self, test)
            if dialog.exec() == QDialog.Accepted:
                test.setParams(*dialog.params())
            dialog.deleteLater()
            self.model.refresh()
            
            
    def separateTest(self):
        test = self.getSelectedTest()
        
        dialog = SeparateTest_dialog(self, test)
        if dialog.exec() == QDialog.Accepted:
            if dialog.new:
                self.battery.addTest(dialog.name, test.testType, dialog.resultDf)
            
            else:
                test.df = dialog.resultDf
                                
        dialog.deleteLater()
        self.model.refresh()
    
    
    def plot(self, selected, deselected):
        self.graphicsView.clear()
        
        test = self.getSelectedTest(warning=False)
        if not test: return
        
        curve = makeCurve(test.testType)
        self.graphicsView.addItem(curve, row=0, col=0)
        curve.plotDf(test.df)
        
    
    def add_from_archive(self):
        archive_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",  # начальная директория
            "ZIP архивы (*.zip);;"
            "Все файлы (*.*)"
        )
        
        if not archive_path:
            return
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(tmpdir)
                    
                for filename in os.listdir(tmpdir):
                    file_path = os.path.join(tmpdir, filename)
                    
                    message, df, testType = read(file_path, "Стандартные CSV файлы (*.csv)")
                    if message == "ok":
                        self.add_test(df, archive_path, testType, filename.replace(".csv", ""))
                        
                    else:
                        QMessageBox.warning(self, "Некорректный файл", message)
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка чтения архива", f"Возникла ошибка: {str(e)}")
    
        
    def save_to_archive(self):
        if not(self.archiveThread is None):
            QMessageBox.warning(self, "Сохранение не завершено",
                        "Дождитесь завершения предыдущего сохранения")
            return
        
        if not self.battery.tests:
            QMessageBox.warning(self, "Испытания не добавлены",
                        "Нет испытаний для сохранения")
            return
        
        default_name = self.battery.name
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить данные батареи в архив",
            os.path.join(".", default_name),
            "ZIP архивы (*.zip);;Все файлы (*)"
        )
        
        if not file_path:
            return
        
        self.archiveThread = ArchiveSaveWorker(file_path, list(self.battery.tests.values()))
        self.archiveThread.finished.connect(lambda message: self.save_to_archive_finish(message, file_path, self.battery.name))
        self.archiveThread.start()
        
        
    def save_to_archive_finish(self, message, path, name):
        self.archiveThread.finished.disconnect()
        self.archiveThread.deleteLater()
        self.archiveThread = None
        if message == "ok":
            QMessageBox.information(self, "Сохранение завершено",
                        f"Данные батареи {name} успешно сохранены в архив по пути: {path}")
            
        else:
            QMessageBox.warning(self, "Ошибка при сохранении",
                        f"Не удалось сохранить данные батареи. Возникла ошибка {message}")
          
        
            
class TestAddDialog(QDialog, Ui_TestAddDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        
        self.Ok = self.buttonBox.button(QDialogButtonBox.Ok)
        self.Ok.setEnabled(False)
        
        self.file_button.clicked.connect(self.open_dialog)
    
        
    def open_dialog(self):
        file_path, filter = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",  # начальная директория
            "NDAX файлы (*.ndax);;"
            "XLSX файлы со стендов (*.xlsx);;"
            "Нормированные кривые из таблицы учета (*.csv);;"
            "CSV со столбцами NDAX (*.csv);;"
            "Стандартные CSV файлы (*.csv);;"
            "Текстовые файлы ЯРОСТАНМАШ (*.txt);;"
            "Все файлы (*.*)"
        )
        
        if file_path:
            message, df, testType = read(file_path, filter)
            if message == "ok":
                self.df = df
                self.testType = testType
            else:
                QMessageBox.warning(self, "Некорректный файл", message)
                
            self.graphicsView.clear()
            
            curve = makeCurve(testType)
            self.graphicsView.addItem(curve, row=0, col=0)
            curve.plotDf(df)
                
            self.fileInput.setText(file_path)
            self.Ok.setEnabled(True)

                
    def accept(self):
        name = self.nameInput.text()
        message = validate.TEST_NAME(name, self.parent().battery)
        if message == "ok":
            self.name = name
            super().accept()
            
        else:
            QMessageBox.warning(self, "Недопустимое название", message)
            
            
            
class TestEditDialog(QDialog, Ui_TestEditDialog):
    def __init__(self, parent, test):
        super().__init__(parent)
        self.setupUi(self)
        
        possibleTypes = test.possibleTypes()
        self.typeInput.addItems(possibleTypes)
        
        self.typeInput.setCurrentText(test.testType)
        self.nameInput.setText(test.name)
        
        self.test = test
        
        
    def accept(self):
        name = self.nameInput.text()
        message = validate.TEST_NAME(name, self.parent().battery, self.test.name)
        if message == "ok":
            super().accept()
            
        else:
            QMessageBox.warning(self, "Недопустимое название", message)
            
            
    def params(self):
        return self.nameInput.text(), self.typeInput.currentText()
        
      
                
                
class ArchiveSaveWorker(QThread):
    finished = Signal(str)
    
    def __init__(self, path, tests):
        super().__init__()
        self.path = path
        self.tests = tests
        
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                for test in self.tests:
                    test.df.to_csv(os.path.join(tmpdir, f"{test.name}.csv"),
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