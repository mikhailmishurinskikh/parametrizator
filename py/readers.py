import fastnda
import pandas as pd
from pathlib import Path



def read(file, filter):
    extension = Path(file).suffix
    if extension in [".ndax", ".nda"]:
        message, data, testType = ndax(file)
        
    elif extension == ".txt":
        message, data, testType = txt(file)
    
    elif extension == ".csv" and filter == "Нормированные кривые из таблицы учета (*.csv)":
        message, data, testType = normCurves(file)
    
    elif extension == ".csv" and filter == "Стандартные CSV файлы (*.csv)":
        message, data, testType = stdCsv(file)
        
    elif extension == ".csv" and filter == "CSV со столбцами NDAX (*.csv)":
        message, data, testType = csvNdax(file)
    
    elif extension == ".xlsx":
        message, data, testType = xlsx(file)
        
    else:
        message = f"Файл {file} не имеет нужного расширения"
        data, testType = None, None
    
    return message, data, testType


def ndax(file):
    try:
        columns = ['U,V', 'I,A', 'Q,Ah', 'W,Wh', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
        data = fastnda.read(file)
        data = data.to_pandas()
        testType = "Исходное испытание"
        
        required_cols = ["cycle_count", "step_index", "step_type", "voltage_V", "current_mA", "step_time_s", "total_time_s", "capacity_mAh", "energy_mWh"]
        
        if all(col in data.columns for col in required_cols):   
            data["Cycle"] = data["cycle_count"]
            data["Step_index"] = data["step_index"]
            data["Step_type"] = data["step_type"]
            data["U,V"] = data["voltage_V"]
            data["I,A"] = data["current_mA"] / 1000
            data["Total_Time,s"] = data["total_time_s"]
            data["Q,Ah"] = data["capacity_mAh"].abs() / 1000
            data["W,Wh"] = data["energy_mWh"].abs() / 1000
            data = data[columns]
            message = "ok"
        else:
            message = f"В файле {file} нет одного из столбцов {required_cols}"
            
    except Exception as e:
        message = str(e)
        
    if message == "ok":
        return message, data, testType
    else:
        return message, None, None


def txt(file):
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
                
    try:
        columns = ['U,V', 'I,A', 'Q,Ah', 'W,Wh', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
        data = pd.read_csv(
            file,
            sep=r'\s+',
            skiprows=find_header(file),
            encoding="cp1251"
        )
        testType = "Исходное испытание"
        
        required_cols = ["Time,s", "U,V", "I,A", "Q,Ah", "E,Wh", "Step", "Cycle"]
        if all(col in data.columns for col in required_cols):  
            if data.iloc[-1].isna().sum() > 1:
                data = data.iloc[:-1]
            data[["Time,s", "U,V", "I,A", "Q,Ah", "W,Wh"]] = data[["Time,s", "U,V", "I,A", "Q,Ah", "E,Wh"]].apply(lambda x: x.astype(str).str.replace(",", ".")).astype(float)
            
            data['Total_Time,s'] = data['Time,s'] + data.groupby('Step', sort=False)['Time,s'].max().shift().fillna(0).cumsum().loc[data['Step']].values
            data["Total_Time,s"] -= data["Total_Time,s"].min()
            
            data[['Step_index', 'Step_type']] = data['Step'].str.extract(r'^(\d*\.?\d*)([A-Za-z]*)')
            data[["Step_index", "Cycle"]] = data[["Step_index", "Cycle"]].astype(int)
            data.loc[data["Step_type"] == "DCCC", "Step_type"] = "CC Dchg"
            data.loc[data["Step_type"] == "RLAX", "Step_type"] = "Rest"
            data.loc[data["Step_type"] == "CHCC", "Step_type"] = "CC Chg"
            data.loc[data["Step_type"] == "CHCV", "Step_type"] = "CV Chg"
            data["Q,Ah"] = data["Q,Ah"].abs()
            data["W,Wh"] = data["W,Wh"].abs()
            data = data[columns]
            message = "ok"
            
        else:
            message = f"В файле {file} нет одного из столбцов {required_cols}"
            
    except Exception as e:
        message = str(e)
        
    if message == "ok":
        return message, data, testType
    else:
        return message, None, None


def normCurves(file):
    try:
        columns = ['Ucell,V', 'Q/m,Ah/kg']
        data = pd.read_csv(file, sep=";", decimal=",")
        testType = "Норм. разрядная кривая"
        
        if "U_уд(B)" in data.columns and "Q_уд(Ач/кг)" in data.columns:
            data["Ucell,V"] = data["U_уд(B)"]
            data["Q/m,Ah/kg"] = data["Q_уд(Ач/кг)"].abs()
            data = data[columns]
            message = "ok"
        
        else:
            message = "Файл должен быть стандартного формата как в таблице учёта"
    
    except Exception as e:
        message = str(e)
    
    if message == "ok":
        return message, data, testType
    else:
        return message, None, None


def stdCsv(file):
    try:
        columnsRow = ['U,V', 'I,A', 'Q,Ah', 'W,Wh', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
        columnsNormCurve = ['Ucell,V', 'Q/m,Ah/kg']
        columnsCurve = ['U,V', 'Q,Ah']
        data = pd.read_csv(file)
        if all(col in data.columns for col in columnsRow):
            data = data[columnsRow]
            testType = "Исходное испытание"
            message = "ok"
            
        elif all(col in data.columns for col in columnsNormCurve):
            data = data[columnsNormCurve]
            testType = "Норм. разрядная кривая"
            message = "ok"
            
        elif all(col in data.columns for col in columnsCurve):
            data = data[columnsCurve]
            testType = "Разрядная кривая"
            message = "ok"
            
        else:
            message = f"В файле {file} нет нужных столбцов:\n{columnsRow}\nили\n{columnsNormCurve}"
            
    except Exception as e:
        message = str(e)
    
    if message == "ok":
        return message, data, testType
    else:
        return message, None, None
    
    
def csvNdax(file):
    try:
        columns = ['U,V', 'I,A', 'Q,Ah', 'W,Wh', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
        data = pd.read_csv(file, sep=";", decimal=",")
        testType = "Исходное испытание"
        
        required_cols = ["Step Type", "Total Time", "Capacity(Ah)", "Voltage(V)", "Current(A)", "Energy(Wh)"]
        if all(col in data.columns for col in required_cols):
            data["Cycle"] = 1
            data["Step_index"] = 1
            data["Step_type"] = data["Step Type"]
            data["U,V"] = data["Voltage(V)"]
            data["I,A"] = data["Current(A)"]
            data["Total_Time,s"] = pd.to_timedelta(data['Total Time']).dt.total_seconds()
            data["Total_Time,s"] -= data["Total_Time,s"].min()
            data["Q,Ah"] = data["Capacity(Ah)"].abs()
            data["W,Wh"] = data["Energy(Wh)"].abs()
            data = data[columns]
            message = "ok"
        
        else:
            message = f"В файле {file} нет одного из столбцов {required_cols}"
    
    except Exception as e:
        message = str(e)
            
    if message == "ok":
        return message, data, testType
    else:
        return message, None, None
    
    
def xlsx(file):
    try:
        columns = ['U,V', 'I,A', 'Q,Ah', 'W,Wh', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
        data = pd.read_excel(file, sheet_name="record")
        testType = "Исходное испытание"
        
        required_cols = ["Step Type", "Total Time", "Capacity(Ah)", "Voltage(V)", "Current(A)", "Energy(Wh)"]
        if all(col in data.columns for col in required_cols):
            data["Cycle"] = 1
            data["Step_index"] = 1
            data["Step_type"] = data["Step Type"]
            data["U,V"] = data["Voltage(V)"]
            data["I,A"] = data["Current(A)"]
            data["Total_Time,s"] = pd.to_timedelta(data['Total Time']).dt.total_seconds()
            data["Total_Time,s"] -= data["Total_Time,s"].min()
            data["Q,Ah"] = data["Capacity(Ah)"].abs()
            data["W,Wh"] = data["Energy(Wh)"].abs()
            data = data[columns]
            message = "ok"
            
        else:
            message = f"В файле {file} нет одного из столбцов {required_cols}"
    
    except Exception as e:
        message = str(e)
        
    if message == "ok":
        return message, data, testType
    else:
        return message, None, None