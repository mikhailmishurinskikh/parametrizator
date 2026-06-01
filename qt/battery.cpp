#include "battery.hpp"

Battery::Battery() = default;

Battery::Battery(const BatteryParams& tmp_params)
    : params(tmp_params)
{
}

void Battery::setParams(const BatteryParams& tmp_params)
{
    params = tmp_params;
}