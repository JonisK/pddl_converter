#include "utils.h"
#include <iostream>
#include <cstdlib>

std::string
exit_code_to_string(ExitCode code)
{
    switch (code) {
    case (ExitCode::INPUT_ERROR):
        return "Input error";
    case (ExitCode::UNSUPPORTED_FEATURE_REQUESTED):
        return "Unsupported feature requested";
    }
    return "";
}

void
exit_with(ExitCode code)
{
    std::cerr << exit_code_to_string(code) << std::endl;
    exit(static_cast<int>(code));
}
