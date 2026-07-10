#pragma once

#include "constants.hpp"

#include <QAbstractTableModel>
#include <QSortFilterProxyModel>

class TestParams;
class Battery;
class Test;


enum class TestColumn {
    Name,
    Type,

    Count = 2
};

class TestsModel : public QAbstractTableModel
{
    Q_OBJECT

public:
    explicit TestsModel(QObject* parent = nullptr);
    
    int rowCount(const QModelIndex& parent = QModelIndex()) const override;
    int columnCount(const QModelIndex& parent = QModelIndex()) const override;
    QVariant data(const QModelIndex& index, int role = Qt::DisplayRole) const override;
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
    Qt::ItemFlags flags(const QModelIndex& index) const override;
    
    Id getTestId(const QModelIndex& index) const;
    void setBattery(Battery* p_battery);
    void addRow(Test* test);
    void removeRow(const QModelIndex& index);
    void editRow(const QModelIndex& index, const TestParams& params);
    void refresh();


private:
    Battery* battery;
    QList<Id> testsIds;
};


class TestsProxyModel : public QSortFilterProxyModel
{
    Q_OBJECT

public:
    explicit TestsProxyModel(QObject* parent = nullptr);
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
};