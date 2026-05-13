from pathvalidate import is_valid_filename

def TEST_NAME(name, battery, oldName=""):
    if not name:
        message = "Вы не ввели название испытания"
        return message
    
    testsNames = battery.testNames()
    if name in testsNames and name != oldName:
        message = "Уже добавлено испытание с таким названием.\n" \
            "Выберите другое название"
        return message
    
    if not is_valid_filename(name):
        message = "Недопустимое имя испытания.\n" \
            "Ваша операционная система не позволяет создавать файлы с таким именем"
        return message
    
    return "ok"


def BATTERY_PARAMS(name, numCells, mass, batteryManager, oldName=""):
    if not name:
        message = "Вы не ввели название АКБ"
        return message
        
    batteriesNames = batteryManager.names()
    if name in batteriesNames and name != oldName:
        message = "Уже добавлена АКБ с таким названием.\n" \
            "Выберите другое название"
        return message
    
    if mass < 5:
        message = "Масса батареи менее 5 грамм\n" \
            "Введите реалистичную массу"
        return message
    
    if not is_valid_filename(name):
        message = "Недопустимое имя\n" \
            "Ваша операционная система не позволяет " \
            "создавать файлы с таким именем"
        return message
    
    return "ok"