#pragma once

#include "constants.hpp"

#include <QString>
#include <QMap>
#include <QDir>


class BatteriesManager;
class Test;
class TestParams;

struct BatteryParams {
    QString name;
    int numCells;
    float mass;
    float nominalCapacity;

    Message validate(const BatteriesManager* manager, const QString& oldName) const;
};


class Battery {
public:
    Battery(const BatteryParams& p, QDir* newDir);
    ~Battery();
    void setParams(const BatteryParams& p);

    void del(Id testId);
    Id add(Test* test);

    Test* get(Id testId) const;
    QList<Id> ids() const;
    int count() const;
    QStringList names() const;
    
    QString name() const { return params.name; }
    int numCells() const { return params.numCells; }
    float mass() const { return params.mass; }
    float nominalCapacity() const { return params.nominalCapacity; }
    QString getDirPath() const { return dir->path(); }

private:
    BatteryParams params;
    QMap<Id, Test*> tests;
    Id testsCounter;
    QDir* dir;
};