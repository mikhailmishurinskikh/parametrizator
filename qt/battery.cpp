#include "battery.hpp"
#include "batteriesManager.hpp"

Battery::Battery() = default;

Battery::Battery(const BatteryParams& p)
    : params(p)
{
}

void Battery::setParams(const BatteryParams& p)
{
    params = p;
}

Message BatteryParams::validate(const BatteriesManager* manager, const QString& oldName) const
{
    if (name.isEmpty()) {
        return Message{
            "Вы не ввели название АКБ",
            MessageType::ERROR
        };
    }
    
    QStringList batteriesNames = manager->names();
    if (batteriesNames.contains(name) && name != oldName) {
        return Message{
            "Уже добавлена АКБ с таким названием.\n"
            "Выберите другое название",
            MessageType::ERROR
        };
    }

    if (mass < 5.0) {
        return Message{
            "Масса батареи менее 5 грамм\n"
            "Введите реалистичную массу",
            MessageType::ERROR
        };
    }

    if (nominalCapacity <= 0) {
        return Message{
            "Номинальная емкость должна быть больше нуля",
            MessageType::ERROR
        };
    }
    
    return Message{
        "ок",
        MessageType::SUCCESS
    };
}