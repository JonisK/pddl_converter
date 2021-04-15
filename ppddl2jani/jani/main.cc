#include "pddl_task.h"
#include "ppddl_task.h"
#include "jani.h"

#include <iostream>

int
main()
{
    read_pddl_task(std::cin);
    build_ppddl_task(*pddl_task);
    JaniModel jani(*ppddl_task);
    jani.dump(std::cout);
    return 0;
}
