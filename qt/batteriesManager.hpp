#pragma once

#include "constants.hpp"

#include <QString>
#include <QMap>
#include <QList>
#include <QPair>

class Battery;
class BatteryParams;

class BatteriesManager
{
public:
    BatteriesManager();
    ~BatteriesManager();

    void del(Id batteryId);
    Id add(Battery* battery);
    Id add(const BatteryParams& params);
    void clear();

    Battery* get(Id batteryId) const;
    QList<Id> ids() const;
    QPair<int, int> count() const;
    QStringList names() const;

private:
    QMap<Id, Battery*> batteries;
    Id batteriesCounter;
};