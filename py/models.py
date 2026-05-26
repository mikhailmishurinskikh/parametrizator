from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from battery import calcQ, calcWh


class BATTERY_COLUMNS:
    NAME = 0
    NUM_CELLS = 1
    MASS = 2
    
    NCOLS = 3
    HEADERS = ["Имя батареи", "Число аккумуляторов", "Масса, г"]
    
    
class TEST_COLUMNS:
    NAME = 0
    TYPE = 1
    
    NCOLS = 2
    HEADERS = ["Имя испытания", "Тип испытания"]
    
    
class CURVES_COLUMNS:
    BATTERY = 0
    NAME = 1
    TYPE = 2
    CAPACITY = 3
    ENERGY_CAPACITY = 4
    LABEL = 5
    
    NCOLS = 6
    HEADERS = {
        "Q" : ["Батарея", "Испытание", "Тип кривой", "Емкость, Ач", "Энергоемкость, Вт ч", "Имя в легенде"],
        "Q/m" : ["Батарея", "Испытание", "Тип кривой", "Уд. емкость, Ач/кг", "Уд. энергоемкость, Вт ч/кг", "Имя в легенде"]
    }



class BatteriesModel(QAbstractTableModel):
    def __init__(self, batteries_manager):
        super().__init__()
        self.batteriesManager = batteries_manager
        
        self.sortColumn = BATTERY_COLUMNS.NAME
        self.sortOrder = Qt.SortOrder.DescendingOrder
        
        self.refresh()
        
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.batteries)
    
    
    def columnCount(self, parent=QModelIndex()):
        return BATTERY_COLUMNS.NCOLS
    
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role != Qt.DisplayRole:
            return None
        
        row, col = index.row(), index.column()
        
        battery = self.batteries[row]
        
        if col == BATTERY_COLUMNS.NAME:
            return battery.name
        elif col == BATTERY_COLUMNS.NUM_CELLS:
            return f"{battery.numCells}"
        elif col == BATTERY_COLUMNS.MASS:
            return f"{battery.mass:.2f}"
        
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        
        if orientation == Qt.Orientation.Horizontal:
            headers = BATTERY_COLUMNS.HEADERS
            return headers[section] if section < len(headers) else None
        
        
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    
    def getId(self, row):
        return self.batteries[row].id
    
    
    def sort(self, column, order):        
        self.sortColumn = column
        self.sortOrder = order
        
        batteriesList = self.batteriesManager.batteriesList()
        reverse = (order == Qt.DescendingOrder)
        
        if column == BATTERY_COLUMNS.NAME:
            self.batteries =  sorted(batteriesList,
                          key=lambda battery: battery.name,
                          reverse=reverse)
        elif column == BATTERY_COLUMNS.NUM_CELLS:
            self.batteries = sorted(batteriesList,
                          key=lambda battery: battery.numCells,
                          reverse=reverse)
        elif column == BATTERY_COLUMNS.MASS:
            self.batteries = sorted(batteriesList,
                          key=lambda battery: battery.mass,
                          reverse=reverse)
        
        self.layoutChanged.emit()
    
    
    def refresh(self):
        self.beginResetModel()
        self.batteries = self.batteriesManager.batteriesList()
        self.sort(self.sortColumn, self.sortOrder)
        self.endResetModel()
        
        
        
class TestsModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.battery = None
        self.tests = []
        
    
    def setBattery(self, battery):
        self.battery = battery
        self.refresh()
        
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.tests)
    
    
    def columnCount(self, parent=QModelIndex()):
        return TEST_COLUMNS.NCOLS
    
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role != Qt.DisplayRole:
            return None
        
        row, col = index.row(), index.column()
        test = self.tests[row]
        
        if col == TEST_COLUMNS.NAME:
            return test.name
        elif col == TEST_COLUMNS.TYPE:
            return test.testType
        
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        
        if orientation == Qt.Orientation.Horizontal:
            headers = TEST_COLUMNS.HEADERS
            return headers[section] if section < len(headers) else None
        
    
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    
    def getId(self, row):
        return self.tests[row].id
    
    
    def refresh(self):
        self.beginResetModel()
        self.tests = list(self.battery.tests.values())
        self.endResetModel()
        
        
        
class CurvesModel(QAbstractTableModel):
    def __init__(self, manager, xlabel):
        super().__init__()
        
        self.sortColumn = CURVES_COLUMNS.BATTERY
        self.sortOrder = Qt.SortOrder.DescendingOrder
        
        self.batteriesManager = manager
        self.curves = []
        self.xlabel = xlabel
        
        self.labels = {}
        self.selectedTests = set()
        
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.curves)
    
    
    def columnCount(self, parent=QModelIndex()):
        return CURVES_COLUMNS.NCOLS
            
            
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        row, col = index.row(), index.column()
        battery, test = self.curves[row]
        
        if role == Qt.DisplayRole:
            if col == CURVES_COLUMNS.BATTERY:
                return battery.name
            elif col == CURVES_COLUMNS.NAME:
                return test.name
            elif col == CURVES_COLUMNS.TYPE:
                return test.testType
            elif col == CURVES_COLUMNS.CAPACITY:
                return f"{calcQ(test, battery, self.xlabel).max():.2f}"
            elif col == CURVES_COLUMNS.ENERGY_CAPACITY:
                return calcWh(test, battery, self.xlabel)
            elif col == CURVES_COLUMNS.LABEL:
                if (battery, test) in self.labels.keys():
                    return self.labels[(battery, test)]
                else:
                    return "По умолч."
        
        elif role == Qt.CheckStateRole:
            if col == CURVES_COLUMNS.BATTERY:
                return Qt.Checked if self.curves[row] in self.selectedTests else Qt.Unchecked
            return None
        
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        
        if orientation == Qt.Orientation.Horizontal:
            headers = CURVES_COLUMNS.HEADERS[self.xlabel]
            return headers[section] if section < len(headers) else None
        
        
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
        if index.column() == CURVES_COLUMNS.BATTERY:
            flags |= Qt.ItemIsUserCheckable
            
        if index.column() == CURVES_COLUMNS.LABEL:
            flags |= Qt.ItemIsEditable
        
        return flags
    
    
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        
        if index.column() == CURVES_COLUMNS.BATTERY and role == Qt.CheckStateRole:
            row = index.row()
            
            if Qt.CheckState(value) == Qt.Checked:
                self.selectedTests.add(self.curves[row])
            else:
                self.selectedTests.discard(self.curves[row])
            
            self.dataChanged.emit(index, index)
            return True
        
        if index.column() == CURVES_COLUMNS.LABEL and role == Qt.EditRole:
            self.labels[self.curves[index.row()]] = value
            return True
        
        return False
    
    
    def setXlabel(self, xlabel):
        self.beginResetModel()
        self.xlabel = xlabel
        self.endResetModel()
        
        
    def getSelected(self):
        return list(self.selectedTests)
    
    
    def sort(self, column, order):        
        self.sortColumn = column
        self.sortOrder = order
        
        reverse = (order == Qt.DescendingOrder)
        
        if column == CURVES_COLUMNS.BATTERY:
            self.curves = sorted(self.curves,
                            key=lambda item: item[0].name,
                            reverse=reverse)
        elif column == CURVES_COLUMNS.NAME:
            self.curves = sorted(self.curves,
                            key=lambda item: item[1].name,
                            reverse=reverse)
        elif column == CURVES_COLUMNS.TYPE:
            self.curves = sorted(self.curves,
                            key=lambda item: item[1].testType,
                            reverse=reverse)
        elif column == CURVES_COLUMNS.CAPACITY:
            self.curves = sorted(self.curves,
                            key=lambda item: calcQ(item[1], item[0], self.xlabel).max(),
                            reverse=reverse)        
        elif column == CURVES_COLUMNS.ENERGY_CAPACITY:
            self.curves = sorted(self.curves,
                            key=self.sortWhKey,
                            reverse=reverse)
        else: return
        
        self.layoutChanged.emit()
        
        
    def sortWhKey(self, item):
        battery = item[0]
        test = item[1]
        
        Wh_str = calcWh(test, battery, self.xlabel)
        if Wh_str == "-":
            return -1
        else:
            return float(Wh_str)
        
        
    def setCheck(self, index):
        checkItem = self.index(index.row(), CURVES_COLUMNS.BATTERY)
        state = Qt.CheckState(checkItem.data(Qt.CheckStateRole)) == Qt.Checked
        newState = Qt.Unchecked if state else Qt.Checked
        self.setData(checkItem, newState, Qt.CheckStateRole)
        
        
    def selectAll(self):
        for row in range(self.rowCount()):
            index = self.index(row, CURVES_COLUMNS.BATTERY)
            self.setData(index, Qt.Checked, Qt.CheckStateRole)
            
            
    def deselectAll(self):
        self.beginResetModel()
        self.labels = {}
        for row in range(self.rowCount()):
            index = self.index(row, CURVES_COLUMNS.BATTERY)
            self.setData(index, Qt.Unchecked, Qt.CheckStateRole)
        self.endResetModel()
            
            
    def showChecked(self):
        self.beginResetModel()
        self.curves = [item for item in self.curves if item in self.selectedTests]
        self.sort(self.sortColumn, self.sortOrder)
        self.endResetModel()
        
        
    def refresh(self):
        self.beginResetModel()
        self.labels = {}
        self.curves = self.batteriesManager.curves()
        self.sort(self.sortColumn, self.sortOrder)
        self.endResetModel()