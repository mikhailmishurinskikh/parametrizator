#pragma once

#include "constants.hpp"

#include <QString>

enum class TestType {
    Curve,
    Norm_Curve,
    Source
};

struct TestParams {
    QString name;
    TestType type;
};

class Test {
public:
    Test();
    Test(const TestParams& p);
    ~Test();
    void setParams(const TestParams& p);

    QString name() const { return params.name; }
    TestType type() const { return params.type; }

private:
    TestParams params;
}