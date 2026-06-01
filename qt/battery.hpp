#pragma once

#include <QString>


struct BatteryParams {
    QString name;
    int numCells;
    float mass;
};


class Battery
{
public:
    Battery();
    Battery(const BatteryParams& tmp_params);
    void setParams(const BatteryParams& tmp_params);
    
    
    QString name() const { return params.name; }
    int numCells() const { return params.numCells; }
    float mass() const { return params.mass; }

private:
    BatteryParams params;
};