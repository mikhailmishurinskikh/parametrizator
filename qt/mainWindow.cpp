#include "ui/ui_main_window.h"

#include "mainWindow.hpp"
#include "batteriesManager.hpp"
#include "batteriesPage.hpp"
#include "testsPage.hpp"


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow),
    manager(new BatteriesManager()),
    batteriesPage(new BatteriesPage(this, manager)),
    testsPage(new TestsPage(this))
{
    ui->setupUi(this);

    ui->stackedWidget->addWidget(batteriesPage);
    ui->stackedWidget->addWidget(testsPage);

    connect(ui->batteriesAction, &QAction::triggered, this, setBatteriesPage);
    connect(testsPage, &TestsPage::returnToBatteriesPage, this, setBatteriesPage);
    connect(batteriesPage, &BatteriesPage::batterySelected, this, setTestsPage);

}

MainWindow::~MainWindow()
{
    delete manager;
    delete ui;
}

void MainWindow::setTestsPage(Battery *battery)
{
    testsPage->setBattery(battery);
    ui->stackedWidget->setCurrentIndex(1);
}

void MainWindow::setBatteriesPage() {
    ui->stackedWidget->setCurrentIndex(0);
};
