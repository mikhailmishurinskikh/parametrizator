#pragma once

#include "constants.hpp"

#include <QString>
#include <QMap>
#include <QList>
#include <QPair>
#include <QTemporaryDir>
#include <QDir>

class Battery;
class BatteryParams;

class BatteriesManager
{
public:
    BatteriesManager();
    ~BatteriesManager();

    void del(Id batteryId);
    Id add(const BatteryParams& params);

    Battery* get(Id batteryId) const;
    QList<Id> ids() const;
    QPair<int, int> count() const;
    QStringList names() const;

private:
    Id batteriesCounter;
    QMap<Id, Battery*> batteries;

    QTemporaryDir* tempDir;
};