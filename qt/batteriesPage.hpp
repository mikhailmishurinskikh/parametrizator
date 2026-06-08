#pragma once

#include "constants.hpp"

#include <QWidget>
#include <QDialog>
#include <QMessageBox>
#include <QHeaderView>


class BatteriesManager;
class BatteriesModel;
class BatteriesProxyModel;
class Battery;



namespace Ui {
    class BatteriesPage;
}

class BatteriesPage : public QWidget
{
    Q_OBJECT

public:
    explicit BatteriesPage(QWidget* parent, BatteriesManager* manager);
    ~BatteriesPage();

signals:
    void batterySelected(Battery* battery);

private slots:
    void addBatteryDialog();
    void delBattery();
    void editBattery();
    void testsOpen();
    void updateCountLabel();

private:
    void initTable();
    QModelIndex getSelectedIndex();

private:
    Ui::BatteriesPage* ui;
    const BatteriesManager* manager;
    BatteriesModel* model;
    BatteriesProxyModel* proxy;
};