# contact: j.kiesbye@tum.de
#
# Glue code to convert a PRISM model to a PDDL domain and problem file
# this code removes and overwrites some files in the directory you run it in
# so be careful!
# One requirement for this script not included in our repo is the extendible
# Probabilistic Model Checker (ePMC). Clone and compile the standard
# distribution according to this guide:
# https://github.com/ISCAS-PMC/ePMC/wiki/Build-ePMC-under-Debian-based-Linux-Distributions
# Optional: add "prepare_plugin prism-exporter" as the second to last line
# in the file ePMC/distributions/standard/build.sh before building. Thus, you
# can also use ePMC to convert from JANI to PRISM
#
# Run with python 3 from the "pddl_converter" directory, copy the
# following line to your bash:
# python3 prism2pddl.py --input saint10_non-deterministic.prism

import argparse
from simplify_prism.simplify_prism import simplify, generate_problem
from ppddl2pddl.ppddl2pddl import convert
import os


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--input", "-i", default="saintMDP_non-deterministic.prism",
                            help="Non-deterministic PRISM file")
    arg_parser.add_argument("--verbose", "-v", default=False, help="Output debug messages? Set True or False")
    args = arg_parser.parse_args()

    input_prism = args.input
    output_prism = "saint_reduced_"
    verbose = args.verbose

    epmc_path = "~/git/ePMC/"
    levels = ["tele", "semi", "auto", "all"]

    for autonomy in levels:
        print("autonomy level: " + autonomy)

        # step 0: clean up
        print("step 0: clean up")
        os.system("rm " + output_prism + autonomy + ".prism "
                  + output_prism + autonomy + ".jani "
                  + output_prism + autonomy + "-domain.ppddl "
                  + output_prism + autonomy + "-problem.ppddl "
                  + "domain_box_cycle_" + autonomy + ".pddl "
                  + "problem_box_cycle_generated_" + autonomy + ".pddl "
                  + "solution_" + autonomy + ".txt")

        # step 1: we simplify the PRISM model
        print("step 1: we simplify the PRISM model")
        # simplify(input_prism, output_prism)
        simplify(input_prism, output_prism + autonomy + ".prism", include_rewards=False, verbose=verbose,
                 autonomy=autonomy)

        # step 2: convert the simplified PRISM model to JANI
        # note: this command uses ePMC. Find the link to the build instructions in
        #       the header comment
        print("step 2: convert the simplified PRISM model to JANI")
        my_path = os.getcwd()
        os.system("java -jar ~/git/ePMC/epmc-standard.jar jani-export --model-input-type prism "
                  "--jani-exporter-overwrite-jani-file true --model-input-files " + my_path + "/" + output_prism +
                  autonomy + ".prism --jani-exporter-jani-file-name " + my_path + "/" + output_prism + autonomy +
                  ".jani")

        # step 3: convert the JANI model to PPDDL
        # note: this command uses the PPDDL converter developed by Michaela Klauck
        #       at Uni Saarbrücken
        print("step 3: convert the JANI model to PPDDL")
        os.system("python2 jani2ppddl/jani2ppddl.py " + output_prism + autonomy + ".jani -c jani2ppddl/config.py")

        # step 4: convert the PPDDL model to PDDL
        # note: disjunctive preconditions, i.e. OR statements in the guard, result
        #       in duplicate actions for every component of the OR statement
        print("step 4: convert the PPDDL model to PDDL")
        convert(input_ppddl=output_prism + autonomy + "-domain.ppddl",
                output_pddl="domain_box_cycle_" + autonomy + ".pddl",
                verbose=False)

        # step 5: generate problem.pddl from pick_done label in the PRISM file
        print("step 5: generate problem.pddl from pick_done label in the PRISM file")
        generate_problem(input_prism,
                         input_ppddl=output_prism + autonomy + "-problem.ppddl",
                         output_pddl="problem_box_cycle_generated_" + autonomy + ".pddl",
                         label="pick_done",
                         verbose=False)

        # step 6: execute planner with the generated pddl file
        # note: a check for integrity of the generated domain file. Uses metric-ff
        #       by Jörg Hoffmann from Uni Saarbrücken
        # note: the maximum number of actions for metric-ff is 50 which is easily
        #       reached with the duplicates created for OR statements. So you need
        #       to comment some actions in the PRISM file to work around.
        print("step 6: execute planner with the generated pddl file")
        os.system("./ff21 -o domain_box_cycle_" + autonomy + ".pddl -f problem_box_cycle_generated_" + autonomy +
                  ".pddl -s 2 > solution_" + autonomy + ".txt")


if __name__ == '__main__':
    main()
