#pragma once

#include <QAbstractTableModel>
#include <QVector>
#include "batteriesManager.hpp"

enum class BatteryColumn {
    Name = 0,
    NumCells = 1,
    Mass = 2,
    TestCount = 3,

    Count = 4
};

class BatteriesModel : public QAbstractTableModel
{
    Q_OBJECT

public:
    explicit BatteriesModel(const BatteriesManager& manager, QObject* parent = nullptr);
    
    int rowCount(const QModelIndex& parent = QModelIndex()) const override;
    int columnCount(const QModelIndex& parent = QModelIndex()) const override;
    QVariant data(const QModelIndex& index, int role = Qt::DisplayRole) const;
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const;
    Qt::ItemFlags flags(const QModelIndex& index) const override;
    void sort(int column, Qt::SortOrder order) override;
    
    Id getBatteryId(int row) const;
    void refresh();

private:
    const BatteriesManager& manager;
    QList<Id> batteriesIds;
    BatteryColumn sortColumn = BatteryColumn::Name;
    Qt::SortOrder sortOrder = Qt::DescendingOrder;
};