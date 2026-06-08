#include "batteriesModel.hpp"
#include "battery.hpp"
#include "batteriesManager.hpp"


BatteriesModel::BatteriesModel(BatteriesManager* manager, QObject* parent)
    : QAbstractTableModel(parent)
    , manager(manager)
{
    refresh();
}

int BatteriesModel::rowCount(const QModelIndex& parent) const
{
    if (parent.isValid()) return 0;
    return batteriesIds.size();
}

int BatteriesModel::columnCount(const QModelIndex& parent) const
{
    if (parent.isValid()) return 0;
    return static_cast<int>(BatteryColumn::Count);
}

QVariant BatteriesModel::data(const QModelIndex& index, int role) const
{
    if (!index.isValid()) return QVariant();
    if (role != Qt::DisplayRole) return QVariant();
    
    int row = index.row();
    auto col = static_cast<BatteryColumn>(index.column());
    
    if (row >= batteriesIds.size()) return QVariant();
    
    Id batteryId = batteriesIds[row];
    const Battery* battery = manager->get(batteryId);
    
    switch (col) {
        case BatteryColumn::Name:
            return battery->name();
        case BatteryColumn::NumCells:
            return battery->numCells();
        case BatteryColumn::Mass:
            return battery->mass();
        case BatteryColumn::NominalCapacity:
            return battery->nominalCapacity();
        case BatteryColumn::TestCount:
            return "no data"; // TODO
        default:
            return QVariant();
    }
}

QVariant BatteriesModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    if (role != Qt::DisplayRole) return QVariant();
    if (orientation != Qt::Horizontal) return QVariant();
    
    switch (static_cast<BatteryColumn>(section)) {
        case BatteryColumn::Name:            return "Имя батареи";
        case BatteryColumn::NumCells:        return "Число аккумуляторов";
        case BatteryColumn::Mass:            return "Масса, г";
        case BatteryColumn::NominalCapacity: return "Номинальная емкость, Ач";
        case BatteryColumn::TestCount:       return "Число испытаний";
        default:                             return QString();
    }
}

Qt::ItemFlags BatteriesModel::flags(const QModelIndex& index) const
{
    if (!index.isValid()) return Qt::NoItemFlags;
    return Qt::ItemIsSelectable | Qt::ItemIsEnabled;
}

Id BatteriesModel::getBatteryId(const QModelIndex& index) const
{
    return batteriesIds[index.row()];
}

void BatteriesModel::addRow(const BatteryParams &params)
{
    Id batteryId = manager->add(params);
    int newRow = batteriesIds.size();
    beginInsertRows(QModelIndex(), newRow, newRow);
    batteriesIds.append(batteryId);
    endInsertRows();
}

void BatteriesModel::removeRow(const QModelIndex& index)
{
    Id batteryId = getBatteryId(index);
    manager->del(batteryId);
    beginRemoveRows(QModelIndex(), index.row(), index.row());
    batteriesIds.removeAt(index.row());
    endRemoveRows();
}

void BatteriesModel::editRow(const QModelIndex& index, const BatteryParams &params)
{
    Id batteryId = getBatteryId(index);
    Battery* battery = manager->get(batteryId);
    battery->setParams(params);
    emit dataChanged(index, index);
}

void BatteriesModel::refresh()
{
    beginResetModel();
    batteriesIds = manager->ids();
    endResetModel();
}


BatteriesProxyModel::BatteriesProxyModel(QObject* parent)
    : QSortFilterProxyModel(parent)
{
}

QVariant BatteriesProxyModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    return sourceModel()->headerData(section, orientation, role);
}
