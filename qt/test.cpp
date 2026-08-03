#include "test.hpp"
#include "battery.hpp"
#include "bpd.hpp"

Test::Test(QFile *new_file)
{
    file = new_file;
}

Test::~Test()
{
    QFile::remove(file->fileName());
    delete file;
}

void Test::setParams(const TestParams& p)
{
    params = p;
}

QVector<QPair<QString, TestType>> Test::possibleTypes() const
{
    QVector<QPair<QString, TestType>> result;
    if (columns.contains(Value::Time) &&
        columns.contains(Value::Current) &&
        columns.contains(Value::Voltage))
        {
            result.append(QPair<QString, TestType>("Исходное испытание", TestType::Source));
        }

    if (columns.contains(Value::Capacity) &&
        columns.contains(Value::Voltage))
        {
            result.append(QPair<QString, TestType>("Разрядная кривая", TestType::Curve));
        }
    
    if (columns.contains(Value::Norm_Capacity) &&
        columns.contains(Value::Norm_Voltage))
        {
            result.append(QPair<QString, TestType>("Норм. разрядная кривая", TestType::Norm_Curve));
        }
    return result;
}

QMap<Value, QVector<TestFloat>> Test::load() const
{
    QMap<Value, QVector<TestFloat>> result;

    file->open(QIODevice::ReadOnly);

    for (const auto& [value, offset] : columns.asKeyValueRange()) {
        result[value] = BPD::readColumn(file, offset, size);
    }

    file->close();
    return result;
}

Message Test::checkFile()
{
    return BPD::checkFile(file, columns, size);
}

void Test::setNewFile(const QString &newFilePath)
{
    QFile::rename(filePath(), newFilePath);
    delete file;
    file = new QFile(newFilePath);
}

void Test::calcCapacities()
{
    file->open(QIODevice::ReadOnly);
    if (columns.contains(Value::Capacity)) {
        auto capacityColumn = BPD::readColumn(file, columns[Value::Capacity], size);
        params.capacity = calcAbsMax(capacityColumn);
    } else params.capacity = 0;

    if (columns.contains(Value::Norm_Capacity)) {
        auto normCapacityColumn = BPD::readColumn(file, columns[Value::Norm_Capacity], size);
        params.normCapacity = calcAbsMax(normCapacityColumn);
    } else params.normCapacity = 0;

    if (columns.contains(Value::Energy)) {
        auto energyColumn = BPD::readColumn(file, columns[Value::Energy], size);
        params.energyCapacity = calcAbsMax(energyColumn);
    } else params.energyCapacity = 0;

    if (columns.contains(Value::Norm_Energy)) {
        auto normEnergyColumn = BPD::readColumn(file, columns[Value::Energy], size);
        params.normEnergyCapacity = calcAbsMax(normEnergyColumn);
    } else params.normEnergyCapacity = 0;

    file->close();
}

Message TestParams::validate(const Battery* battery, const QStringList& otherNames) const
{
    if (name.isEmpty()) {
        return Message{
            "Вы не ввели название испытания",
            MessageResult::Error
        };
    }

    if (otherNames.contains(name)) {
        return Message{
            "Уже добавлено испытание с таким названием.\n"
            "Выберите другое название",
            MessageResult::Error
        };
    }
    return Message{
        "ок",
        MessageResult::Success
    };
}
