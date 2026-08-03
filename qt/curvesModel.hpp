#pragma once

#include "constants.hpp"

#include <QAbstractTableModel>
#include <QSortFilterProxyModel>

class BatteriesManager;


enum class CurveColumn {
    Battery,
    Name,
    NumCells,
    NominalCapacity,
    Type,
    Capacity,
    EnergyCapacity,
    Label,

    Count = 8
};

class CurvesModel : public QAbstractTableModel
{
    Q_OBJECT

public:
    explicit CurvesModel(BatteriesManager* manager, QObject* parent = nullptr);

    int rowCount(const QModelIndex& parent = QModelIndex()) const override;
    int columnCount(const QModelIndex& parent = QModelIndex()) const override;
    QVariant data(const QModelIndex& index, int role = Qt::DisplayRole) const override;
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
    Qt::ItemFlags flags(const QModelIndex& index) const override;

    void refresh();

private:
    BatteriesManager* manager;
    QVector<QPair<Id, Id>> curvesIds;
    QVector<QString> labels;
    Value capacityType;
};


class CurvesProxyModel : public QSortFilterProxyModel
{
    Q_OBJECT

public:
    explicit CurvesProxyModel(QObject* parent = nullptr);
    QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const override;
};