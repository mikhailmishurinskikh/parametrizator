import pandas as pd
from pathlib import Path
import fastnda


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
    
    
    def curves(self):
        curves = {}
        for battery in self.batteries.values():
            batteryCurves = {"tests" : {}, "battery" : battery}
            for test in battery.tests.values():
                if test.testType in ["Разрядная кривая", "Зарядная кривая"]:
                    batteryCurves["tests"][test.id] = test
            
            curves[battery.id] = batteryCurves
        return curves
    
    
    
def to_pandas(file : str):
    """
    На вход получаем путь к файлу испытаний в txt или ndax(nda) формате.
    
    На выход pd.DataFrame со стандартными столбцами
    columns = ['Time,s', 'U,V', 'I,A', 'Q,Ah', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
    
    None в случае ошибки и сообщение об ошибке
    """
    
    def find_header(file):
        with open(file, "r", encoding="cp1251") as f:
            n = 0
            while True:
                line = f.readline()
                if "Cycle" in line and "Time,s" in line:
                    return n
                n += 1
                if n > 50:
                    raise ValueError("Не найдена шапка таблицы в файле (Cycle)")
            
            
    columns = ['Time,s', 'U,V', 'I,A', 'Q,Ah', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
    extension = Path(file).suffix
    if extension in [".ndax", ".nda"]:
        data = fastnda.read(file)
        data = data.to_pandas()
        
        required_cols = ["cycle_count", "step_index", "step_type", "voltage_V", "current_mA", "step_time_s", "total_time_s", "capacity_mAh"]
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"В файле {file} нет одного из столбцов {required_cols}")
        
        data["Cycle"] = data["cycle_count"]
        data["Step_index"] = data["step_index"]
        data["Step_type"] = data["step_type"]
        data["U,V"] = data["voltage_V"]
        data["I,A"] = data["current_mA"] / 1000
        data["Time,s"] = data["step_time_s"]
        data["Total_Time,s"] = data["total_time_s"]
        data["Q,Ah"] = data["capacity_mAh"] / 1000
        data = data[columns]
        
        
    elif extension == ".txt":
        data = pd.read_csv(
            file,
            sep=r'\s+',
            skiprows=find_header(file),
            encoding="cp1251"
        )
        
        required_cols = ["Time,s", "U,V", "I,A", "Q,Ah", "Step", "Cycle"]
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"В файле {file} нет одного из столбцов {required_cols}")
        
        if data.iloc[-1].isna().sum() > 1:
            data = data.iloc[:-1]
        data[["Time,s", "U,V", "I,A", "Q,Ah"]] = data[["Time,s", "U,V", "I,A", "Q,Ah"]].astype(float)
        
        data['Total_Time,s'] = data['Time,s'] + data.groupby('Step', sort=False)['Time,s'].max().shift().fillna(0).cumsum().loc[data['Step']].values
        data["Total_Time,s"] -= data["Total_Time,s"].min()
        
        data[['Step_index', 'Step_type']] = data['Step'].str.extract(r'^(\d*\.?\d*)([A-Za-z]*)')
        data[["Step_index", "Cycle"]] = data[["Step_index", "Cycle"]].astype(int)
        data.loc[data["Step_type"] == "DCCC", "Step_type"] = "CC Dchg"
        data.loc[data["Step_type"] == "RLAX", "Step_type"] = "Rest"
        data.loc[data["Step_type"] == "CHCC", "Step_type"] = "CC Chg"
        data.loc[data["Step_type"] == "CHCV", "Step_type"] = "CV Dchg"
        data = data[columns]
    
    
    else:
        raise ValueError(f"Файл {file} не имеет нужного расширения")
        
    return data