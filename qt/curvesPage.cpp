#include "ui/ui_curves_page.h"

#include "curvesPage.hpp"

CurvesPage::CurvesPage(QWidget *parent, BatteriesManager *manager)
    : QWidget(parent)
    , ui(new Ui::CurvesPage)
    , manager(manager)
    , model(new CurvesModel(manager, this))
    , proxy(new CurvesProxyModel(this))
{
    ui->setupUi(this);
    initTable();
}

CurvesPage::~CurvesPage()
{
    delete ui;
}

void CurvesPage::initTable()
{
    proxy->setSourceModel(model);
    ui->tableView->setModel(proxy);
    
    ui->tableView->setSelectionBehavior(QAbstractItemView::SelectRows);
    ui->tableView->setSelectionMode(QAbstractItemView::SingleSelection);
    ui->tableView->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
}
