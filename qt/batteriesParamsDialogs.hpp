#pragma once

#include <QDialog>

#include "batteriesManager.hpp"

#include "ui/ui_battery_add_dialog.h"
#include "ui/ui_battery_edit_dialog.h"


namespace Ui {
    class BatteriesAddDialog;
    class BatteriesEditDialog;
}


class BatteryAddDialog : public QDialog
{
    Q_OBJECT

public:
    explicit BatteryAddDialog(QWidget* parent, const BatteriesManager* manager);
    ~BatteryAddDialog();
    BatteryParams params() const;

public slots:
    void accept() override;

private:
    Ui::BatteryAddDialog* ui;
    const BatteriesManager* manager;
};


class BatteryEditDialog : public QDialog
{
    Q_OBJECT

public:
    explicit BatteryEditDialog(QWidget* parent, const Battery* battery, const BatteriesManager* manager);
    ~BatteryEditDialog();
    BatteryParams params() const;

public slots:
    void accept() override;

private:
    Ui::BatteryEditDialog* ui;
    const Battery* battery;
    const BatteriesManager* manager;
};