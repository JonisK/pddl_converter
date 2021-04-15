# contact: j.kiesbye@tum.de
#
# reduce a non-deterministic PRISM model to a non-deterministic one, remove
# all modules but the "task_planner". The option "--rewards" [= True/False]
# will include all rewards, labels, and initial conditions in the destination
# if set to True.
# run with python 3 from the "conversion-tools" directory, copy the
# following line to your bash
# python3 simplify_prism/simplify_prism.py --input saintMDP_non-deterministic.prism --output saintMDP_compact.prism --rewards True --autonomy auto

import argparse
import regex


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--input", "-i", default="saintMDP_non-deterministic.prism", help="Non-deterministic PRISM file")
    arg_parser.add_argument("--output", "-o", default="saintMDP_compact.prism", help="Simplified PRISM file")
    arg_parser.add_argument("--rewards", "-r", default=True, help="Include rewards? Set True or False")
    arg_parser.add_argument("--verbose", "-v", default=False, help="Output debug messages? Set True or False")
    arg_parser.add_argument("--autonomy", "-a", default="auto", help="Autonomy level: tele, semi, or auto")
    args = arg_parser.parse_args()

    input_prism = args.input
    output_prism = args.output
    include_rewards = args.rewards
    verbose = args.verbose
    autonomy = args.autonomy

    simplify(input_prism, output_prism, include_rewards, verbose, autonomy)


def check_autonomy(autonomy, current_action, verbose):
    if autonomy == "auto" and (regex.search("^\[semi", current_action) or regex.search("^\[manual", current_action) or regex.search("^\[technician", current_action)):
        print("Action " + current_action + " does not belong to autonomy level " + autonomy) if verbose else None
        return False
    elif autonomy == "semi" and (regex.search("^\[manual", current_action) or regex.search("^\[technician", current_action)):
        print("Action " + current_action + " does not belong to autonomy level " + autonomy) if verbose else None
        return False
    elif autonomy == "tele" and regex.search("^\[technician", current_action):
        print("Action " + current_action + " does not belong to autonomy level " + autonomy) if verbose else None
        return False
    else:
        print("Action " + current_action + " belongs to autonomy level " + autonomy) if verbose else None
        return True


def simplify(input_prism, output_prism, include_rewards, verbose, autonomy):
    beginning_of_file = True
    in_module_task_planner = False
    in_rewards = False
    label_valid = True
    in_init = False
    previous_action = "empty"
    roll_dice = False
    action_name = "empty action"
    guard_roll_dice = "empty guard"
    remove_variables = ["dice",
                        "num_attempts",
                        "req_box_cycles",
                        "req_pick_cycles",
                        "box_detectability_observed",
                        "item_detectability_observed",
                        "readability_observed",
                        "graspability_observed",
                        "movability_observed"]
    replace_values = {"true_conveyor_state": 2,
                      "true_sorter_state": 1,
                      "true_gripper_state": 1,
                      "true_obstacle_state": 0,
                      "true_item_state": 0}
    remove_variables_patterns = remove_variables.copy()
    for index in range(len(remove_variables)):
        remove_variables_patterns[index] = "([ ]*&[ ]*)*" + remove_variables[index] + "[ ]*(=|>=|<=|>|<|!=)[ ]*[0-9]+"
    # add_variables = ["detectability",
    #                  "readability",
    #                  "graspability"]
    guard_pattern = "(?<=\[\w*\][ ]*)([^ ].*[^ ])(?=[ ]*->)"
    effects_pattern = "(?<=->[ ]*)([^ ].*)(?=;)"
    with open(input_prism) as source, open(output_prism, 'w') as destination:
        lines = source.readlines()
        for line in lines:
            print(line[0:-1]) if verbose else None
            if regex.search("module task_planner", line):
                print("Found the beginning of the task planner module") if verbose else None
                in_module_task_planner = True
                beginning_of_file = False
                destination.write(line)
                # # Include the observed variables
                # for index in range(len(add_variables)):
                #     destination.write("        " + add_variables[index] + " : [0..3];\n")
            elif in_module_task_planner:
                if regex.search("endmodule", line):
                    print("Found the end of the task planner module") if verbose else None
                    in_module_task_planner = False
                    destination.write(line + "\n")
                    if not include_rewards:
                        break
                elif regex.search("dice[ ]*:[ ]*\[0..[0-9]+\]", line):
                    print("Discarding dice definition") if verbose else None
                elif regex.search("num_attempts[ ]*:[ ]*\[0..[0-9]+\]", line):
                    print("Discarding num_attempts definition") if verbose else None
                elif regex.search("\[initialize\]", line):
                    print("Discarding [initialize] action") if verbose else None
                else:
                    current_action = regex.search("\[\w+\]", line)
                    if current_action:
                        current_action = line[current_action.regs[0][0]:
                                             current_action.regs[0][1]]
                        print("Label: " + current_action) if verbose else None
                        # Removing unneeded variables in the guard
                        # Find the guard
                        guard = regex.search(guard_pattern, line)
                        guard = line[guard.regs[0][0]:guard.regs[0][1]]
                        for index in range(len(remove_variables_patterns)):
                            if regex.search(remove_variables_patterns[index],guard):
                                print("Removing " + remove_variables[index] + " variable in the guard") if verbose else None
                                guard = regex.sub(remove_variables_patterns[index], "", guard, count=1)
                                if not guard:
                                    guard = "true"
                        line = regex.sub(guard_pattern, guard, line, count=1)

                        # Removing unneeded variables in the effects
                        # Find the effects
                        effects = regex.search(effects_pattern, line)
                        effects = line[effects.regs[0][0]:effects.regs[0][1]]
                        print("Effects: " + effects) if verbose else None
                        # if regex.search("([ ]*&[ ]*)\(dice'[ ]*=[ ]*[0-9]+\)+",
                        #                 effects):
                        #     print("Removing dice statement in effects") if verbose else None
                        #     effects = regex.sub(
                        #         "([ ]*&[ ]*)\(dice'[ ]*=[ ]*[0-9]+\)+", "",
                        #         effects, count=1)
                        # Remove references to remove_variables
                        # for variable in remove_variables:
                        #     if regex.search(variable, effects):
                        #         print("Replacing variable " + variable + \
                        #               " with value " + \
                        #               str(replace_values[variable])) \
                        #             if verbose else None
                        #         effects = regex.sub(variable, str(
                        #             replace_values[variable]), effects,
                        #                             count=1)
                        # Remove references to remove_variables
                        for variable in remove_variables:
                            if regex.search(variable, effects):
                                print("Removing variable " + variable) \
                                    if verbose else None
                                effects = regex.sub("[ ]*&[ ]*\([ ]*" + variable + "'[ ]*=[ ]*\d+[ ]*\)", "", effects,
                                                    count=1)
                        # Replace references to replace_variables with default values
                        for variable in replace_values:
                            if regex.search(variable, effects):
                                    print("Replacing variable " + variable + \
                                          " with value " + \
                                          str(replace_values[variable])) \
                                        if verbose else None
                                    effects = regex.sub(variable, str(
                                        replace_values[variable]), effects,
                                                        count=1)
                        print("Effects: " + effects) if verbose else None
                        line = regex.sub(effects_pattern, effects, line,
                                         count=1)
                        print("Line: " + line) if verbose else None

                        if regex.search("_roll_dice", current_action) and not roll_dice:
                            print("Entering a roll_dice cluster") if verbose else None
                            roll_dice = True
                            # Find out the name
                            action_name = regex.search("\w+(?=_roll_dice)", current_action)
                            action_name = current_action[action_name.regs[0][0]:action_name.regs[0][1]]
                            print("Action name is " + action_name) if verbose else None
                            # Find the guard
                            guard_roll_dice = regex.search("(?<=]).+(?=->)", line)  # copies spaces
                            # guard_roll_dice = regex.search("\w+=\d+([ ]*&[ ]*\w+=\d+)*", line)  # does not include parantheses and pipes
                            guard_roll_dice = line[guard_roll_dice.regs[0][0]:guard_roll_dice.regs[0][1]]
                            print("The guard is " + guard_roll_dice) if verbose else None
                        elif regex.search("_roll_dice", current_action) and roll_dice:
                            print("Discarding duplicate roll_dice action") if verbose else None
                        elif regex.search("_unsuccessful", current_action):
                            print("Discarding unsuccessful roll_dice action") if verbose else None
                        elif regex.search("_observation]", current_action):
                            print("Discarding observation roll_dice action") if verbose else None
                        elif roll_dice and regex.search("_successful", current_action) and check_autonomy(autonomy, current_action, verbose):
                            print("Found the successful action. Writing simplified action to destination") if verbose else None
                            roll_dice = False
                            # Find out the successful effects
                            effects_roll_dice = regex.search(effects_pattern, line)
                            effects_roll_dice = line[effects_roll_dice.regs[0][0]:effects_roll_dice.regs[0][1]]
                            if regex.search("[ ]*&[ ]*\(dice'[ ]*=[ ]*[0-9]\)+", effects_roll_dice):
                                print("Removing dice statement in effects") if verbose else None
                                effects = regex.sub("[ ]*&[ ]*\(dice'[ ]*=[ ]*[0-9]\)+", "", effects_roll_dice, count=1)
                            # Remove references to remove_variables
                            for variable in remove_variables:
                                if regex.search(variable, effects):
                                    print("Replacing variable " + variable + " with value " + replace_values[variable]) if verbose else None
                                    effects = regex.sub(variable, replace_values[variable], effects_roll_dice, count=1)
                            print("Writing the action:" + "        [" + action_name + "]" + guard_roll_dice + "-> " +
                                  effects_roll_dice + ";\n") if verbose else None
                            destination.write("        [" + action_name + "]" + guard_roll_dice + "-> " + effects_roll_dice + ";\n")
                        elif not roll_dice and current_action == previous_action:
                            print("Discarding this line because it starts with the same label as the last one") if verbose else None
                        elif not roll_dice and check_autonomy(autonomy, current_action, verbose):
                            print("Copying to the destination") if verbose else None
                            destination.write(line)
                        previous_action = current_action
                    else:
                        print("Copying to the destination") if verbose else None
                        destination.write(line)
            elif beginning_of_file:
                print("We are at the beginning of the file") if verbose else None
                destination.write(line)
            elif regex.search("^rewards", line):
                print("Entering a rewards section") if verbose else None
                in_rewards = True
                destination.write(line)
            elif in_rewards:
                current_action = regex.search("\[\w+\]", line)
                if current_action:
                    current_action = line[current_action.regs[0][0]:current_action.regs[0][1]]
                    print("Label: " + current_action) if verbose else None
                    if regex.search("_roll_dice", current_action):
                        action_name = regex.search("\w+(?=_roll_dice)", current_action)
                        action_name = current_action[action_name.regs[0][0]:action_name.regs[0][1]]
                        print("Action name is " + action_name) if verbose else None
                        line = regex.sub("(?<=\[)(\w*)(?=\])", action_name, line, count=1)
                        destination.write(line)
                    # elif regex.search("_roll_dice", current_action):
                    #     print("Discarding duplicate roll_dice action") if verbose else None
                    elif regex.search("_unsuccessful", current_action):
                        print("Discarding unsuccessful roll_dice action") if verbose else None
                    elif regex.search("_observation", current_action):
                        print("Discarding observation roll_dice action") if verbose else None
                    elif regex.search("_successful", current_action):
                        print("Discarding successful roll_dice action") if verbose else None
                    elif regex.search("\[initialize\]", current_action):
                        print("Discarding initialize action") if verbose else None
                    # elif current_action == previous_action:
                    #     print("Discarding this line because it starts with the same label as the last one") if verbose else None
                    else:
                        print("Copying to the destination") if verbose else None
                        destination.write(line)
                    previous_action = current_action
                elif regex.search("^endrewards", line):
                    print("Leaving the rewards section") if verbose else None
                    in_rewards = False
                    destination.write(line + "\n")
                else:
                    print("Copying to the destination") if verbose else None
                    destination.write(line)
            elif regex.search("^label", line):
                print("Found a label") if verbose else None
                for variable in remove_variables:
                    if regex.search(variable, line):
                        label_valid = False
                if label_valid:
                    destination.write(line)
            elif not in_init and regex.search("^init", line):
                print("Found an init line") if verbose else None
                in_init = True
                for index in range(len(remove_variables_patterns)):
                    if regex.search(remove_variables_patterns[index], line):
                        print("Removing " + remove_variables[index] + " variable in the init line") if verbose else None
                        line = regex.sub(remove_variables_patterns[index], "", line, count=1)
                destination.write("\n" + line)
                if regex.search("endinit", line):
                    in_init = False
            elif in_init:
                if regex.search("& dice=\d+", line):
                    pass
                else:
                    for index in range(len(remove_variables_patterns)):
                        if regex.search(remove_variables_patterns[index], line):
                            print("Removing " + remove_variables[index] + " variable in the init line") if verbose else None
                            line = regex.sub(remove_variables_patterns[index], "", line, count=1)
                    destination.write(line)
                    if regex.search("endinit", line):
                        in_init = False
            else:
                print("Discarding this one") if verbose else None
            print() if verbose else None


def generate_problem(input_prism, input_ppddl, output_pddl, label, verbose=False):
    specifiers = []
    with open(input_prism) as source:
        lines = source.readlines()
        for line in lines:
            if regex.search("^label", line):
                # see if this is the correct label
                if regex.search(label, line):
                    # extract all goal specifiers
                    specifiers = regex.findall("(\w+[ ]*=[ ]*\d+)", line)
                    break
    with open(input_ppddl) as source, open(output_pddl, 'w') as destination:
        lines = source.readlines()
        for line in lines:
            if regex.search("(value warehouse n0)", line):
                line = regex.sub("(n0)", "n2", line)
                destination.write(line)
            elif regex.search("(fulfiled goal_condition)", line):
                # we are in the goal statement and can add the goal specifiers
                if len(specifiers) > 1:
                    destination.write("        (and\n")
                for specifier in specifiers:
                    variable = regex.search("\w+(?=[ ]*=[ ]*\d+)", specifier)
                    variable = specifier[variable.regs[0][0]:variable.regs[0][1]]
                    value = regex.search("(?<=\w+[ ]*=[ ]*)\d+", specifier)
                    value = specifier[value.regs[0][0]:value.regs[0][1]]
                    destination.write("            (value " + variable + " n" + value + ")\n")
                if len(specifiers) > 1:
                    destination.write("        )\n")
            else:
                destination.write(line)


if __name__ == '__main__':
    main()