import pandas as pd


class Test:
    def __init__(self, df, file, counter):
        self.df = df
        self.file = file
        self.testType = "Исходное испытание"
        self.name = f"Испытание {counter}"
        self.id = counter
        self.parts = {}
        self.defineParts()
        
        
    def defineParts(self):
        parts = []
        borders = set()
        
        grouped = self.df.groupby(["Cycle", "Step_index", "Step_type"], observed=False)
        
        for (cycle, step, step_type), group in grouped:
            borders.add(group["Total_Time,s"].min())
            borders.add(group["Total_Time,s"].max())
        
        borders = sorted(list(borders))
        
        for i in range(len(borders) - 1):
            parts.append({
                "t_min": borders[i],
                "t_max": borders[i + 1]
            })
        
        parts.sort(key=lambda x: x["t_min"])
        for i, part in enumerate(parts):
            self.parts[i] = part

        
    def getPartDf(self, rect_id):
        time = self.df["Total_Time,s"]
        return self.df[(time >= self.parts[rect_id]["t_min"]) &
                       (time <= self.parts[rect_id]["t_max"])]
                
                
    def separateTest(self, selected):
        if len(selected) == 1:
            df = self.getPartDf(selected[0]).copy()
        elif len(selected) == 2:
            df = pd.DataFrame()
            for i in range(min(selected), max(selected)+1):
                df = pd.concat((df, self.getPartDf(i)))
        
        df["Total_Time,s"] = df["Total_Time,s"] - df["Total_Time,s"].min()
        return df



class Battery:
    def __init__(self, name, numCells, mass, battery_id):
        self.id = battery_id
        self.name = name
        self.numCells = numCells
        self.mass = mass
        self.tests = {}
        self.test_counter = 0
        
        
    def addTest(self, df, file):
        test = Test(df, file, self.test_counter)
        self.tests[self.test_counter] = test
        self.test_counter += 1
        return test
    
    
    def testNames(self):
        return [test.name for test in self.tests.values()]
    
    
    def changeTestName(self, test_id, name):
        test = self.tests[test_id]
        if name not in self.testNames() and name:
            test.name = name
        return test.name


    def delTest(self, test_id):
        if test_id < 0:
            return
        self.tests.pop(test_id)
        
        
    def changeParams(self, param, value):
        if param == "Название":
            pass
        
        
    def setParams(self, name, numCells, mass):
        self.name = name
        self.numCells = numCells
        self.mass = mass



class BatteriesManager:
    def __init__(self):
        self.batteries = {}
        self.batteries_counter = 0
        
        
    def delete(self, battery_id):
        self.batteries.pop(battery_id, None)
        
        
    def add(self, name, numCells, mass):
        battery = Battery(name, numCells, mass, self.batteries_counter)
        self.batteries[self.batteries_counter] = battery
        self.batteries_counter += 1
        return battery
        
        
    def get(self, battery_id):
        return self.batteries[battery_id]
    
    
    def names(self):
        return [battery.name for battery in self.batteries.values()]