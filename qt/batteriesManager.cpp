#include "batteriesManager.hpp"
#include "battery.hpp"

BatteriesManager::BatteriesManager()
    : batteriesCounter(0)
{
}

BatteriesManager::~BatteriesManager()
{
    clear();
}

void BatteriesManager::del(Id batteryId)
{
    delete batteries.take(batteryId);
}

Id BatteriesManager::add(Battery* battery)
{
    ++batteriesCounter;
    batteries[batteriesCounter] = battery;
    return batteriesCounter;
}

Id BatteriesManager::add(const BatteryParams& params)
{
    ++batteriesCounter;
    batteries[batteriesCounter] = new Battery(params);
    return batteriesCounter;
}

void BatteriesManager::clear()
{
    qDeleteAll(batteries);
    batteries.clear();
    batteriesCounter = 0;
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
    int numTests = 0; //TODO
    
    return QPair<int, int>(numBatteries, numTests);
}

QStringList BatteriesManager::names() const
{
    QStringList result;
    for (Battery* battery : batteries) {
        result.append(battery->name());
    }
    return result;
}
