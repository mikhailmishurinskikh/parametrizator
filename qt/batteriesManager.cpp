#include "batteriesManager.hpp"
#include "battery.hpp"

#include <QDebug>

BatteriesManager::BatteriesManager()
    : batteriesCounter(0),
    tempDir(new QTemporaryDir())
{
}

BatteriesManager::~BatteriesManager()
{
    qDeleteAll(batteries);
    batteries.clear();
    batteriesCounter = 0;
    delete tempDir;
}

void BatteriesManager::del(Id batteryId)
{
    delete batteries.take(batteryId);
}

Id BatteriesManager::add(const BatteryParams& params)
{
    ++batteriesCounter;
    QString batteryDirPath = tempDir->path() + QString::number(batteriesCounter);
    QDir().mkpath(batteryDirPath);
    QDir* batteryDir = new QDir(batteryDirPath);

    batteries[batteriesCounter] = new Battery(params, batteryDir);
    return batteriesCounter;
}

Battery* BatteriesManager::get(Id batteryId) const
{
    return batteries[batteryId];
}

QList<Id> BatteriesManager::ids() const
{
    return batteries.keys();
}

QPair<int, int> BatteriesManager::count() const
{
    int numBatteries = batteries.size();
    int numTests = 0;
    for (Battery* battery : batteries.values()) {
        numTests += battery->count();
    }
    return QPair<int, int>(numBatteries, numTests);
}

QStringList BatteriesManager::names() const
{
    QStringList result;
    for (Battery* battery : batteries.values()) {
        result.append(battery->name());
    }
    return result;
}
