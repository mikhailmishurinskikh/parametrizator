#include "testsParamsDialogs.hpp"
#include "test.hpp"
#include "battery.hpp"
#include "bpd.hpp"



TestAddDialog::TestAddDialog(QWidget *parent, const Battery *battery)
    : QDialog(parent)
    , ui(new Ui::TestAddDialog)
    , battery(battery)
    , batteryPath(battery->getDirPath())
    , storage(new QTemporaryDir())
    , counter(0)
{
    ui->setupUi(this);

    ui->buttonBox->button(QDialogButtonBox::Ok)->setEnabled(false);

    connect(ui->addTests_button, &QPushButton::clicked, this, &TestAddDialog::openDialog);
    connect(ui->delTest_button, &QPushButton::clicked, this, &TestAddDialog::delTest);
    connect(ui->typeInput, &QComboBox::currentIndexChanged, this, &TestAddDialog::changeType);
    connect(ui->file_comboBox, &QComboBox::currentIndexChanged, this, &TestAddDialog::changeFile);
    connect(ui->nameInput, &QLineEdit::textEdited, this, [this](const QString& t) {setParams();});
}

TestAddDialog::~TestAddDialog()
{
    delete storage;
    delete ui;
}

QList<Test*> TestAddDialog::getTests() const
{
    return tests.values();
}

void TestAddDialog::openDialog()
{
    ui->file_comboBox->blockSignals(true);

    QString filter;

    QStringList filePaths = QFileDialog::getOpenFileNames(
        this,
        "Выберите файлы",
        QString(),
        "BPD файлы (*.bpd);;CSV файлы (*.csv);;Все файлы (*.*)",
        &filter
    );

    bool flag = false;
    for (QString filePath : filePaths) {

        QString tmpPath = storage->filePath("tmp" + QString::number(counter) + ".bpd");

        if (filter == "BPD файлы (*.bpd)") {

            if (!QFile::copy(filePath, tmpPath)) {
                QMessageBox::warning(this, "Непредвиденная ошибка с файлом " + filePath, "Не удалось скопировать временный файл");
                break;
            };            

        } else if (filter == "CSV файлы (*.csv)") {
            // TODO csv_to_bpd(filePath, tmpPath)
        } else if (filter == "Все файлы (*.*)") {
            QMessageBox::information(this, "Выберите тип файла", "Необходимо выбрать тип файла в окне выбора файла");
            break;
        }

        
        Test* test = new Test(new QFile(tmpPath));
        Message message = test->checkFile();

        if (message.result != MessageResult::Success) {
            QMessageBox::warning(this, "Ошибка в BPD файле: " + filePath, message.text);
            delete test;
            break;
        }

        TestParams params;
        params.name = QFileInfo(filePath).fileName();
        params.type = test->possibleTypes()[0].second;
        test->setParams(params);
        tests[counter] = test;

        ui->file_comboBox->addItem(filePath, QVariant::fromValue(counter));

        flag = true;
        counter ++;
    }

    if (flag) {
        ui->buttonBox->button(QDialogButtonBox::Ok)->setEnabled(true);
        changeFile(ui->file_comboBox->count() - 1);
    }

    ui->file_comboBox->blockSignals(false);
}

void TestAddDialog::changeFile(int index)
{
    if (index == -1) return;

    ui->typeInput->blockSignals(true);

    size_t number = ui->file_comboBox->currentData().value<size_t>();
    Test* test = tests[number];

    ui->nameInput->setText(test->name());
    ui->typeInput->clear();
    for (const auto& info : test->possibleTypes()) {
        ui->typeInput->addItem(info.first, QVariant::fromValue(info.second));
        if (info.second == test->type()) {
            ui->typeInput->setCurrentIndex(ui->typeInput->count() - 1);
        }
    }

    ui->typeInput->blockSignals(false);

    ui->canvas->addTest(test);
    ui->canvas->plotTest();

}

void TestAddDialog::changeType(int index)
{
    if (index == -1) return;

    setParams();
    ui->canvas->plotTest();
}

void TestAddDialog::accept()
{
    for (const auto& [number, test] : tests.asKeyValueRange()) {
        QStringList otherNames = battery->names();
        for (const auto& otherTest : tests.values()) {
            if (otherTest != test) {
                otherNames.append(otherTest->name());
            }
        }

        Message message = test->getParams().validate(battery, otherNames);
        if (message.result != MessageResult::Success) {
            QMessageBox::warning(this, "Недопустимое название" + test->name(), message.text);
            return;
        }
    }

    QDialog::accept();
}

void TestAddDialog::setParams()
{
    size_t number = ui->file_comboBox->currentData().value<size_t>();
    Test* test = tests[number];

    TestParams params;
    params.type = ui->typeInput->currentData().value<TestType>();
    params.name = ui->nameInput->text();
    test->setParams(params);
}

void TestAddDialog::delTest()
{
    ui->canvas->clearCanvas();
    int currentIndex = ui->file_comboBox->currentIndex();
    if (currentIndex == -1) return;

    size_t number = ui->file_comboBox->currentData().value<size_t>();
    Test* test = tests[number];
    tests.remove(number);

    delete test;
    ui->file_comboBox->removeItem(currentIndex);
    ui->typeInput->clear();
    ui->nameInput->clear();
}

TestEditDialog::TestEditDialog(QWidget* parent, const Test* test, const Battery* battery)
    : QDialog(parent)
    , ui(new Ui::TestEditDialog)
    , test(test)
    , battery(battery)
{
    ui->setupUi(this);
    
    for (const auto& info : test->possibleTypes()) {
        ui->typeInput->addItem(info.first, QVariant::fromValue(info.second));
        if (info.second == test->type()) {
            ui->typeInput->setCurrentIndex(ui->typeInput->count() - 1);
        }
    }
    ui->nameInput->setText(test->name());
}

TestEditDialog::~TestEditDialog()
{
    delete ui;
}

TestParams TestEditDialog::params() const
{
    TestParams p;
    p.name = ui->nameInput->text();
    p.type = ui->typeInput->currentData().value<TestType>();
    return p;
}

void TestEditDialog::accept()
{
    TestParams p = params();
    QStringList otherNames = battery->names();
    otherNames.removeOne(test->name());
    Message message = p.validate(battery, otherNames);
    if (message.result == MessageResult::Success) {
        QDialog::accept();        
    } else {
        QMessageBox::warning(this, "Недопустимое название", message.text);
    }
}