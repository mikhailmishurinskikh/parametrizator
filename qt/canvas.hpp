#pragma once

#include "constants.hpp"
#include "jkqtplotter/jkqtplotter.h"


class Test;
class JKQTPlotter;


class Canvas : public JKQTPlotter {
    Q_OBJECT

public:
    explicit Canvas(QWidget* parent);

    void addTest(const Test* test);
    void plotTest();
    void clearCanvas();

private:
    const Test* test;
    QMap<Value, size_t> idMap;

    JKQTPCoordinateAxisRef yAxis2;
};