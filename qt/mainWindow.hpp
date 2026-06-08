#pragma once

#include <QMainWindow>

class BatteriesManager;
class BatteriesPage;



namespace Ui {
    class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent=0);
    ~MainWindow() override;

private:
    Ui::MainWindow* ui;
    BatteriesPage* batteriesPage;
    BatteriesManager* manager;
};