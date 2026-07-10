#pragma once

#include <QMainWindow>

class BatteriesManager;
class Battery;
class BatteriesPage;
class TestsPage;

namespace Ui {
    class MainWindow;
}


class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent=0);
    ~MainWindow() override;

private slots:
    void setBatteriesPage();
    void setTestsPage(Battery* battery);

private:
    BatteriesManager* manager;
    Ui::MainWindow* ui;
    BatteriesPage* batteriesPage;
    TestsPage* testsPage;
};