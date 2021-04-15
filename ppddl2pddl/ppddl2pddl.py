# contact: j.kiesbye@tum.de
#
# remove all probabilistic effects from a PPDDL domain file to convert it to
# PDDL. The first outcome of the probailistic statement will be copied to the
# PDDL domain
# run it via bash ("python3 ppddl2pddl.py") or import it into another python
# script to change the arguments

import regex

input_ppddl = "sample.ppddl"
output_pddl = "converted.pddl"
verbose = False

def convert(input_ppddl, output_pddl, verbose):
    probabilistic_statement = False
    first_effect_over = False
    start_probabilistic = regex.compile("\\t\\t\\tprobabilistic")
    with open(input_ppddl) as ppddl, open(output_pddl, 'w') as pddl:
        lines = ppddl.readlines()
        for line in lines:
            print(line) if verbose else None
            # Shorten the action name
            action_name = regex.search("(?<=\(:action )\w+", line)
            if action_name:
                action_name = line[action_name.regs[0][0]:
                                      action_name.regs[0][1]]
                print("Old action name: " + action_name) if verbose else None
                shortened_action_name = regex.search("\w+(?=_task_planner)", action_name)
                shortened_action_name = action_name[shortened_action_name.regs[0][0]:
                                   shortened_action_name.regs[0][1]]
                print("Shortened action name: " + shortened_action_name) if verbose else None
                line = regex.sub("(?<=\(:action )\w+", shortened_action_name, line, count=1)
            # Remove probabilistic effects
            if probabilistic_statement == False and \
                    regex.search("^\t\t:effect [(]", line):
                pddl.write("\t\t:effect\n")
            elif probabilistic_statement == False and \
                    start_probabilistic.search(line):
                # we are in a probabilistic statement
                probabilistic_statement = True
            elif probabilistic_statement:
                if regex.search("			[0-9.]+", line):
                    pass
                elif regex.search("^\t\t[)]", line):
                    probabilistic_statement = False
                    first_effect_over = False
                elif regex.search("^\t\t\t\t[)]", line) and\
                        first_effect_over == False:
                    first_effect_over = True
                    pddl.write(line)
                elif first_effect_over:
                    pass
                else:
                    pddl.write(line)
            else:
                pddl.write(line)

if __name__ == "__main__":
    convert()


