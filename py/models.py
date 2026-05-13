from battery import BATTERY_COLUMNS, TEST_COLUMNS
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


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
        
        self.batteries = self.batteriesManager.sort(column, (order == Qt.DescendingOrder))
        self.layoutChanged.emit()
    
    
    def refresh(self):
        self.beginResetModel()
        self.batteries = self.batteriesManager.sort(
            self.sortColumn, (self.sortOrder == Qt.DescendingOrder)
        )
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