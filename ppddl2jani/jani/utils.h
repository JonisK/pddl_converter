#ifndef UTILS_H
#define UTILS_H

#include <string>

enum class ExitCode {
    INPUT_ERROR = 1,
    UNSUPPORTED_FEATURE_REQUESTED = 2,
};

std::string exit_code_to_string(ExitCode code);

void exit_with(ExitCode code);

#endif
