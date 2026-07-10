#include "canvas.hpp"
#include "test.hpp"
#include "jkqtplotter/graphs/jkqtplines.h"


Canvas::Canvas(QWidget *parent) : JKQTPlotter(parent)
{
    hide();
    yAxis2 = getPlotter()->addSecondaryYAxis(
        new JKQTPVerticalAxis(getPlotter(), JKQTPPrimaryAxis)
    );

    auto style = getPlotter()->getCurrentPlotterStyle();
    style.graphsStyle.defaultGraphSymbols.clear();
    style.graphsStyle.defaultGraphSymbols.append(JKQTPNoSymbol);
    style.defaultFontName = "Times New Roman";
    style.defaultFontSize = 14;

    getPlotter()->setCurrentPlotterStyle(style);

    getYAxis(yAxis2)->setDrawGrid(false);

    getYAxis()->setDrawMode0(JKQTPCADMLine);
    getYAxis()->setDrawMode1(JKQTPCADMcomplete);
    getYAxis()->setDrawMode2(JKQTPCADMnone);

    getYAxis(yAxis2)->setDrawMode0(JKQTPCADMnone);
    getYAxis(yAxis2)->setDrawMode1(JKQTPCADMnone);
    getYAxis(yAxis2)->setDrawMode2(JKQTPCADMnone);

    getXAxis()->setDrawMode0(JKQTPCADMnone);
    getXAxis()->setDrawMode1(JKQTPCADMcomplete);
    getXAxis()->setDrawMode2(JKQTPCADMnone);
}

void Canvas::addTest(const Test* addedTest)
{
    test = addedTest;
    
    idMap.clear();

    JKQTPDatastore* datastore = getDatastore();
    datastore->clear();

    auto dataMap = test->load();

    for (const auto& [value, data] : dataMap.asKeyValueRange()) {
        idMap[value] = datastore->addCopiedColumn(data, valueToString(value));
    }
}

void Canvas::plotTest()
{
    if (!test) return;

    getPlotter()->clearGraphs();

    TestType type = test->type();

    switch (type) {
        case TestType::Source: {
            getXAxis()->setAxisLabel(valueToString(Value::Time));

            JKQTPXYLineGraph* voltageGraph = new JKQTPXYLineGraph(this);
            voltageGraph->setXColumn(idMap[Value::Time]);
            voltageGraph->setYColumn(idMap[Value::Voltage]);
            voltageGraph->setColor(Qt::blue);
            addGraph(voltageGraph);

            getYAxis()->setAxisLabel(valueToString(Value::Voltage));


            JKQTPXYLineGraph* currentGraph = new JKQTPXYLineGraph(this);
            currentGraph->setXColumn(idMap[Value::Time]);
            currentGraph->setYColumn(idMap[Value::Current]);
            currentGraph->setColor(Qt::red);
            currentGraph->setYAxis(yAxis2);
            addGraph(currentGraph);

            getYAxis(yAxis2)->setAxisLabel(valueToString(Value::Current));
            getYAxis(yAxis2)->setDrawMode2(JKQTPCADMcomplete);
            break;
        }

        case TestType::Curve: {
            getXAxis()->setAxisLabel(valueToString(Value::Capacity));

            JKQTPXYLineGraph* graph = new JKQTPXYLineGraph(this);
            graph->setXColumn(idMap[Value::Capacity]);
            graph->setYColumn(idMap[Value::Voltage]);
            graph->setColor(Qt::magenta);
            addGraph(graph);

            getYAxis()->setAxisLabel(valueToString(Value::Voltage));

            getYAxis(yAxis2)->setDrawMode2(JKQTPCADMnone);
            break;
        }

        case TestType::Norm_Curve: {
            getXAxis()->setAxisLabel(valueToString(Value::Norm_Capacity));

            JKQTPXYLineGraph* graph = new JKQTPXYLineGraph(this);
            graph->setXColumn(idMap[Value::Norm_Capacity]);
            graph->setYColumn(idMap[Value::Norm_Voltage]);
            graph->setColor(Qt::cyan);
            addGraph(graph);

            getYAxis()->setAxisLabel(valueToString(Value::Norm_Voltage));
            getYAxis()->setColor(Qt::cyan);

            getYAxis(yAxis2)->setDrawMode2(JKQTPCADMnone);
            break;
        }
    }

    getPlotter()->zoomToFit();
    redrawPlot();
    show();
}

void Canvas::clearCanvas()
{
    getPlotter()->clearGraphs();
    test = nullptr;
    idMap.clear();
    getDatastore()->clear();
    hide();
}
