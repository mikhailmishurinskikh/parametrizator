#pragma once

#include "constants.hpp"

#include <QString>
#include <QMap>

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
    Battery();
    Battery(const BatteryParams& p);
    ~Battery();
    void setParams(const BatteryParams& p);

    void del(Id testId);
    Id add(Test* test);
    Id add(const TestParams& params);
    void clear();
    
    QString name() const { return params.name; }
    int numCells() const { return params.numCells; }
    float mass() const { return params.mass; }
    float nominalCapacity() const { return params.nominalCapacity; }
    int count() const;

private:
    BatteryParams params;
    QMap<Id, Test*> tests;
    Id testsCounter;
};