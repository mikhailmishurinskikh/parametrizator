#include "ui/ui_batteries_page.h"

#include "batteriesPage.hpp"
#include "batteriesParamsDialogs.hpp"
#include "batteriesModel.hpp"
#include "battery.hpp"
#include "batteriesManager.hpp"



BatteriesPage::BatteriesPage(QWidget* parent, BatteriesManager* manager)
    : QWidget(parent)
    , ui(new Ui::BatteriesPage)
    , manager(manager)
    , model(new BatteriesModel(manager, this))
    , proxy(new BatteriesProxyModel(this))
{
    ui->setupUi(this);
    initTable();
    updateCountLabel();
    
    connect(ui->addBattery_button, &QPushButton::clicked,
            this, &BatteriesPage::addBatteryDialog);
    connect(ui->delBattery_button, &QPushButton::clicked,
            this, &BatteriesPage::delBattery);
    connect(ui->editBattery_button, &QPushButton::clicked,
            this, &BatteriesPage::editBattery);
    connect(ui->testsOpen_button, &QPushButton::clicked,
            this, &BatteriesPage::testsOpen);
    connect(model, &BatteriesModel::countChanged,
            this, &BatteriesPage::updateCountLabel);
}

BatteriesPage::~BatteriesPage()
{
    delete ui;
}

void BatteriesPage::initTable()
{
    proxy->setSourceModel(model);
    
    ui->tableView->setModel(proxy);
    ui->tableView->setSelectionBehavior(QAbstractItemView::SelectRows);
    ui->tableView->setSelectionMode(QAbstractItemView::SingleSelection);
    ui->tableView->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
}

QModelIndex BatteriesPage::getSelectedIndex()
{
    QModelIndexList selection = ui->tableView->selectionModel()->selectedRows();
    if (selection.isEmpty()) {
        QMessageBox::warning(this, "Не выбрана батарея",
                             "Выберите (или добавьте) батарею");
        return QModelIndex();
    }
    
    QModelIndex index = selection.first();
    return proxy->mapToSource(index);
}

void BatteriesPage::addBatteryDialog()
{
    BatteryAddDialog dialog(this, manager);
    if (dialog.exec() == QDialog::Accepted) {
        auto params = dialog.params();
        model->addRow(params);
    }
}

void BatteriesPage::delBattery()
{
    QModelIndex index = getSelectedIndex();
    if (index.isValid()) {
        model->removeRow(index);
    }
}

void BatteriesPage::editBattery()
{
    QModelIndex index = getSelectedIndex();
    if (index.isValid()) {
        Id batteryId = model->getBatteryId(index);
        Battery* battery = manager->get(batteryId);
        BatteryEditDialog dialog(this, battery, manager);
        
        if (dialog.exec() == QDialog::Accepted) {
            auto params = dialog.params();
            model->editRow(index, params);
        }
    }
}

void BatteriesPage::testsOpen()
{
    QModelIndex index = getSelectedIndex();
    if (index.isValid()) {
        Id batteryId = model->getBatteryId(index);
        Battery* battery = manager->get(batteryId);
        emit batterySelected(battery);
    }
}

void BatteriesPage::updateCountLabel()
{
    auto [numBatteries, numTests] = manager->count();
    ui->countLabel->setText(QString("Всего батарей: %1\nВсего испытаний: %2")
                            .arg(numBatteries).arg(numTests));
}