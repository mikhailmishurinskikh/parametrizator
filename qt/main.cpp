#include <QApplication>

#include <QDebug>
#include <cstdio>

#include "mainWindow.hpp"


int main(int argc, char* argv[]) {
    qInstallMessageHandler([](QtMsgType type, const QMessageLogContext &context, const QString &msg) {
        // Пишем в stderr
        fprintf(stderr, "%s\n", qPrintable(msg));
        fflush(stderr);
    });

    QApplication app(argc, argv);
    
    MainWindow window;
    window.show();
    
    return app.exec();
}