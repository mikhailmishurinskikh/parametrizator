#include "testsModel.hpp"
#include "battery.hpp"
#include "test.hpp"

TestsModel::TestsModel(QObject *parent)
    : QAbstractTableModel(parent)
{}

int TestsModel::rowCount(const QModelIndex &parent) const
{
    if (parent.isValid()) return 0;
    return testsIds.size();
}

int TestsModel::columnCount(const QModelIndex &parent) const
{
    if (parent.isValid()) return 0;
    return static_cast<int>(TestColumn::Count);
}

QVariant TestsModel::data(const QModelIndex &index, int role) const
{
    if (!index.isValid()) return QVariant();
    if (role != Qt::DisplayRole) return QVariant();

    int row = index.row();
    auto col = static_cast<TestColumn>(index.column());

    if (row >= testsIds.size()) return QVariant();

    Id testId = testsIds[row];
    const Test* test = battery->get(testId);

    switch (col) {
        case TestColumn::Name:
            return test->name();
        case TestColumn::Type:
            return testTypeToString(test->type());
        default:
            return QVariant();
    }
}

QVariant TestsModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    if (role != Qt::DisplayRole) return QVariant();
    if (orientation != Qt::Horizontal) return QVariant();
    
    switch (static_cast<TestColumn>(section)) {
        case TestColumn::Name:  return "Имя испытания";
        case TestColumn::Type:  return "Тип испытания";
        default:                return QString();
    }
}

Qt::ItemFlags TestsModel::flags(const QModelIndex &index) const
{
    if (!index.isValid()) return Qt::NoItemFlags;
    return Qt::ItemIsSelectable | Qt::ItemIsEnabled;
}

Id TestsModel::getTestId(const QModelIndex &index) const
{
    return testsIds[index.row()];
}

void TestsModel::setBattery(Battery *p_battery)
{
    battery = p_battery;
    refresh();
}

void TestsModel::addRow(Test* test)
{
    Id testId = battery->add(test);
    int newRow = testsIds.size();
    beginInsertRows(QModelIndex(), newRow, newRow);
    testsIds.append(testId);
    endInsertRows();
}

void TestsModel::removeRow(const QModelIndex &index)
{
    Id testId = getTestId(index);
    battery->del(testId);
    beginRemoveRows(QModelIndex(), index.row(), index.row());
    testsIds.removeAt(index.row());
    endRemoveRows();
}

void TestsModel::editRow(const QModelIndex &index, const TestParams &params)
{
    Id testId = getTestId(index);
    Test* test = battery->get(testId);
    test->setParams(params);
}

void TestsModel::refresh()
{
    beginResetModel();
    testsIds = battery->ids();
    endResetModel();
}

TestsProxyModel::TestsProxyModel(QObject *parent)
    : QSortFilterProxyModel(parent)
{
}

QVariant TestsProxyModel::headerData(int section, Qt::Orientation orientation, int role) const
{
    return sourceModel()->headerData(section, orientation, role);
}
