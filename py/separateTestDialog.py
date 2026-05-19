from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import QDialog, QMessageBox
import pyqtgraph as pg

import validate

from ui_py.ui_separateTest_dialog import Ui_SeparateTest_dialog



class SeparateTest_dialog(QDialog, Ui_SeparateTest_dialog):
    def __init__(self, parent, test):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMaximizeButtonHint
        )
        
        self.test = test
        
        self.xlabel = self.test.getXlabel()
        self.graphicsView.plot(self.test.testType, self.test.df)
        
        self.linesEnable = self.test.df[self.test.getXlabel()].is_monotonic_increasing
        
        if self.linesEnable:
            self.lines = Lines(self, self.test)
            self.lines.addItems(self.graphicsView.plotItem)
            
            self.lines.cutDots.connect(self.updateSpinBox)
            self.continious_checkBox.toggled.connect(self.setContinuous)
            self.continious_checkBox.setChecked(True)
            
        else:
            self.continious_checkBox.setEnabled(False)
            QMessageBox.warning(self, "Возможности ограничены", "Значения по оси x не являются монотонно возрастающими\n"
                                "Ограничительные линии недоступны. Можно использовать удаление точек с начала и с конца")
        
        self.rightSpinBox.valueChanged.connect(self.cutDots)
        self.leftSpinBox.valueChanged.connect(self.cutDots)
        
        self.new_checkBox.toggled.connect(lambda check: self.nameInput.setEnabled(check))
        self.nameInput.setEnabled(self.new_checkBox.isChecked())
            
            
    def setContinuous(self, continuous):
        self.lines.continuous = continuous
        self.rightSpinBox.setEnabled(continuous)
        self.leftSpinBox.setEnabled(continuous)
            
            
    def updateSpinBox(self, leftPos, rightPos):
        left, right = self.findLeftRightDots(leftPos, rightPos)
        self.blockSignals(True)
        
        self.leftSpinBox.setValue(left)
        self.rightSpinBox.setValue(right)
        
        self.setMaximumsSB(left, right)
        
        self.blockSignals(False)
        
        self.greyPlot(left, right)
        
        
    def greyPlot(self, left, right):
        dfs = []
        
        if left:
            dfs.append(self.test.df.iloc[:left+1].reset_index())
        if right:
            dfs.append(self.test.df.iloc[-right:].reset_index())
        
        self.graphicsView.greyPlot(dfs)
        
    
    def findLeftRightDots(self, leftPos, rightPos):
        left = len(self.test.df[self.test.df[self.xlabel] < leftPos])
        right = len(self.test.df[self.test.df[self.xlabel] > rightPos])
        return left, right
        
        
    def setMaximumsSB(self, left, right):
        self.rightSpinBox.setMaximum(len(self.test.df) - left - 1)
        self.leftSpinBox.setMaximum(len(self.test.df) - right - 1)
        
        
    def cutDots(self, _):
        left = self.leftSpinBox.value()
        right = self.rightSpinBox.value()
        
        self.setMaximumsSB(left, right)
        
        self.greyPlot(left, right)
        
        if self.linesEnable:
            newLeft = self.test.df.iloc[left][self.xlabel]
            newRight = self.test.df.iloc[-(right + 1)][self.xlabel]
            self.lines.setLines(newLeft, newRight)
            
    
    def separateTest(self):
        right = self.rightSpinBox.value()
        left = self.leftSpinBox.value()
        
        df = self.test.df
        if left:
            df = df.iloc[left:]
        if right:
            df = df.iloc[:(-right)]
            
        df = df.copy()
        
        if self.xlabel == "Total_Time,s":
            df[self.xlabel] = df[self.xlabel] - df[self.xlabel].min()
        return df.reset_index(drop=True)
        
        
    def accept(self):
        resultDf = self.separateTest()
        if len(resultDf) < 3:
            QMessageBox.warning(self, "Неправильное выделение", "Область выделения включает менее трех точек")
            return
        
        name = self.nameInput.text()
        new = self.new_checkBox.isChecked()
        
        if new:
            message = validate.TEST_NAME(name, self.parent().battery)
        else:
            message = "ok"
        
        if message == "ok":
            self.name = name
            self.new = new
            self.resultDf = resultDf
            super().accept()
            
        else:
            QMessageBox.warning(self, "Недопустимое название", message)
            return
    
        
    
class Lines(QObject):
    cutDots = Signal(float, float)
    
    def __init__(self, parent, test):
        super().__init__(parent)
        
        self.borders = test.defineBorders()
        
        self.initLine()
        
        self.continuous = False
        
        
    def initLine(self):
        self.leftLine = pg.InfiniteLine(
            pos=self.borders[0],
            pen=pg.mkPen(color="black", width=3),
            hoverPen=pg.mkPen(color='#FF0000', width=4),
            movable=True
        )
        
        self.rightLine = pg.InfiniteLine(
            pos=self.borders[-1],
            pen=pg.mkPen(color="black", width=3),
            hoverPen=pg.mkPen(color='#FF0000', width=4),
            movable=True
        )
        
        self.region = pg.LinearRegionItem(
            values=(self.borders[0], self.borders[-1]),
            brush=pg.mkBrush(100, 100, 255, 50),
            movable=False
        )
        
        self.leftLine.sigPositionChanged.connect(self.moveLines)
        self.rightLine.sigPositionChanged.connect(self.moveLines)      
            
            
    def moveLines(self):        
        leftPos = self.leftLine.value()
        rightPos = self.rightLine.value()
        
        if not self.continuous:
            leftPos = self.find_nearest(leftPos)
            rightPos = self.find_nearest(rightPos)
        
        newLeft = min(leftPos, rightPos)
        newRight = max(leftPos, rightPos)
        
        newLeft = max(newLeft, self.borders[0])
        newRight = min(newRight, self.borders[-1])
        
        self.setLines(newLeft, newRight)
        
        self.cutDots.emit(leftPos, rightPos)
        
        
    def find_nearest(self, pos):
        return self.borders[min(range(len(self.borders)), 
                  key=lambda i: abs(self.borders[i] - pos))]
        
        
    def setLines(self, newLeft, newRight):
        self.leftLine.blockSignals(True)
        self.rightLine.blockSignals(True)
        self.region.blockSignals(True)
        
        self.leftLine.setPos(newLeft)
        self.rightLine.setPos(newRight)
        self.region.setRegion((newLeft, newRight))
        
        self.leftLine.blockSignals(False)
        self.rightLine.blockSignals(False)
        self.region.blockSignals(False)
        
        
    def addItems(self, plotItem):
        self.plotItem = plotItem
        plotItem.addItem(self.region)
        plotItem.addItem(self.leftLine)
        plotItem.addItem(self.rightLine)
        
        
    def deleteLater(self):
        self.leftLine.sigPositionChanged.disconnect(self.moveLines)
        self.rightLine.sigPositionChanged.disconnect(self.moveLines)
        
        self.plotItem.removeItem(self.region)
        self.plotItem.removeItem(self.leftLine)
        self.plotItem.removeItem(self.rightLine)
        
        self.region.deleteLater()
        self.leftLine.deleteLater()
        self.rightLine.deleteLater()
        
        self.plotItem = None
        super().deleteLater()