#include "battery.hpp"
#include "batteriesManager.hpp"
#include "bpd.hpp"
#include "test.hpp"


Battery::Battery(const BatteryParams& p, QDir* newDir)
    : params(p), dir(newDir), testsCounter(0)
{
}

Battery::~Battery()
{
    qDeleteAll(tests);
    tests.clear();
    testsCounter = 0;
    delete dir;
}

void Battery::setParams(const BatteryParams& p)
{
    params = p;
}

void Battery::del(Id testId)
{
    delete tests.take(testId);
}

Id Battery::add(Test* test)
{
    ++testsCounter;
    QString newFilePath = dir->filePath(QString::number(testsCounter) + ".btd");
    test->setNewFile(newFilePath);
    
    tests[testsCounter] = test;
    return testsCounter;
}

Test* Battery::get(Id testId) const
{
    return tests[testId];
}

QList<Id> Battery::ids() const
{
    return tests.keys();
}

int Battery::count() const
{
    return tests.count();
}

QStringList Battery::names() const
{
    QStringList result;
    for (Test* test : tests.values()) {
        result.append(test->name());
    }
    return result;
}

Message BatteryParams::validate(const BatteriesManager* manager, const QString& oldName) const
{
    if (name.isEmpty()) {
        return Message{
            "Вы не ввели название АКБ",
            MessageResult::Error
        };
    }
    
    QStringList batteriesNames = manager->names();
    if (batteriesNames.contains(name) && name != oldName) {
        return Message{
            "Уже добавлена АКБ с таким названием.\n"
            "Выберите другое название",
            MessageResult::Error
        };
    }

    if (mass < 5.0) {
        return Message{
            "Масса батареи менее 5 грамм\n"
            "Введите реалистичную массу",
            MessageResult::Error
        };
    }

    if (nominalCapacity <= 0) {
        return Message{
            "Номинальная емкость должна быть больше нуля",
            MessageResult::Error
        };
    }
    
    return Message{
        "ок",
        MessageResult::Success
    };
}