from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory


from ui_py.ui_separateTest_dialog import Ui_SeparateTest_dialog


class SeparateTest_dialog(QDialog, Ui_SeparateTest_dialog):
    def __init__(self, parent, test):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMaximizeButtonHint
        )
        
        self.test = test
        self.resultDf = None
        
        self.canvas = SeparateTestCanvas(self, self.test)
        self.graphLayout.addWidget(self.canvas)
        self.canvas.startSelection()
    
    
    def free(self):
        self.canvas.clearAll()
        
        
    def accept(self):
        selected = list(self.canvas.selected)
        
        if len(selected) == 0:
            QMessageBox.warning(self, "Участок не выбран", "Выберите участок на графике")
        
        elif len(selected) > 2:
            QMessageBox.warning(self, "Выбрано слишком много участков на графике",
                                "Выберите либо один участок, либо два участка, ограничивающих область на графике")
        
        else:
            df = self.test.separateTest(selected)                
            self.resultDf = df
            super().accept()
    

class SeparateTestCanvas(FigureCanvas):
    def __init__(self, parent, test):        
        super().__init__(plt.Figure())
        self.setParent(parent)
        self.test = test
        
        
    def startSelection(self):       
        self.selected = set()
        self.selected_lines = {}
        self.rects = {}
        
        self.plotTest()
        self.plotPartsRects()
        
        self.connections = [
            self.mpl_connect('motion_notify_event', self.hoverEvent),
            self.mpl_connect('figure_leave_event', self.leaveFigureEvent),
            self.mpl_connect('pick_event', self.pickEvent)
        ]
        
        self.draw_idle()
        
        
    def plotTest(self):
        test = self.test
        self.axs = self.figure.subplots(2)
        axs = self.axs
        axs[0].plot(test.df["Total_Time,s"], test.df["U,V"])
        axs[1].plot(test.df["Total_Time,s"], test.df["I,A"])
        axs[0].set_xlabel("Время, с")
        axs[0].set_ylabel("Напряжение, В")
        axs[1].set_xlabel("Время, с")
        axs[1].set_ylabel("Ток, А")
        
        
    def plotPartsRects(self):
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
        
        
    def clearAll(self):
        for connection in self.connections:
            self.mpl_disconnect(connection)
            
        self.figure.clf()
        plt.close(self.figure)