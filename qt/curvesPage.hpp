#pragma once

#include "constants.hpp"

#include <QWidget>
#include <QDialog>
#include <QMessageBox>
#include <QHeaderView>


class BatteriesManager;
class CurvesModel;
class CurvesProxyModel;


namespace Ui {
    class CurvesPage;
}

class CurvesPage : public QWidget
{
    Q_OBJECT

public:
    explicit CurvesPage(QWidget* parent, BatteriesManager* manager);
    ~CurvesPage();

private:
    void initTable();

private:
    Ui:CurvesPage* ui;
    const BatteriesManager* manager;
    CurvesModel* model;
    CurvesProxyModel* proxy;
};