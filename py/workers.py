import os
import json
import tempfile
import zipfile

import pandas as pd

from readers import read
from battery import Battery, BatteriesManager
import validate

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QFileDialog, QProgressDialog, QMessageBox



class SaveZIPWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    
    def __init__(self, testsList):
        super().__init__()
        self.tests = testsList
        self.dialogName = "Сохранить архив ZIP"
        self.progressName = "Сохранение ZIP архива..."
        self.filter = "ZIP архивы (*.zip);;Все файлы (*.*)"
        
        
    def setPath(self, path):
        self.path = path
        
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                total = len(self.tests)
                for i, test in enumerate(self.tests):                    
                    test.df.to_csv(os.path.join(tmpdir, f"{test.name}.csv"),
                              index=False, encoding="utf-8")
                    progress_value = int((i + 1) / total * 100 / 2)
                    self.progress.emit(progress_value)
                    
                    if self.checkInterrupt(): return
                
                with zipfile.ZipFile(
                        os.path.join(tmpdir, "archive.zip"),
                        "w",
                        compression=zipfile.ZIP_DEFLATED,
                        compresslevel=6) as zipf:
                    
                    for i, filename in enumerate(os.listdir(tmpdir)):
                        if filename == "archive.zip":
                            continue
                        
                        zipf.write(os.path.join(tmpdir, filename), filename)
                        progress_value = int((i + 1) / total * 100 / 2 + 50)
                        self.progress.emit(progress_value)
                        
                        if self.checkInterrupt(): return
                        
                if os.path.exists(self.path):
                    os.remove(self.path)
                        
                os.rename(os.path.join(tmpdir, "archive.zip"), self.path)
            
            self.finished.emit("ok")
                
                
        except Exception as e:
            self.finished.emit(str(e))
        
        
    def checkInterrupt(self):
        if self.isInterruptionRequested():
            self.finished.emit("interrupted")
            return True
        
        return False
    
            
            
class LoadZIPWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    
    def __init__(self, battery):
        super().__init__()
        self.battery = battery
        self.dialogName = "Загрузить архив ZIP"
        self.progressName = "Загрузка ZIP архива..."
        self.filter = "ZIP архивы (*.zip);;Все файлы (*.*)"
        
    
    def setPath(self, path):
        self.path = path
        
        
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(self.path, 'r') as zipf:
                    zipf.extractall(tmpdir)
                    
                files = [f for f in os.listdir(tmpdir) if f.endswith('.csv')]
                total = len(files)
                    
                for i, filename in enumerate(files):
                    file_path = os.path.join(tmpdir, filename)
                    
                    progress_value = int((i + 1) / total * 100)
                    self.progress.emit(progress_value)
                    
                    message, df, testType = read(file_path, "Стандартные CSV файлы (*.csv)")
                    if message == "ok":
                        name = filename.replace(".csv", "")
                        nameMessage = validate.TEST_NAME(name, self.battery)
                        if nameMessage == "ok":
                            self.battery.addTest(filename.replace(".csv", ""), testType, df)
                        else:
                            self.finished.emit(nameMessage)
                            return
                        
                    else:
                        self.finished.emit(message)
                        return
                        
                    if self.checkInterrupt(): return
            
            self.finished.emit("ok")
        
        except Exception as e:
            self.finished.emit(str(e))
    
    
    def checkInterrupt(self):
        if self.isInterruptionRequested():
            self.finished.emit("interrupted")
            return True
        
        return False


class SaveBPAWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    
    def __init__(self, batteriesList):
        super().__init__()
        self.batteries = batteriesList
        self.dialogName = "Сохранить архив BPA"
        self.progressName = "Сохранение BPA архива..."
        self.filter = "BPA архивы (*.bpa);;Все файлы (*.*)"
        
        
    def setPath(self, path):
        self.path = path
    
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:                
                total = len(self.batteries)
                for i, battery in enumerate(self.batteries):
                    if self.checkInterrupt(): return
                    if not self.save_battery(tmpdir, battery, i): return
                    progress_value = int((i + 1) / total * 100 / 2)
                    self.progress.emit(progress_value)
                
                if not self.create_zip(tmpdir): return
                self.finished.emit("ok")
                
        except Exception as e:
            self.finished.emit(str(e))

    
    def save_battery(self, tmpdir, battery, index):
        battery_folder = os.path.join(tmpdir, f'{index}')
        os.makedirs(battery_folder)
        
        battery_params = {
            'name': battery.name,
            'numCells': battery.numCells,
            'mass': battery.mass,
        }
        
        with open(os.path.join(battery_folder, 'params.json'), 'w', encoding='utf-8') as f:
            json.dump(battery_params, f, ensure_ascii=False, indent=2)
        
        tests_meta = []
        tests = battery.testsList()
        for i, test in enumerate(tests):
            parquet_path = os.path.join(battery_folder, f'{i}.parquet')
            test.df.to_parquet(parquet_path, index=False)
            
            tests_meta.append({
                'id': i,
                'name': test.name,
                'testType': test.testType
            })
            
            if self.checkInterrupt(): return False
        
        with open(os.path.join(battery_folder, 'tests_metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(tests_meta, f, ensure_ascii=False, indent=2)
            
            if self.checkInterrupt(): return False
            
        return True
    
    
    def create_zip(self, tmpdir):
        with zipfile.ZipFile(os.path.join(tmpdir, "archive.zip"), 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file == "archive.zip":
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, tmpdir)
                    zipf.write(file_path, arcname)
                    
                    if self.checkInterrupt(): return False
        
        if os.path.exists(self.path):
            os.remove(self.path)
        
        os.rename(os.path.join(tmpdir, "archive.zip"), self.path)
        return True
                    
                    
    def checkInterrupt(self):
        if self.isInterruptionRequested():
            self.finished.emit("interrupted")
            return True
        
        return False
                        
    
    
class LoadBPAWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    
    
    def __init__(self, batteriesManager):
        super().__init__()
        self.batteries = batteriesManager
        self.batteries.clear()
        
        self.dialogName = "Загрузить архив BPA"
        self.progressName = "Загрузка BPA архива..."
        self.filter = "BPA архивы (*.bpa);;Все файлы (*.*)"
        
        
    def setPath(self, path):
        self.path = path
    
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(self.path, 'r') as zipf:
                    zipf.extractall(tmpdir)

                total = sum(1 for _ in os.scandir(tmpdir))
                for i, item in enumerate(os.listdir(tmpdir)):
                    item_path = os.path.join(tmpdir, item)
                    
                    if not self.load_battery(item_path): return
                    
                    progress_value = int((i + 1) / total * 100)
                    self.progress.emit(progress_value)
                    
                    if self.checkInterrupt(): return
                    
                self.finished.emit("ok")
                
        except Exception as e:
            self.finished.emit(str(e))
    
    
    def load_battery(self, battery_path):
        with open(os.path.join(battery_path, 'params.json'), 'r', encoding='utf-8') as f:
            battery_params = json.load(f)
        
        battery = self.batteries.add(
            battery_params['name'],
            battery_params['numCells'],
            battery_params['mass']
        )
        
        with open(os.path.join(battery_path, 'tests_metadata.json'), 'r', encoding='utf-8') as f:
            tests_meta = json.load(f)
        
        for test_meta in tests_meta:
            parquet_path = os.path.join(battery_path, f"{test_meta['id']}.parquet")
            df = pd.read_parquet(parquet_path)
            battery.addTest(test_meta["name"], test_meta["testType"], df)
            
            if self.checkInterrupt(): return False
        
        return True
            
            
    def checkInterrupt(self):
        if self.isInterruptionRequested():
            self.finished.emit("interrupted")
            return True
        
        return False
            
            
    
def saveDialog(parent, thread):
    path, _ = QFileDialog.getSaveFileName(
        parent,
        thread.dialogName,
        os.path.join(".", "unnamed"),
        thread.filter
    )
    
    if not path:
        return
    
    thread.setPath(path)
        
    progress = QProgressDialog(thread.progressName, "Отмена", 0, 100, parent)
    progress.setWindowTitle("Сохранение")
    progress.setWindowModality(Qt.WindowModality.NonModal)
    progress.setMinimumDuration(0)
    
    def on_finished(message):
        thread.deleteLater()
        progress.close()
        progress.deleteLater()
        if message == "ok":
            QMessageBox.information(parent, "Сохранение успешно",
                                    f"Успешно сохранено по пути: {path}")
        elif message == "interrupted":
            return
        else:
            QMessageBox.warning(parent, "Ошибка сохранения", message)
    
    thread.progress.connect(progress.setValue)
    thread.finished.connect(on_finished)
    progress.canceled.connect(thread.requestInterruption)
        
    thread.start()
    progress.open()
    
    
def loadDialog(parent, thread, callback, path=None):
    if path is None:
        path, _ = QFileDialog.getOpenFileName(
            parent,
            thread.dialogName,
            "",
            thread.filter
        )
        
        if not path:
            return None
    
    thread.setPath(path)
    
    progress = QProgressDialog(thread.progressName, "Отмена", 0, 100, parent)
    progress.setWindowTitle("Загрузка")
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.setMinimumDuration(0)
    
    def on_finished(message):
        thread.deleteLater()
        progress.close()
        progress.deleteLater()
        if message == "ok":
            QMessageBox.information(parent, "Загрузка успешна",
                                    f"Успешно загружено из файла: {path}")
        elif message == "interrupted":
            return
        else:
            QMessageBox.warning(parent, "Ошибка загрузки", message)
            
        callback()
            
    thread.progress.connect(progress.setValue)
    thread.finished.connect(on_finished)
    progress.canceled.connect(thread.requestInterruption)
    
    thread.start()
    progress.open()