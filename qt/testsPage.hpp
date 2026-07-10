#pragma once

#include "constants.hpp"

#include <QWidget>
#include <QDialog>
#include <QMessageBox>
#include <QHeaderView>


class Battery;
class TestsModel;
class TestsProxyModel;

namespace Ui {
    class TestsPage;
}

class TestsPage : public QWidget
{
    Q_OBJECT

public:
    explicit TestsPage(QWidget* parent);
    ~TestsPage();
    void setBattery(Battery* p_battery);

signals:
    void returnToBatteriesPage();

private slots:
    void addTestDialog();
    void delTest();
    void editTest();
    void separateTest();
    void plotSelected(const QModelIndex& current, const QModelIndex& previous);

private:
    void initTable();
    QModelIndex getSelectedIndex();

private:
    Ui::TestsPage* ui;
    Battery* battery;
    TestsModel* model;
    TestsProxyModel* proxy;
};