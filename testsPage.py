from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFileDialog, QDialog,
                               QMessageBox, QDialogButtonBox, QTableWidgetItem,
                               QHeaderView, QTableWidget, QComboBox, QApplication)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from battery import to_pandas, makeCurve
from separateTestDialog import SeparateTest_dialog
from cutDotsDialog import CutDots_dialog

from ui_py.ui_choose_test import Ui_ChooseFileDialog
from ui_py.ui_tests import Ui_TestsPage



class TestsPage(QWidget, Ui_TestsPage):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        
        self.battery = None
        
        self.table = TestsTable(self)   
        self.tableLayout.addWidget(self.table)
        self.canvas = TestsCanvas(self)
        self.graphLayout.addWidget(self.canvas)
        
        self.addTest_button.clicked.connect(self.add_test_dialog)
        self.delTest_button.clicked.connect(self.delete_test)
        self.separateTest_button.clicked.connect(self.separateTest)
        self.cutDots_button.clicked.connect(self.cutDots)
        self.table.testSelected.connect(self.select_test)
        self.table.typeChanged.connect(lambda: self.canvas.plotTest(self.canvas.test))
        
        
    def setBattery(self, battery):
        self.battery = battery
        self.batteryLabel.setText(f"{battery.name}")
        
        self.table.fillTests(battery)
        
        self.canvas.figure.clf()
        self.canvas.draw_idle()
        
    
    def add_test(self, df, file, testType):
        test = self.battery.addTest(df, file, testType)
        self.table.addTest(test)
        
        
    def delete_test(self):
        test_id = self.table.deleteSelected()
        self.battery.delTest(test_id)
        
        
    def add_test_dialog(self):            
        dialog = Choose_file_dialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.add_test(dialog.df, dialog.file, dialog.testType)
        dialog.deleteLater()
            
                
    def select_test(self, test_id):
        if test_id < 0:
            self.canvas.figure.clf()
            self.canvas.draw_idle()
        
        else:
            test = self.battery.tests[test_id]
            self.canvas.plotTest(test)
        
        
    def separateTest(self):
        test = self.canvas.test
        
        if test is None:
            QMessageBox.warning(self, "Испытание не выбрано",
                                "Сперва добавьте или выберите из списка выше испытание")
            return
        
        if test.testType in ["Зарядная кривая", "Разрядная кривая"]:
            QMessageBox.warning(self, "Предупреждение",
                                "Данная функция недоступна для разрядных/зарядных кривых")
            return
        
        dialog = SeparateTest_dialog(self, test)
        if dialog.exec() == QDialog.Accepted:
            self.add_test(dialog.resultDf, "-", test.testType)
        dialog.free()
        dialog.deleteLater()
    
    
    def cutDots(self):
        test = self.canvas.test
        
        if test is None:
            QMessageBox.warning(self, "Испытание не выбрано",
                                "Сперва добавьте или выберите из списка выше испытание")
            return
        
        dialog = CutDots_dialog(self, test)
        if dialog.exec() == QDialog.Accepted:
            self.add_test(dialog.resultDf, "-", test.testType)
            self.delete_test()
        dialog.free()
        dialog.deleteLater()
                   
       
       
class TestsTable(QTableWidget):
    class Column:
        header = ["id теста", "Название", "Имя файла", "Средний ток, А", "Тип испытания"]
        ID = 0
        NAME = 1
        FILE = 2
        CURRENT = 3
        COMBO_BOX = 4
        
    testSelected = Signal(int)
    typeChanged = Signal()
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setColumnCount(len(self.Column.header))
        self.setHorizontalHeaderLabels(self.Column.header)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        self.horizontalHeader().hideSection(self.Column.ID)
        
        self.itemSelectionChanged.connect(self.tableRowSelected)
        self.itemChanged.connect(self.nameChanged)
        
        
    def getTestId(self, row):
        return int(self.item(row, self.Column.ID).text())

        
    def addTest(self, test):
        self.blockSignals(True)
        
        row_position = self.rowCount()
        self.insertRow(row_position)
        self.setItem(row_position, self.Column.ID, QTableWidgetItem(f"{test.id}"))
        self.setItem(row_position, self.Column.NAME, QTableWidgetItem(test.name))
        self.setItem(row_position, self.Column.FILE, QTableWidgetItem(test.file))
        if test.testType in ["Разрядная кривая", "Зарядная кривая"]:
            self.setItem(row_position, self.Column.CURRENT, QTableWidgetItem("-"))
        else:
            self.setItem(row_position, self.Column.CURRENT, QTableWidgetItem(f"{test.df["I,A"].mean():.2f}"))
        
        
        for i in [self.Column.ID, self.Column.FILE, self.Column.CURRENT]:
            item = self.item(row_position, i)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setToolTip(item.text())
        
        testTypeComboBox = QComboBox()
        possibleTypes = test.possibleTypes()
        
        testTypeComboBox.addItems(possibleTypes)
        testTypeComboBox.setCurrentText(test.testType)
        self.setCellWidget(row_position, self.Column.COMBO_BOX, testTypeComboBox)
        
        testTypeComboBox.currentTextChanged.connect(
            lambda text, test=test, sender=testTypeComboBox: self.changeTestType(text, test, sender)
        )
        
        self.blockSignals(False)
    
        
    def fillTests(self, battery):
        self.blockSignals(True)
        self.setRowCount(0)
        self.blockSignals(False)
        for test in battery.tests.values():
            self.addTest(test)
        
        
    def changeTestType(self, text, test, sender):
        testType, message = test.setType(text)
        if message != "ok":
            QMessageBox.warning(self, "Тип испытания не установлен", message)
        
        self.blockSignals(True)
        sender.setCurrentText(testType)
        self.blockSignals(False)
        
        self.typeChanged.emit()
    
    
    def nameChanged(self, item):
        self.blockSignals(True)
        test_id = self.getTestId(item.row())
        new_name = item.text()
        accepted_name = self.parent().battery.changeTestName(test_id, new_name)
        item.setText(accepted_name)
        self.blockSignals(False)
            
            
    def tableRowSelected(self):
        current_row = self.currentRow()
        if current_row < 0:
            self.testSelected.emit(-1)
        
        else:
            test_id = self.getTestId(current_row)
            self.testSelected.emit(test_id)
                
                
    def deleteSelected(self):
        if self.currentRow() < 0:
            return -1
        
        test_id = self.getTestId(self.currentRow())
        self.removeRow(self.currentRow())
        return test_id
        
                
                
class TestsCanvas(FigureCanvas):
    def __init__(self, parent):
        super().__init__(Figure(constrained_layout=True))
        self.setParent(parent)
        
        self.test = None
        
        
    def plotTest(self, test):
        self.figure.clf()
        self.test = test
        
        if test.testType == "Исходное испытание":
            self.axs = self.figure.subplots(2)
            axs = self.axs
            axs[0].plot(test.df["Total_Time,s"], test.df["U,V"])
            axs[1].plot(test.df["Total_Time,s"], test.df["I,A"])
            axs[0].set_xlabel("Время, с")
            axs[0].set_ylabel("Напряжение, В")
            axs[1].set_xlabel("Время, с")
            axs[1].set_ylabel("Ток, А")
        
        elif test.testType in ["Разрядная кривая", "Зарядная кривая"]:
            self.axs = self.figure.subplots(1)
            axs = self.axs
            x, y, xlabel, ylabel = makeCurve(test.df)
            axs.plot(x, y)
            axs.set_xlabel(xlabel)
            axs.set_ylabel(ylabel)
            
        self.draw_idle()
          
        
            
class Choose_file_dialog(QDialog, Ui_ChooseFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.choose_button.clicked.connect(self.open_dialog)
        self.df = None
        self.file = None
        self.testType = None
        self.Ok = self.buttonBox.button(QDialogButtonBox.Ok)
        self.Ok.setEnabled(False)
        
        self.canvas = FigureCanvas(Figure(constrained_layout=True))
        layout = QVBoxLayout(self.plot_view)
        layout.addWidget(self.canvas)
    
        
    def open_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",  # начальная директория
            "Все поддерживаемые форматы (*.txt *.nda *.ndax *.csv);;"
            "Текстовые файлы (*.txt);;"
            "NDA файлы (*.nda);;"
            "NDAX файлы (*.ndax);;"
            "CSV файлы (*.csv);;"
            "Все файлы (*.*)"
        )
        
        if file_path:
            self.lineEdit.setText(file_path)
            try:
                df, testType = to_pandas(file_path)
                self.df = df
                self.file = file_path
                self.testType = testType
                
                self.canvas.figure.clear()        
                ax = self.canvas.figure.subplots()
                
                if testType == "Исходное испытание":
                    ax.plot(df["Total_Time,s"], df["U,V"])
                    ax.set_xlabel("Время, с")
                    ax.set_ylabel("Напряжение, В")
                
                elif testType in ["Разрядная кривая", "Зарядная кривая"]:
                    x, y, xlabel, ylabel = makeCurve(df)
                        
                    ax.plot(x, y)
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel)
                
                self.canvas.draw_idle()
                
                self.Ok.setEnabled(True)
                
            except Exception as e:
                QMessageBox.warning(self, "Некорректный файл", str(e))