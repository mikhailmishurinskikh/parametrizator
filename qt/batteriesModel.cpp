#include "batteriesModel.hpp"

BatteriesModel::BatteriesModel(const BatteriesManager& manager, QObject* parent)
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
    if (!index.isValid()) return QString();
    if (role != Qt::DisplayRole) return QString();
    
    int row = index.row();
    auto col = static_cast<BatteryColumn>(index.column());
    
    if (row >= batteriesIds.size()) return QString();
    
    Id batteryId = batteriesIds[row];
    const Battery& battery = manager.get(batteryId);
    
    switch (col) {
        case BatteryColumn::Name:
            return battery.name();
        case BatteryColumn::NumCells:
            return QString::number(battery.numCells());
        case BatteryColumn::Mass:
            return QString::number(battery.mass(), 'f', 1);
        case BatteryColumn::TestCount:
            return QString::number(1); // TODO
        default:
            return QString();
    }
}

QVariant BatteriesModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    if (role != Qt::DisplayRole) return QString();
    if (orientation != Qt::Horizontal) return QString();
    
    switch (static_cast<BatteryColumn>(section)) {
        case BatteryColumn::Name:      return "Имя батареи";
        case BatteryColumn::NumCells:  return "Число аккумуляторов";
        case BatteryColumn::Mass:      return "Масса, г";
        case BatteryColumn::TestCount: return "Число испытаний";
        default:                       return QString();
    }
}

Qt::ItemFlags BatteriesModel::flags(const QModelIndex& index) const
{
    if (!index.isValid()) return Qt::NoItemFlags;
    return Qt::ItemIsSelectable | Qt::ItemIsEnabled;
}

Id BatteriesModel::getBatteryId(int row) const
{
    if (row < 0 || row >= batteriesIds.size()) return 0;
    return batteriesIds[row];
}

void BatteriesModel::sort(int column, Qt::SortOrder order)
{
    sortColumn = static_cast<BatteryColumn>(column);
    sortOrder = order;
    
    bool reverse = (order == Qt::DescendingOrder);
    
    auto sortLambda = [this, reverse](Id a, Id b) {
        const Battery& ba = manager.get(a);
        const Battery& bb = manager.get(b);
        
        switch (sortColumn) {
            case BatteryColumn::Name:
                return reverse ? ba.name() > bb.name() : ba.name() < bb.name();
            case BatteryColumn::NumCells:
                return reverse ? ba.numCells() > bb.numCells() : ba.numCells() < bb.numCells();
            case BatteryColumn::Mass:
                return reverse ? ba.mass() > bb.mass() : ba.mass() < bb.mass();
            // case BatteryColumn::TestCount:
            //     return reverse ? ba.testCount() > bb.testCount() : ba.testCount() < bb.testCount();
            default:
                return false;
        }
    };
    
    std::sort(batteriesIds.begin(), batteriesIds.end(), sortLambda);
    emit layoutChanged();
}

void BatteriesModel::refresh()
{
    beginResetModel();
    batteriesIds = manager.ids();
    sort(static_cast<int>(sortColumn), sortOrder);
    endResetModel();
}