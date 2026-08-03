#include "curvesModel.hpp"

#include "battery.hpp"
#include "test.cpp"
#include "batteriesManager.hpp"

CurvesModel::CurvesModel(BatteriesManager *manager, QObject *parent)
    : QAbstractTableModel(parent)
    , manager(manager)
{
}

int CurvesModel::rowCount(const QModelIndex &parent) const
{
    if (parent.isValid()) return 0;
    return curvesIds.size();
}

int CurvesModel::columnCount(const QModelIndex &parent) const
{
    if (parent.isValid()) return 0;
    return static_cast<int>(CurveColumn::Count);
}

QVariant CurvesModel::data(const QModelIndex &index, int role) const
{
    if (!index.isValid()) return QVariant();
    if (role != Qt::DisplayRole) return QVariant();

    int row = index.row();
    auto col = static_cast<CurveColumn>(index.column());

    if (row >= curvesIds.size()) return QVariant();

    QPair<Id, Id> pair = curvesIds[row];
    const Battery* battery = manager->get(pair.first);
    const Test* test = battery->get(pair.second);

    switch (col) {
        case CurveColumn::Battery:
            return battery->name();
        case CurveColumn::Name:
            return test->name();
        case CurveColumn::NumCells:
            return battery->numCells();
        case CurveColumn::NominalCapacity:
            return battery->nominalCapacity();
        case CurveColumn::Type: {
            if (test->type() == TestType::Curve) {
                return "Разрядная кривая";
            } else {
                return "Норм. разрядная кривая";
            }
        }
        case CurveColumn::Capacity: {
            TestFloat capacity = test->capacity();
            if (capacity > 0) return capacity;
            else return "-";
        }
        case CurveColumn::EnergyCapacity: {
            TestFloat absolute = test->energyCapacity();
            TestFloat norm = test->normEnergyCapacity();
            // TODO
        }
        case CurveColumn::Label:
            return labels[row];
    }
}

QVariant CurvesModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    if (role != Qt::DisplayRole) return QVariant();
    if (orientation != Qt::Horizontal) return QVariant();
    
    switch (static_cast<CurveColumn>(section)) {
        case CurveColumn::Battery:           return "Батарея";
        case CurveColumn::Name:              return "Испытание";
        case CurveColumn::NumCells:          return "Число аккум.";
        case CurveColumn::NominalCapacity:   return "Ном. ёмкость, Ач";
        case CurveColumn::Type:              return "Тип";
        case CurveColumn::Capacity:          return "Ёмкость, Ач";
        case CurveColumn::EnergyCapacity:    return "Энергоёмкость, Втч";
        case CurveColumn::Label:             return "Имя в легенде";
        default:                             return QVariant();
    }
}

Qt::ItemFlags CurvesModel::flags(const QModelIndex &index) const
{
    if (!index.isValid()) return Qt::NoItemFlags;
    auto col = static_cast<CurveColumn>(index.column());

    if (col == CurveColumn::Label) {
        return Qt::ItemIsSelectable | Qt::ItemIsEnabled | Qt::ItemIsEditable;
    } else {
        return Qt::ItemIsSelectable | Qt::ItemIsEnabled;
    }
}

void CurvesModel::refresh()
{
    beginResetModel();
    curvesIds = manager->curves();
    endResetModel();
}

CurvesProxyModel::CurvesProxyModel(QObject *parent)
    : QSortFilterProxyModel(parent)
{
}

QVariant CurvesProxyModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    return sourceModel()->headerData(section, orientation, role);
}
