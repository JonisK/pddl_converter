#!/usr/bin/python

import subprocess
import argparse
import os
import sys

P = os.path.dirname(os.path.realpath(__file__))

def get_jani_exec():
    exe = None
    if os.name == "nt":
        exe = "sas2jani.exe"
    else:
        exe = "sas2jani"
    res = os.path.join(P, "jani", exe)
    if not os.path.exists(res):
        sys.stderr.write("%s was not found\n" % res)
        sys.stderr.write("Try to run make in %s\n" % os.path.dirname(res))
        sys.exit(1)
    return res

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("domain", nargs="?", default=None, help="Path to PPDDL domain file")
    p.add_argument("problem", help="Path to PPDDL problem file")
    p.add_argument("--jani", help="Path to file where the JANI model should be stored. Defaults to {problem}.jani", default=None)

    args = p.parse_args()
    if args.domain is None:
        prob = os.path.basename(args.problem)
        i = prob.rfind(".")
        if i >= 0:
            ending = prob[i+1:]
            for name in [
                "domain",
                "domain_" + prob[:i],
                "dom_" + prob[:i],
                "domain-" + prob[:i],
                "dom-" + prob[:i],
                prob[:i] + "-domain",
                ] + ([prob[:i].replace("problem", "domain")] if "problem" in prob else []):
                path = os.path.join(os.path.dirname(args.problem), name) + "." + ending
                if os.path.exists(path):
                    args.domain = path
                    break
        if args.domain is None:
            sys.stderr.write("Could not find corresponding PPDDL domain file\n")
            sys.exit(1)
            
    if args.jani is None:
        args.jani = args.problem + ".jani"

    p = subprocess.Popen(["python", os.path.join(P, "ppddl", "translate.py"), args.domain, args.problem])
    p.communicate()
    if p.returncode == 0:
        assert(os.path.exists("output.sas"))
        with open("output.sas") as sas:
            p = subprocess.Popen([get_jani_exec()], stdout=subprocess.PIPE, stdin=sas)
            out, err = p.communicate()
            if p.returncode == 0:
                with open(args.jani, "wb") as f:
                    f.write(out)
        # os.remove("output.sas")
    sys.exit(p.returncode)

