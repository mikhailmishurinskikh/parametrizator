#include "ui/ui_tests_page.h"


#include "testsPage.hpp"
#include "testsParamsDialogs.hpp"
#include "battery.hpp"
#include "test.hpp"
#include "testsModel.hpp"



TestsPage::TestsPage(QWidget* parent)
    : QWidget(parent)
    , ui(new Ui::TestsPage)
    , battery(nullptr)
    , model(new TestsModel(this))
    , proxy(new TestsProxyModel(this))
{
    ui->setupUi(this);

    ui->splitter->setSizes({500, 500});

    initTable();
    
    connect(ui->addTest_button, &QPushButton::clicked,
            this, &TestsPage::addTestDialog);
    connect(ui->delTest_button, &QPushButton::clicked,
            this, &TestsPage::delTest);
    connect(ui->editTest_button, &QPushButton::clicked,
            this, &TestsPage::editTest);
    connect(ui->battariesPage_button, &QPushButton::clicked,
            this, &TestsPage::returnToBatteriesPage);
    connect(ui->tableView->selectionModel(), &QItemSelectionModel::currentChanged,
            this, &TestsPage::plotSelected);
}

TestsPage::~TestsPage()
{
    delete ui;
}

void TestsPage::setBattery(Battery *p_battery)
{
    ui->canvas->clearCanvas();
    battery = p_battery;
    model->setBattery(p_battery);
    ui->batteryLabel->setText(battery->name());
}

void TestsPage::addTestDialog()
{
    TestAddDialog dialog(this, battery);

    if (dialog.exec() == QDialog::Accepted) {
        auto tests = dialog.getTests();
        for (Test* test : tests) {
            model->addRow(test);
        }
    }

    ui->canvas->clearCanvas();
}

void TestsPage::delTest()
{
    QModelIndex index = getSelectedIndex();
    if (index.isValid()) {
        model->removeRow(index);
    }
}

void TestsPage::editTest()
{
    QModelIndex index = getSelectedIndex();
    if (index.isValid()) {
        Id testId = model->getTestId(index);
        Test* test = battery->get(testId);
        TestEditDialog dialog(this, test, battery);
        
        if (dialog.exec() == QDialog::Accepted) {
            auto params = dialog.params();
            model->editRow(index, params);
        }
    }
}

void TestsPage::separateTest()
{
    // TODO
}

void TestsPage::plotSelected(const QModelIndex& current, const QModelIndex& previous)
{
    QModelIndex index = proxy->mapToSource(current);
    if (index.isValid()) {
        Id testId = model->getTestId(index);
        Test* test = battery->get(testId);

        ui->canvas->clearCanvas();
        ui->canvas->addTest(test);
        ui->canvas->plotTest();
    }
}

void TestsPage::initTable()
{
    proxy->setSourceModel(model);
    
    ui->tableView->setModel(proxy);
    ui->tableView->setSelectionBehavior(QAbstractItemView::SelectRows);
    ui->tableView->setSelectionMode(QAbstractItemView::SingleSelection);
    ui->tableView->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
}

QModelIndex TestsPage::getSelectedIndex()
{
    QModelIndexList selection = ui->tableView->selectionModel()->selectedRows();
    if (selection.isEmpty()) {
        QMessageBox::warning(this, "Не выбрано испытание",
                             "Выберите (или добавьте) испытание");
        return QModelIndex();
    }
    
    QModelIndex index = selection.first();
    return proxy->mapToSource(index);
}
