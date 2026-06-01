#include "batteriesPage.hpp"
#include "ui/ui_batteries.h"

BatteriesPage::BatteriesPage(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::BatteriesPage)
{
    ui->setupUi(this);
}

BatteriesPage::~BatteriesPage()
{
    delete ui;
}
