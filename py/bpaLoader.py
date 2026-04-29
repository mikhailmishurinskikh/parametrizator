import os
import json
import tempfile
import zipfile

import pandas as pd

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QFileDialog, QProgressDialog, QMessageBox



class SaveBPAWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    
    def __init__(self, filepath, batteries):
        super().__init__()
        self.filepath = filepath
        self.batteries = batteries
    
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:                
                total = len(self.batteries)
                for i, battery in enumerate(self.batteries):
                    self.save_battery(tmpdir, battery, i)
                    progress_value = int((i + 1) / total * 100)
                    self.progress.emit(progress_value)
                
                self.create_zip(tmpdir)
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
        for i, test in enumerate(battery.tests.values()):
            parquet_path = os.path.join(battery_folder, f'{i}.parquet')
            test.df.to_parquet(parquet_path, index=False)
            
            tests_meta.append({
                'id': i,
                'name': test.name,
                'file': test.file,
                'testType': test.testType
            })
        
        with open(os.path.join(battery_folder, 'tests_metadata.json'), 'w', encoding='utf-8') as f:
            json.dump(tests_meta, f, ensure_ascii=False, indent=2)
    
    
    def create_zip(self, tmpdir):
        with zipfile.ZipFile(self.filepath, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, tmpdir)
                    zipf.write(file_path, arcname)



def saveDialog(parent, batteries):
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Сохранить архив BPA",
        "",
        "BPA архивы (*.bpa);;Все файлы (*.*)"
    )
    
    if not file_path:
        return
        
    progress = QProgressDialog("Сохранение BPA архива...", "Отмена", 0, 100, parent)
    progress.setWindowTitle("Сохранение")
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.setMinimumDuration(0)
    progress.show()
    
    def on_finished(message):
        progress.close()
        thread.deleteLater()
        if message == "ok":
            QMessageBox.information(parent, "Сохранение успешно",
                                    f"Успешно сохранено по пути: {file_path}")
        else:
            QMessageBox.warning(parent, "Ошибка сохранения", message)
    
    thread = SaveBPAWorker(file_path, batteries)
    thread.progress.connect(progress.setValue)
    thread.finished.connect(on_finished)
    progress.canceled.connect(thread.quit)
        
    thread.start()
    progress.exec()
    
    
    
class LoadBPAWorker(QThread):
    progress = Signal(int)
    finished = Signal(str)
    
    
    def __init__(self, filepath, batteriesManager):
        super().__init__()
        self.filepath = filepath
        self.batteries = batteriesManager
        self.batteries.clear()
    
    
    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(self.filepath, 'r') as zipf:
                    zipf.extractall(tmpdir)

                numBatteries = sum(1 for entry in os.scandir(tmpdir))
                for i, item in enumerate(os.listdir(tmpdir)):
                    item_path = os.path.join(tmpdir, item)
                    
                    self.load_battery(item_path, self.batteries)
                    
                    progress_value = int((i + 1) / numBatteries * 100)
                    self.progress.emit(progress_value)
                    
                self.finished.emit("ok")
                
        except Exception as e:
            self.finished.emit(str(e))
    
    
    def load_battery(self, battery_path, batteriesManager):        
        with open(os.path.join(battery_path, 'params.json'), 'r', encoding='utf-8') as f:
            battery_params = json.load(f)
        
        battery = batteriesManager.add(
            battery_params['name'],
            battery_params['numCells'],
            battery_params['mass']
        )
        
        with open(os.path.join(battery_path, 'tests_metadata.json'), 'r', encoding='utf-8') as f:
            tests_meta = json.load(f)
        
        for test_meta in tests_meta:
            parquet_path = os.path.join(battery_path, f"{test_meta['id']}.parquet")
            df = pd.read_parquet(parquet_path)
            test = battery.addTest(df, test_meta["file"], test_meta["testType"])
            test.name = test_meta["name"]
            
            
            
def loadDialog(parent, batteriesManager):
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Загрузить BPA архив",
        "",
        "BPA архивы (*.bpa);;Все файлы (*.*)"
    )
    
    if not file_path:
        return None
    
    progress = QProgressDialog("Загрузка BPA архива...", "Отмена", 0, 100, parent)
    progress.setWindowTitle("Загрузка")
    progress.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress.setMinimumDuration(0)
    progress.show()
        
    def on_finished(message):
        progress.close()
        thread.deleteLater()
        if message == "ok":
            QMessageBox.information(parent, "Загрузка успешна",
                                    f"Успешно загружено из файла: {file_path}")
        else:
            QMessageBox.warning(parent, "Ошибка сохранения", message)
    
    thread = LoadBPAWorker(file_path, batteriesManager)
    thread.progress.connect(progress.setValue)
    thread.finished.connect(on_finished)
    progress.canceled.connect(thread.quit)
    
    thread.start()
    progress.exec()