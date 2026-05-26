class Test:
    def __init__(self, name, testType, df, test_id):
        self.df = df.reset_index(drop=True)
        self.testType = testType
        self.name = name
        
        self.id = test_id
            
            
    def getXlabel(self):
        if self.testType == "Исходное испытание":
            xlabel = "Total_Time,s"
            
        elif self.testType == "Разрядная кривая":
            xlabel = "Q,Ah"
            
        elif self.testType == "Норм. разрядная кривая":
            xlabel = "Q/m,Ah/kg"
            
        return xlabel
        
        
    def defineBorders(self):
        xlabel = self.getXlabel()
        criteria = [column for column in ["Cycle", "Step_index", "Step_type"] if column in self.df.columns]
        if not criteria:
            return [self.df[xlabel].min(), self.df[xlabel].max()]
        
        borders = set()
        grouped = self.df.groupby(criteria, observed=False)
        
        for _, group in grouped:
            borders.add(group[xlabel].min())
            borders.add(group[xlabel].max())
        
        return sorted(list(borders))
         
    
    def setParams(self, name, testType):
        self.name = name
        self.testType = testType
    
    
    def possibleTypes(self):
        result = []
        if "Total_Time,s" in self.df:
            result.append("Исходное испытание")
        if "Q,Ah" in self.df:
            result.append("Разрядная кривая")
        if "Q/m,Ah/kg" in self.df:
            result.append("Норм. разрядная кривая")
            
        return result



class Battery:
    def __init__(self, name, numCells, mass):
        self.setParams(name, numCells, mass)
        self.tests = {}
        self.test_counter = 0
        
        
    def addTest(self, name, testType, df):
        test = Test(name, testType, df, self.test_counter)
        self.tests[self.test_counter] = test
        self.test_counter += 1
        return test
    
    
    def delTest(self, test_id):
        self.tests.pop(test_id, None)
    
    
    def testNames(self):
        return [test.name for test in self.tests.values() if test]
        
        
    def getTest(self, test_id):
        return self.tests[test_id]
        
        
    def setParams(self, name, numCells, mass):
        self.name = name
        self.numCells = numCells
        self.mass = mass
        
    
    def testsList(self):
        return list(self.tests.values())
    
    
    def testCount(self):
        return len(self.tests)



class BatteriesManager:
    def __init__(self):
        self.batteries = {}
        self.batteries_counter = 0
        
        
    def delete(self, battery_id):
        self.batteries.pop(battery_id, None)
        
        
    def addBattery(self, battery):
        self.batteries[self.batteries_counter] = battery
        self.batteries_counter += 1
        
        
    def add(self, name, numCells, mass):
        battery = Battery(name, numCells, mass)
        self.addBattery(battery)
        return battery
        
        
    def get(self, battery_id):
        return self.batteries[battery_id]
    
    
    def names(self):
        return [battery.name for battery in self.batteries.values()]
    
    
    def curves(self):
        curves = []
        for battery in self.batteries.values():
            curves += [
                (battery, test) for test in battery.tests.values()
                if test.testType in ["Разрядная кривая", "Норм. разрядная кривая"]
            ]
        return curves
    
    
    def batteriesList(self):
        return list(self.batteries.values())
    
    
    def ids(self):
        return self.batteries.keys()
    
    
    def clear(self):
        self.batteries.clear()
        self.batteries_counter = 0



def calcQ(test, battery, xlabel, ylabel=None):
    if xlabel == "Q":
        if test.testType == "Разрядная кривая":
            x = test.df["Q,Ah"]
        
        elif test.testType == "Норм. разрядная кривая":
            x = test.df["Q/m,Ah/kg"] * (battery.mass / 1000) / battery.numCells

    elif xlabel == "Q/m":
        if test.testType == "Разрядная кривая":
            x = (test.df["Q,Ah"] / (battery.mass / 1000)).abs() * battery.numCells
        
        elif test.testType == "Норм. разрядная кривая":
            x = test.df["Q/m,Ah/kg"]
            
    if ylabel is None: return x

    if ylabel == "V общее":
        if test.testType == "Разрядная кривая":
            y = test.df["U,V"]
        
        elif test.testType == "Норм. разрядная кривая":
            y = test.df["Ucell,V"] * battery.numCells

    elif ylabel == "V на аккум.":
        if test.testType == "Разрядная кривая":
            y = test.df["U,V"] / battery.numCells
            
        elif test.testType == "Норм. разрядная кривая":
            y = test.df["Ucell,V"]
            
    return x, y


def calcWh(test, battery, xlabel):
    if xlabel == "Q":
        if "W,Wh" in test.df.columns:
            x = f"{test.df['W,Wh'].max():.2f}"
            
        else:
            x = "-"
            
    elif xlabel == "Q/m":
        if "W,Wh" in test.df.columns:
            x = f"{test.df['W,Wh'].max() / (battery.mass/1000):.2f}"
            
        else:
            x = "-"
    
    return x