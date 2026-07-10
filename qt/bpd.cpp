#include "bpd.hpp"

namespace BPD {

QVector<TestFloat> readColumn(QFile *file, qint64 offset, qint64 size)
{
    QVector<TestFloat> data(size);
    file->seek(offset);
    file->read(reinterpret_cast<char*>(data.data()), size * sizeof(float));
    return data;
}

Message checkFile(QFile *file, QMap<Value, qint64> &columns, qint64 &size)
{
    if (!file) {
        return Message{"BPD файл не найден", MessageResult::Error};
    }

    if (!file->open(QIODevice::ReadOnly)) {
        return Message{"BPD файл не удалось открыть", MessageResult::Error};
    }

    BinaryHeader header;
    qint64 bytesRead = file->read(reinterpret_cast<char*>(&header), sizeof(BinaryHeader));
    if (bytesRead != sizeof(BinaryHeader)) {
        file->close();
        return Message{"Не удалось прочитать заголовок", MessageResult::Error};
    }

    if (strncmp(header.magic, "BPD", 4) != 0) {
        file->close();
        return Message{"Файл не соответствует BPD формату", MessageResult::Error};
    }

    size = header.value_count;

    columns.clear();

    qint64 fileSize = sizeof(header);
    for (const auto& [value, mask] : MASK.asKeyValueRange()) {
        if (mask & header.column_mask) {
            columns[value] = fileSize;
            fileSize += alignTo64(size * sizeof(TestFloat));
        }
    }

    if (columns.isEmpty()) {
        file->close();
        return Message{"Файл не содержит шапку", MessageResult::Error};
    }

    if (file->size() != fileSize) {
        file->close();
        return Message{"Размер файла не соответствует ожидаемому", MessageResult::Error};
    }

    file->close();

    return Message{"Ok", MessageResult::Success};
}

} // namespace BPD