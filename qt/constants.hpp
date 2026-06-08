#pragma once

#include <QString>

enum class MessageType {
    SUCCESS,
    ERROR
};

enum class Values {
    Voltage,
    Current
    //TODO
}

struct Message {
    QString text;
    MessageType type;
};

using Id = int;