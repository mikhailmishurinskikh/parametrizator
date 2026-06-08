#include "ui/ui_main_window.h"

#include "mainWindow.hpp"
#include "batteriesManager.hpp"
#include "batteriesPage.hpp"




MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow),
    manager(new BatteriesManager()),
    batteriesPage(new BatteriesPage(this, manager))
{
    ui->setupUi(this);

    ui->stackedWidget->addWidget(batteriesPage);

    connect(ui->batteriesAction, &QAction::triggered, this, [this]() {
        ui->stackedWidget->setCurrentIndex(0);
    });

}

MainWindow::~MainWindow()
{
    delete manager;
    delete ui;
}
