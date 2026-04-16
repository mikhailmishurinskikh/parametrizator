from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from ui_py.ui_cutDots_dialog import Ui_CutDotsDialog


class CutDots_dialog(QDialog, Ui_CutDotsDialog):
    def __init__(self, parent, test):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMaximizeButtonHint
        )
        
        self.test = test
        self.resultDf = None
        
        self.canvas = CutDotsCanvas(self, self.test)
        self.graphLayout.addWidget(self.canvas)
        
        self.startInput.valueChanged.connect(self.updateDf)
        self.endInput.valueChanged.connect(self.updateDf)
        
        self.updateDf()
        
        
    def updateDf(self, value=None):
        numStart = self.startInput.value()
        numEnd = self.endInput.value()
        
        df = self.test.cutDots(numStart, numEnd)
        self.canvas.plotTest(df)
        self.resultDf = df
            
            
    def accept(self):
        if self.resultDf is None:
            QMessageBox.warning(self, "Ошибка удаления точек",
                                "Нельзя удалить все точки испытания. Выберите меньшее число точек")
            return
        
        super().accept()
        
        
    def free(self):
        self.canvas.clearAll()
        
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.updateDf()
            return
        super().keyPressEvent(event)
        
        
        
class CutDotsCanvas(FigureCanvas):
    def __init__(self, parent, test):        
        super().__init__(plt.Figure(constrained_layout=True))
        self.setParent(parent)
        self.test = test
        
        
    def plotTest(self, df):
        self.figure.clf()
        
        test = self.test
        self.axs = self.figure.subplots(2)
        axs = self.axs
        axs[0].plot(test.df["Total_Time,s"], test.df["U,V"], color="red")
        axs[1].plot(test.df["Total_Time,s"], test.df["I,A"], color="red")
        axs[0].set_xlabel("Время, с")
        axs[0].set_ylabel("Напряжение, В")
        axs[1].set_xlabel("Время, с")
        axs[1].set_ylabel("Ток, А")
        
        if df is not None:
            self.axs[0].plot(df["Total_Time,s"], df["U,V"], color="green")
            self.axs[1].plot(df["Total_Time,s"], df["I,A"], color="green")
        
        self.draw_idle()
        
        
    def clearAll(self):
        self.figure.clf()
        plt.close(self.figure)