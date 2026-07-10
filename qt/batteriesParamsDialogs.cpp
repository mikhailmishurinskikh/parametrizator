#include "batteriesParamsDialogs.hpp"
#include "batteriesManager.hpp"
#include "battery.hpp"


BatteryAddDialog::BatteryAddDialog(QWidget* parent, const BatteriesManager* manager)
    : QDialog(parent),
    ui(new Ui::BatteryAddDialog),
    manager(manager)
{
    ui->setupUi(this);
}

BatteryAddDialog::~BatteryAddDialog()
{
    delete ui;
}

BatteryParams BatteryAddDialog::params() const
{
    BatteryParams p;
    p.name = ui->nameInput->text();
    p.numCells = ui->numCellsInput->value();
    p.mass = ui->massInput->value();
    p.nominalCapacity = ui->nominalCapacityInput->value();
    return p;
}

void BatteryAddDialog::accept()
{
    BatteryParams p = params();
    Message message = p.validate(manager, QString(""));
    if (message.result == MessageResult::Success) {
        QDialog::accept();
    } else {
        QMessageBox::warning(this, "Недопустимые параметры", message.text);
    }
}



BatteryEditDialog::BatteryEditDialog(QWidget* parent, const Battery* battery, const BatteriesManager* manager)
    : QDialog(parent),
    ui(new Ui::BatteryEditDialog),
    battery(battery),
    manager(manager)
{
    ui->setupUi(this);
    
    ui->nameInput->setText(battery->name());
    ui->numCellsInput->setValue(battery->numCells());
    ui->massInput->setValue(battery->mass());
    ui->nominalCapacityInput->setValue(battery->nominalCapacity());
}

BatteryEditDialog::~BatteryEditDialog()
{
    delete ui;
}

BatteryParams BatteryEditDialog::params() const
{
    BatteryParams p;
    p.name = ui->nameInput->text();
    p.numCells = ui->numCellsInput->value();
    p.mass = ui->massInput->value();
    p.nominalCapacity = ui->nominalCapacityInput->value();
    return p;
}

void BatteryEditDialog::accept()
{
    BatteryParams p = params();
    Message message = p.validate(manager, battery->name());
    if (message.result == MessageResult::Success) {
        QDialog::accept();
    } else {
        QMessageBox::warning(this, "Недопустимые параметры", message.text);
    }
}