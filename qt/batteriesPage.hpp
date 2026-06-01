#pragma once

#include <QWidget>

#include "batteriesManager.hpp"



namespace Ui {
    class BatteriesPage;
}

class BatteriesPage : public QWidget
{
    Q_OBJECT

public:
    explicit BatteriesPage(QWidget* parent);
    ~BatteriesPage() override;

private:
    Ui::BatteriesPage *ui;
};