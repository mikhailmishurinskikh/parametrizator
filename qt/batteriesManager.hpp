#pragma once

#include <QMap>
#include <QPair>
#include "constants.hpp"
#include "battery.hpp"

class BatteriesManager
{
public:
    BatteriesManager();

    void del(Id batteryId);
    Battery& add(Battery* battery);
    Battery& add(const BatteryParams& params);
    Battery& get(Id batteryId) const;
    void clear();
    const QList<Id>& ids() const;
    QPair<int, int> count() const;

private:
    QMap<int, Battery*> batteries;
    Id batteriesCounter;
};