import pyqtgraph as pg


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
        for plot in self.greyPlots["left"]:
            self.removeItem(plot)
        for plot in self.greyPlots["right"]:
            self.right_vb.removeItem(plot)
        
        self.greyPlots = {"left" : [], "right" : []}
        
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
        
        self.greyPlots = []
        
        for df in dfs:
            self.greyPlots.append(
                self.plot(
                    df["Q,Ah"],
                    df["U,V"],
                    pen=pg.mkPen(color='grey', width=2)
                )
            )
        

    
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
        
        self.greyPlots = []
        
        for df in dfs:
            self.greyPlots.append(
                self.plot(
                    df["Q/m,Ah/kg"],
                    df["Ucell,V"],
                    pen=pg.mkPen(color='grey', width=2)
                )
            )
        
        
def makeCurve(testType):
    if testType == "Исходное испытание":
        curve = TimeVoltageCurrentPlotItem()
        
    elif testType == "Разрядная кривая":
        curve = CurvePlotItem()
        
    elif testType == "Норм. разрядная кривая":
        curve = NormCurvePlotItem()
        
    return curve