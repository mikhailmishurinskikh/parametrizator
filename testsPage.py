from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFileDialog, QDialog,
                               QMessageBox, QDialogButtonBox, QTableWidgetItem,
                               QHeaderView, QTableWidget, QComboBox, QApplication)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory


from battery import to_pandas

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
        self.separateTest_button.clicked.connect(self.separateTest_start)
        self.table.testSelected.connect(self.select_test)
        
        
    def setBattery(self, battery):
        self.battery = battery
        self.batteryLabel.setText(f"{battery.name}")
        
        self.table.fillTests(battery)
        
        self.canvas.figure.clf()
        self.canvas.draw_idle()
        
    
    def add_test(self, df, file):
        test = self.battery.addTest(df, file)
        self.table.addTest(test)
        
        
    def delete_test(self):
        test_id = self.table.deleteSelected()
        self.battery.delTest(test_id)
        
        
    def add_test_dialog(self):            
        dialog = Choose_file_dialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.add_test(dialog.df, dialog.file)
            
                
    def select_test(self, test_id):
        if test_id < 0:
            self.canvas.figure.clf()
            self.canvas.draw_idle()
        
        else:
            test = self.battery.tests[test_id]
            self.canvas.plotTest(test)
        
        
    def separateTest_start(self):
        test = self.canvas.test
        
        if test is None:
            QMessageBox.warning(self, "Испытание не выбрано",
                                "Сперва добавьте или выберите из списка выше испытание")
            return
        
        self.separateTest_button.clicked.disconnect()
        self.separateTest_button.setText("ОК")
        self.separateTest_button.clicked.connect(lambda: self.separateTest_finish(ok=True))
        self.helpLabel.setText("Выберите одну область на графике или две граничные")
        
        QApplication.instance().installEventFilter(self)
        self.canvas.startSelection()
        
        
    def separateTest_finish(self, ok):
        if ok:
            selected = list(self.canvas.selected)
            
            if len(selected) == 0:
                QMessageBox.warning(self, "Участок не выбран", "Выберите участок на графике")
            
            elif len(selected) > 2:
                QMessageBox.warning(self, "Выбрано слишком много участков на графике",
                                    "Выберите либо один участок, либо два участка, ограничивающих область на графике")
            
            else:
                df = self.canvas.test.separateTest(selected)                
                self.add_test(df, "Нет файла")
        
        self.canvas.stopSelection()        
        QApplication.instance().removeEventFilter(self)
        self.separateTest_button.clicked.disconnect()
        self.separateTest_button.setText("Выделить выбранное в отдельное испытание")
        self.separateTest_button.clicked.connect(self.separateTest_start)
        self.helpLabel.setText("")
        
        
    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            pos = event.globalPosition().toPoint()
            widget = QApplication.widgetAt(pos)
            
            if widget != self.canvas and widget != self.separateTest_button:
                self.separateTest_finish(ok=False)
            
        elif event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.separateTest_finish(ok=True)
                return True
            
            else:
                self.separateTest_finish(ok=False)

        return super().eventFilter(watched, event)
       
       
       
class TestsTable(QTableWidget):
    class Column:
        header = ["id теста", "Название", "Имя файла", "Средний ток, А", "Тип испытания"]
        ID = 0
        NAME = 1
        FILE = 2
        CURRENT = 3
        COMBO_BOX = 4
        
    testSelected = Signal(int)
    
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
        self.setItem(row_position, self.Column.CURRENT, QTableWidgetItem(f"{test.df["I,A"].mean():.2f}"))
        
        
        for i in [self.Column.ID, self.Column.FILE, self.Column.CURRENT]:
            item = self.item(row_position, i)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setToolTip(item.text())
        
        testTypeComboBox = QComboBox()
        testTypeComboBox.addItems([
            "Исходное испытание",
            "Разрядная кривая",
            "Зарядная кривая",
            "Импульсы"
        ])
        testTypeComboBox.setCurrentText(test.testType)
        self.setCellWidget(row_position, self.Column.COMBO_BOX, testTypeComboBox)
        
        testTypeComboBox.currentTextChanged.connect(
            lambda text, test=test: self.changeTestType(text, test)
            )
        
        self.blockSignals(False)
    
        
    def fillTests(self, battery):
        self.blockSignals(True)
        self.setRowCount(0)
        self.blockSignals(False)
        for test in battery.tests.values():
            self.addTest(test)
        
        
    def changeTestType(self, text, test):
        test.testType = text
    
    
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
        super().__init__(plt.Figure())
        self.setParent(parent)
        
        self.test = None
        self.connections = []
        self.rects = {}
        self.selected = set()
        self.selected_lines = {}
        
        
    def plotTest(self, test):
        self.figure.clf()
        self.test = test
        
        self.axs = self.figure.subplots(2)
        axs = self.axs
        axs[0].plot(test.df["Total_Time,s"], test.df["U,V"])
        axs[1].plot(test.df["Total_Time,s"], test.df["I,A"])
        axs[0].set_xlabel("Время, с")
        axs[0].set_ylabel("Напряжение, В")
        axs[1].set_xlabel("Время, с")
        axs[1].set_ylabel("Ток, А")
        
        self.figure.set_tight_layout(True)
        self.draw_idle()
        
        
    def startSelection(self):
        parts = self.test.parts
        
        transform = blended_transform_factory(
            self.axs[0].transData,
            self.figure.transFigure
        )
        
        for rect_id, part in parts.items():
            t_min = part["t_min"]
            t_max = part["t_max"]
            
            rect = Rectangle(
                (t_min, 0),
                t_max - t_min,
                1,
                alpha=0.0,
                color="grey",
                picker=True,
                figure=self.figure,
                transform=transform
            )
            
            rect.rect_id = rect_id
            self.rects[rect_id] = rect
            self.figure.add_artist(rect)
            
        self.connections.append(self.mpl_connect('motion_notify_event', self.hoverEvent))
        self.connections.append(self.mpl_connect('figure_leave_event', self.leaveFigureEvent))
        self.connections.append(self.mpl_connect('pick_event', self.pickEvent))
        
        self.draw_idle()
        
        
    def stopSelection(self):
        for connection in self.connections:
            self.mpl_disconnect(connection)
        self.connections = []
        self.selected_lines = {}
        self.selected = set()
        self.rects = {}
        
        self.figure.clf()
        self.plotTest(self.test)
        
        self.draw_idle()
        
        
    def hoverEvent(self, event):
        for rect in self.rects.values():
            if rect.rect_id in self.selected:
                continue
            
            if rect.contains_point((event.x, event.y)):
                rect.set_alpha(0.2)
            else:
                rect.set_alpha(0)
        
        self.draw_idle()
        
        
    def leaveFigureEvent(self, event):
        for rect in self.rects.values():
            if rect.rect_id in self.selected:
                continue
            
            rect.set_alpha(0)
        
        self.draw_idle()
        
    
    def pickEvent(self, event):
        rect = event.artist
        if rect.rect_id in self.selected:
            rect.set_alpha(0.2)
            self.selected.remove(rect.rect_id)
            for lines in self.selected_lines[rect.rect_id]:
                for line in lines:
                    line.remove()
            
            self.selected_lines.pop(rect.rect_id)

        else:
            self.selected.add(rect.rect_id)
            df_part = self.test.getPartDf(rect.rect_id)
            
            self.selected_lines[rect.rect_id] = [
                self.axs[0].plot(df_part["Total_Time,s"], df_part["U,V"]),
                self.axs[1].plot(df_part["Total_Time,s"], df_part["I,A"])
            ]
            
        self.draw_idle()
        
        
            
class Choose_file_dialog(QDialog, Ui_ChooseFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.choose_button.clicked.connect(self.open_dialog)
        self.df = None
        self.file = None
        self.Ok = self.buttonBox.button(QDialogButtonBox.Ok)
        self.Ok.setEnabled(False)
        
        self.canvas = FigureCanvas(plt.Figure())
        layout = QVBoxLayout(self.plot_view)
        layout.addWidget(self.canvas)
    
        
    def open_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",  # начальная директория
            "Все поддерживаемые форматы (*.txt *.nda *.ndax);;"
            "Текстовые файлы (*.txt);;"
            "NDA файлы (*.nda);;"
            "NDAX файлы (*.ndax);;"
            "Все файлы (*.*)"
        )
        
        if file_path:
            self.lineEdit.setText(file_path)
            try:
                df = to_pandas(file_path)
                self.df = df
                self.file = file_path
                
                self.canvas.figure.clear()        
                ax = self.canvas.figure.subplots()
                
                ax.plot(df["Total_Time,s"], df["U,V"])
                ax.set_xlabel("Время, с")
                ax.set_ylabel("Напряжение, В")
                
                self.canvas.figure.tight_layout()
                self.canvas.draw()
                
                self.Ok.setEnabled(True)
                
            except Exception as e:
                QMessageBox.warning(self, "Некорректный файл", str(e))