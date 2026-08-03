#pragma once

#include <QDataStream>
#include <QString>
#include <QFile>
#include <QTextStream>
#include <QMap>

#include "constants.hpp"


namespace BPD {

static const QMap<Value, qint64> MASK = {
    {Value::Part,          1ULL << 0},
    {Value::Time,          1ULL << 1},
    {Value::Voltage,       1ULL << 2},
    {Value::Current,       1ULL << 3},
    {Value::Capacity,      1ULL << 4},
    {Value::Energy,        1ULL << 5},
    {Value::Norm_Capacity, 1ULL << 6},
    {Value::Norm_Voltage,  1ULL << 7}
};

#pragma pack(push, 1)
struct BinaryHeader {
    char magic[4];        // BPD\0
    qint32 version;      // Версия
    qint64 value_count;  // Число значений в одном столбце
    qint64 column_mask;  // Битовая маска столбцов
    char reserved[40];
};
#pragma pack(pop)

static inline qint64 alignTo64(qint64 value) {
    return (value + 63) & ~63LL;
}

QVector<TestFloat> readColumn(QFile* file, qint64 offset, qint64 size);
Message checkFile(QFile* file, QMap<Value, qint64>& columns, qint64& size);
TestFloat calcCapacity(QFile* file);
TestFloat calcEnergyCapacity(QFile* file);

} // namespace BPD