#include "mainWindow.hpp"
#include "ui/ui_main_window.h"
#include "batteriesManager.hpp"



MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow),
    batteriesPage(new BatteriesPage(this))
{
    ui->setupUi(this);

    ui->stackedWidget->addWidget(batteriesPage);

    connect(ui->batteriesAction, &QAction::triggered, this, [this]() {
        ui->stackedWidget->setCurrentIndex(0);
    });

}

MainWindow::~MainWindow()
{
    delete ui;
}
