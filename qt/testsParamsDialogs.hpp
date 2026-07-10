#pragma once

#include <QDialog>
#include <QMessageBox>
#include <QDialogButtonBox>
#include <QPushButton>
#include <QFileDialog>
#include <QTemporaryDir>
#include <QFile>
#include <QFileInfo>
#include <QMap>

#include "ui/ui_test_edit_dialog.h"
#include "ui/ui_test_add_dialog.h"

class Battery;
class Test;
class TestParams;
class BatteriesManager;


namespace Ui {
    class TestsEditDialog;
    class TestsAddDialog;
}


class TestAddDialog : public QDialog
{
    Q_OBJECT

public:
    explicit TestAddDialog(QWidget* parent, const Battery* battery);
    ~TestAddDialog();
    QList<Test*> getTests() const;

public slots:
    void openDialog();
    void changeFile(int index);
    void changeType(int index);
    void accept() override;
    void setParams();
    void delTest();

private:
    Ui::TestAddDialog* ui;
    const Battery* battery;
    QTemporaryDir* storage;
    QString batteryPath;
    size_t counter;
    QMap<size_t, Test*> tests;
};



class TestEditDialog : public QDialog
{
    Q_OBJECT

public:
    explicit TestEditDialog(QWidget* parent, const Test* test, const Battery* battery);
    ~TestEditDialog();
    TestParams params() const;

public slots:
    void accept() override;

private:
    Ui::TestEditDialog* ui;
    const Battery* battery;
    const Test* test;
};