import pyqtgraph as pg
from PySide6.QtWidgets import QSizePolicy



class PlotView(pg.GraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.plotItem = None
        
        
    def plot(self, testType, df):
        self.clear()
        if testType == "Исходное испытание":
            self.plotItem = TimeVoltageCurrentPlotItem()
            
        elif testType == "Разрядная кривая":
            self.plotItem = CurvePlotItem()
            
        elif testType == "Норм. разрядная кривая":
            self.plotItem = NormCurvePlotItem()
        
        self.plotItem.plotDf(df)
        self.setCentralItem(self.plotItem)
        
        
    def greyPlot(self, dfs):
        self.plotItem.greyPlot(dfs)
        
        
    def clear(self):
        if self.plotItem:
            self.plotItem.close()
            self.plotItem = None
            
    
    def deleteLater(self):
        self.clear()
        return super().deleteLater()



class TimeVoltageCurrentPlotItem(pg.PlotItem):
    def __init__(self):
        super().__init__()

        self.setMenuEnabled(False)
        
        self.showAxis('right')
        self.showGrid(x=True, y=True, alpha=0.3)
        
        self.setLabel('bottom', 'Время, с')
        self.setLabel('left', 'Ток, А', color='red')
        self.setLabel('right', 'Напряжение, В', color="blue")
        
        self.greyPlots = {"left" : [], "right" : []}
        
        
    def plotDf(self, df):
        self.right_vb = pg.ViewBox()
        self.right_vb.setParentItem(self)
        self.right_vb.setParent(self)
        self.getAxis('right').linkToView(self.right_vb)
        self.right_vb.setXLink(self.getViewBox())
        self.getViewBox().sigResized.connect(self.update_right_vb)
        self.sigRangeChanged.connect(self.update_right_vb)
        self.right_vb.setMenuEnabled(False)
        
        self.plot(
            df["Total_Time,s"].values,
            df["I,A"].values,
            pen=pg.mkPen(color='r', width=2)
        )
        
        curve = pg.PlotCurveItem(
            df["Total_Time,s"].values,
            df["U,V"].values,
            pen=pg.mkPen(color='b', width=2)
        )
        self.right_vb.addItem(curve)
        
        self.update_right_vb()
        
    
    def update_right_vb(self):
        sceneRect = self.getViewBox().sceneBoundingRect()
        self.right_vb.setGeometry(sceneRect)
        self.right_vb.linkedViewChanged(self.getViewBox(), self.right_vb.XAxis)
        
        
    def greyPlot(self, dfs):
        self.clearGreyPlots()
        
        for df in dfs:
            self.greyPlots["left"].append(
                self.plot(
                    df["Total_Time,s"].values,
                    df["I,A"].values,
                    pen=pg.mkPen(color='grey', width=2)
                )
            )
            
            curve = pg.PlotCurveItem(
                df["Total_Time,s"].values,
                df["U,V"].values,
                pen=pg.mkPen(color='grey', width=2)
            )
            self.right_vb.addItem(curve)
            self.greyPlots["right"].append(curve)
            
            
    def clearGreyPlots(self):
        for plot in self.greyPlots["left"]:
            plot.clear()
            self.removeItem(plot)
            plot.deleteLater()
        for plot in self.greyPlots["right"]:
            plot.clear()
            self.right_vb.removeItem(plot)
            plot.deleteLater()
        
        self.greyPlots = {"left" : [], "right" : []}
            
            
    def close(self):
        self.getViewBox().sigResized.disconnect(self.update_right_vb)
        self.sigRangeChanged.disconnect(self.update_right_vb)
        self.clearGreyPlots()
        self.right_vb.close()
        self.removeItem(self.right_vb)
        self.right_vb = None
        super().close()
                
        

class CurvePlotItem(pg.PlotItem):
    def __init__(self):
        super().__init__()
        
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setMenuEnabled(False)
        
        self.greyPlots = []
        
        
    def plotDf(self, df):
        self.setLabel('bottom', "Емкость, Ач")
        self.setLabel('left', "Напряжение, В")
        
        self.plot(
            df["Q,Ah"],
            df["U,V"],
            pen=pg.mkPen(color='m', width=2)
        )
        
        
    def greyPlot(self, dfs):
        for plot in self.greyPlots:
            self.removeItem(plot)
            plot.deleteLater()
        
        self.greyPlots = []
        
        for df in dfs:
            self.greyPlots.append(
                self.plot(
                    df["Q,Ah"],
                    df["U,V"],
                    pen=pg.mkPen(color='grey', width=2)
                )
            )
            
            
    def close(self):
        for plot in self.greyPlots:
            self.removeItem(plot)
            plot.deleteLater()
        super().close()
        

    
class NormCurvePlotItem(pg.PlotItem):
    def __init__(self):
        super().__init__()
        
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setMenuEnabled(False)
        
        self.greyPlots = []
        
        
    def plotDf(self, df):
        self.setLabel('bottom', "Удельная емкость, Ач/кг")
        self.setLabel('left', "Напряжение на 1 акк.")
        
        self.plot(
            df["Q/m,Ah/kg"],
            df["Ucell,V"],
            pen=pg.mkPen(color='m', width=2)
        )
        
        
    def greyPlot(self, dfs):
        for plot in self.greyPlots:
            self.removeItem(plot)
            plot.deleteLater()
        
        self.greyPlots = []
        
        for df in dfs:
            self.greyPlots.append(
                self.plot(
                    df["Q/m,Ah/kg"],
                    df["Ucell,V"],
                    pen=pg.mkPen(color='grey', width=2)
                )
            )
            
            
    def close(self):
        for plot in self.greyPlots:
            self.removeItem(plot)
            plot.deleteLater()
            
        super().close()