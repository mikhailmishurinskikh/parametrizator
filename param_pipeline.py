import pandas as pd
import fastnda
import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import cumulative_trapezoid
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


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


def to_pandas(file : str):
    """
    На вход получаем путь к файлу испытаний в txt или ndax(nda) формате.
    
    На выход pd.DataFrame со стандартными столбцами
    columns = ['Time,s', 'U,V', 'I,A', 'Q,Ah', 'Cycle', 'Total_Time,s', 'Step_index', 'Step_type']
    
    None в случае ошибки и сообщение об ошибке
    """
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


def RC2_func(x, a, b, c, p, q):
    return a + b * np.exp( p * x ) + c * np.exp( q * x )


def biexpfit(xdata, ydata):
    """
    Взята с https://github.com/madphysicist/scikit-guess/issues/1
    
    Подбирает параметры для аппроксимации функцией:
    y = a + b * exp( p x ) + c * exp( q x )
    
    На вход берет x, y в виде двух np.array
    
    Возвращает a,b,c,p,q
    """
    x = np.array(xdata)
    y = np.array(ydata)

    S = [0.]*len(xdata)
    for k in range(1,len(ydata)) :
        S[k] = S[k-1] + (1/2.)*(y[k]+y[k-1])*(x[k]-x[k-1])
    S = np.array(S)
    
    SS = [0.]*len(xdata)
    for k in range(1,len(ydata)) :
        SS[k] = SS[k-1] + (1/2.)*(S[k]+S[k-1])*(x[k]-x[k-1])
    SS = np.array(SS)

    x2 = x * x
    x3 = x2 * x
    x4 = x2 * x2

    M = [ [sum(SS*SS),  sum(SS*S), sum( SS*x2 ), sum(SS*x), sum(SS)],
          [sum(SS*S),   sum(S*S),  sum(S*x2),    sum(S*x), sum(S) ],
          [sum(SS*x2),  sum(S*x2), sum(x4),      sum(x3),  sum(x2) ],
          [sum(SS*x),   sum(S*x),  sum(x3),      sum(x2),  sum(x) ],
          [sum(SS),     sum(S),    sum(x2),      sum(x),   len(xdata) ] ]

    Minv = np.linalg.inv(M)
    
    Ycol = np.array( [ sum(SS*y), sum(S*y), sum(x2*y), sum(x*y), sum(y) ] )

    A,B,C,D,E = list( np.matmul(Minv,Ycol) )

    p = (1/2.)*(B + np.sqrt(B*B+4*A))
    q = (1/2.)*(B - np.sqrt(B*B+4*A))

    beta = np.exp(p*x)
    eta = np.exp(q*x)
    betaeta = beta * eta

    L = [ [ len(xdata), sum(beta), sum(eta) ],
          [ sum(beta),  sum(beta*beta), sum(betaeta) ],
          [ sum(eta),   sum(betaeta), sum(eta*eta)] ]

    Linv = np.linalg.inv(L)

    Ycol = np.array( [ sum(y), sum(beta*y), sum(eta*y) ] )

    a,b,c = list( np.matmul( Linv, Ycol ) )

    return a,b,c,p,q


def calc_params(a, b, c, p, q, I, U0):
    """
    Вычисляет параметры RC цепочек и R0 по известным a,b,c,p,q,I,U0
    
    Для первых пяти используем функцию biexpfit
    I - ток импульса
    U0 - напряжение в начале импульса
    
    Возвращает: R0, R1, R2, C1, C2
    """
    R1 = b/I
    R2 = c/I
    R0 = (U0 - (a+b+c))/I
    tau1 = -1/p
    tau2 = -1/q
    C1 = tau1/R1
    C2 = tau2/R2
    
    return R0, R1, R2, C1, C2


def combine_files(files):
    """
    Функция принимает на вход список файлов с испытаниями или папку с файлами.
    
    На выходе получается один pandas.DataFrame со всеми испытаниями последовательно
    """
    
    if type(files) == str:
        dir = Path(files)
        files = []
        for file in dir.iterdir():
            try: find_header(file)
            except ValueError:
                continue
            
            files.append(file)
    
    time = 0
    file_num = 0
    df = pd.DataFrame()
    for file in files:
        data = to_pandas(file)
        
        delta_time = data["Total_Time,s"].max()
        data["Total_Time,s"] += time
        data["file_num"] = file_num
        
        df = pd.concat((df, data))
        time += delta_time+1
        file_num += 1
    
    plt.figure()    
    sns.lineplot(data=df, x="Total_Time,s", y="U,V")
    plt.figure()
    sns.lineplot(data=df, x="Total_Time,s", y="I,A")
    
    return df


class Energy_Storage:
    def __init__(self):
        self.OCV = None
        self.RC_params = {}
        
    def calc_OCV(self, file : str):
        """
        Принимает на вход файл с испытанием OCV
        
        Пользователь выбирает нужные участки графика и функция
        строит разрядную, зарядную и усредненную кривые
        """
        data = to_pandas(file)
        plt.figure()
        sns.lineplot(data=data, x="Total_Time,s", y="U,V", hue="Step_index",
                    palette=sns.color_palette("deep", 10))
        plt.legend(title="Номер шага")
        plt.show(True)
        Dchg_index = int(input("Введите номер шага разрядной кривой"))
        Chg_index = int(input("Введите номер шага зарядной кривой"))
        
        Chg = data[data["Step_index"] == Chg_index]
        Dchg = data[data["Step_index"] == Dchg_index]
        
        Q = np.trapezoid(np.abs(Dchg["I,A"]), Dchg["Total_Time,s"]) / 3600
        
        Chg["soc"] = cumulative_trapezoid(np.abs(Chg["I,A"]), Chg["Total_Time,s"], initial=0) / 3600 / Q * 100
        Dchg["soc"] = 100 - cumulative_trapezoid(np.abs(Dchg["I,A"]), Dchg["Total_Time,s"], initial=0) / 3600 / Q * 100
        
        soc_grid = np.linspace(0, 100, 1001)
        chg_U = np.interp(soc_grid, Chg["soc"], Chg["U,V"])
        dchg_U = np.interp(soc_grid, Dchg["soc"][::-1], Dchg["U,V"][::-1])
        mean_U = (dchg_U + chg_U) / 2
        
        plt.plot(soc_grid, chg_U, label="Chg")
        plt.plot(soc_grid, dchg_U, label="Dchg")
        plt.plot(soc_grid, mean_U, label="Mean")
        plt.xlabel("SOC")
        plt.ylabel("U,V")
        plt.legend()