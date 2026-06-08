#pragma once

#include "constants.hpp"

#include <QAbstractTableModel>
#include <QSortFilterProxyModel>

class BatteriesManager;
class BatteryParams;


enum class BatteryColumn {
    Name,
    NumCells ,
    Mass,
    NominalCapacity,
    TestCount,

    Count = 5
};

class BatteriesModel : public QAbstractTableModel
{
    Q_OBJECT

public:
    explicit BatteriesModel(BatteriesManager* manager, QObject* parent = nullptr);
    
    int rowCount(const QModelIndex& parent = QModelIndex()) const override;
    int columnCount(const QModelIndex& parent = QModelIndex()) const override;
    QVariant data(const QModelIndex& index, int role = Qt::DisplayRole) const override;
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
    Qt::ItemFlags flags(const QModelIndex& index) const override;
    
    Id getBatteryId(const QModelIndex& index) const;
    void addRow(const BatteryParams& params);
    void removeRow(const QModelIndex& index);
    void editRow(const QModelIndex& index, const BatteryParams& params);
    void refresh();

private:
    BatteriesManager* manager;
    QList<Id> batteriesIds;
};


class BatteriesProxyModel : public QSortFilterProxyModel
{
    Q_OBJECT

public:
    explicit BatteriesProxyModel(QObject* parent = nullptr);
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
};