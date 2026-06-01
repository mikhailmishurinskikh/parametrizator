#include "batteriesManager.hpp"

BatteriesManager::BatteriesManager()
    : batteriesCounter(0)
{
}

void BatteriesManager::del(Id batteryId)
{
    Q_ASSERT_X(batteries.contains(batteryId), "get", "Battery not found");
    delete batteries.take(batteryId);
}

Battery& BatteriesManager::add(Battery* battery)
{
    ++batteriesCounter;
    batteries[batteriesCounter] = battery;
    return *batteries[batteriesCounter];
}

Battery& BatteriesManager::add(const BatteryParams& params)
{
    ++batteriesCounter;
    batteries[batteriesCounter] = new Battery(params);
    return *batteries[batteriesCounter];
}

Battery& BatteriesManager::get(Id batteryId) const
{
    Q_ASSERT_X(batteries.contains(batteryId), "get", "Battery not found");
    return *batteries[batteryId];
}

void BatteriesManager::clear()
{
    qDeleteAll(batteries);
    batteries.clear();
    batteriesCounter = 0;
}

const QList<Id>& BatteriesManager::ids() const
{
    return batteries.keys();
}

QPair<int, int> BatteriesManager::count() const
{
    int numBatteries = batteries.size();
    int numTests = 0;
    
    return QPair<int, int>(numBatteries, numTests);
}