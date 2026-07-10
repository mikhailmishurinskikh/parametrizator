#pragma once

#include "constants.hpp"

#include <QString>
#include <QVector>
#include <QFile>
#include <QFileInfo>


class Battery;


struct TestParams {
    QString name;
    TestType type;

    Message validate(const Battery* battery, const QStringList& otherNames) const;
};

class Test {
public:
    Test(QFile* new_file);
    ~Test();
    void setParams(const TestParams& p);
    QVector<QPair<QString, TestType>> possibleTypes() const;
    QMap<Value, QVector<TestFloat>> load() const;
    Message checkFile();
    void setNewFile(const QString& filePath);


    QString name() const { return params.name; }
    TestType type() const { return params.type; }
    TestParams getParams() const { return params; }
    QString filePath() const { return QFileInfo(*file).absoluteFilePath(); }

private:
    TestParams params;
    QMap<Value, qint64> columns;
    qint64 size;
    QFile* file;
};