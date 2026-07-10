#pragma once

#include <QString>

constexpr int MAX_COLUMNS = 64;

enum class TestType {
    Curve,
    Norm_Curve,
    Source
};

enum class MessageResult {
    Success,
    Error
};

enum class Value {
    Part,
    Time,
    Voltage,
    Current,
    Capacity,
    Energy,
    Norm_Capacity,
    Norm_Voltage
};

struct Message {
    QString text;
    MessageResult result;
};

using Id = int;
using TestFloat = double;

inline QString testTypeToString(TestType type)
{
    switch (type) {
        case TestType::Curve:      return "Разрядная кривая";
        case TestType::Norm_Curve: return "Норм. разрядная кривая";
        case TestType::Source:     return "Исходное испытание";
        default:                   return "Неизвестный тип";
    }
}

inline QString valueToString(Value value)
{
    switch (value) {
        case Value::Part:          return "Номер";
        case Value::Time:          return "Время, с";
        case Value::Voltage:       return "Напряжение, В";
        case Value::Current:       return "Ток, А";
        case Value::Capacity:      return "Ёмкость, А·ч";
        case Value::Energy:        return "Энергия, Вт·ч";
        case Value::Norm_Capacity: return "Норм. ёмкость, А·ч";
        case Value::Norm_Voltage:  return "Норм. напряжение, В";
        default:                   return "Неизвестно";
    }
}