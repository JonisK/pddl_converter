# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import math
import fractions
import functools

import graph
import pddl


def cartesian_product(*sequences):
    # TODO: Also exists in tools.py outside the pddl package (defined slightly
    #       differently). Not good. Need proper import paths.
    if not sequences:
        yield ()
    else:
        for tup in cartesian_product(*sequences[1:]):
            for item in sequences[0]:
                yield (item,) + tup


def parse_typed_list(alist, only_variables=False,
                     constructor=pddl.TypedObject,
                     default_type="object"):
    result = []
    while alist:
        try:
            separator_position = alist.index("-")
        except ValueError:
            items = alist
            _type = default_type
            alist = []
        else:
            items = alist[:separator_position]
            _type = alist[separator_position + 1]
            alist = alist[separator_position + 2:]
        for item in items:
            assert not only_variables or item.startswith("?"), \
                   "Expected item to be a variable: %s in (%s)" % (
                item, " ".join(items))
            entry = constructor(item, _type)
            result.append(entry)
    return result


def set_supertypes(type_list):
    # TODO: This is a two-stage construction, which is perhaps
    # not a great idea. Might need more thought in the future.
    type_name_to_type = {}
    child_types = []
    for type in type_list:
        type.supertype_names = []
        type_name_to_type[type.name] = type
        if type.basetype_name:
            child_types.append((type.name, type.basetype_name))
    for (desc_name, anc_name) in graph.transitive_closure(child_types):
        type_name_to_type[desc_name].supertype_names.append(anc_name)


def parse_predicate(alist):
    name = alist[0]
    arguments = parse_typed_list(alist[1:], only_variables=True)
    return pddl.Predicate(name, arguments)


def parse_function(alist, type_name):
    name = alist[0]
    arguments = parse_typed_list(alist[1:])
    return pddl.Function(name, arguments, type_name)


def parse_condition(alist, type_dict, predicate_dict):
    condition = parse_condition_aux(alist, False, type_dict, predicate_dict)
    # TODO: The next line doesn't appear to do anything good,
    # since uniquify_variables doesn't modify the condition in place.
    # Conditions in actions or axioms are uniquified elsewhere, but
    # it looks like goal conditions are never uniquified at all
    # (which would be a bug).
    condition.uniquify_variables({})
    return condition


def parse_condition_aux(alist, negated, type_dict, predicate_dict):
    """Parse a PDDL condition. The condition is translated into NNF on the fly."""
    tag = alist[0]
    if tag in ("and", "or", "not", "imply"):
        args = alist[1:]
        if tag == "imply":
            assert len(args) == 2
        if tag == "not":
            assert len(args) == 1
            return parse_condition_aux(
                args[0], not negated, type_dict, predicate_dict)
    elif tag in ("forall", "exists"):
        parameters = parse_typed_list(alist[1])
        args = alist[2:]
        assert len(args) == 1
    else:
        return parse_literal(alist, type_dict, predicate_dict, negated=negated)

    if tag == "imply":
        parts = [parse_condition_aux(
                args[0], not negated, type_dict, predicate_dict),
                 parse_condition_aux(
                args[1], negated, type_dict, predicate_dict)]
        tag = "or"
    else:
        parts = [parse_condition_aux(part, negated, type_dict, predicate_dict)
                 for part in args]

    if tag == "and" and not negated or tag == "or" and negated:
        return pddl.Conjunction(parts)
    elif tag == "or" and not negated or tag == "and" and negated:
        return pddl.Disjunction(parts)
    elif tag == "forall" and not negated or tag == "exists" and negated:
        return pddl.UniversalCondition(parameters, parts)
    elif tag == "exists" and not negated or tag == "forall" and negated:
        return pddl.ExistentialCondition(parameters, parts)


def parse_literal(alist, type_dict, predicate_dict, negated=False):
    if alist[0] == "not":
        assert len(alist) == 2
        alist = alist[1]
        negated = not negated

    pred_id, arity = _get_predicate_id_and_arity(
        alist[0], type_dict, predicate_dict)

    if arity != len(alist) - 1:
        raise SystemExit("predicate used with wrong arity: (%s)"
                         % " ".join(alist))

    if negated:
        return pddl.NegatedAtom(pred_id, alist[1:])
    else:
        return pddl.Atom(pred_id, alist[1:])


SEEN_WARNING_TYPE_PREDICATE_NAME_CLASH = False
def _get_predicate_id_and_arity(text, type_dict, predicate_dict):
    global SEEN_WARNING_TYPE_PREDICATE_NAME_CLASH

    the_type = type_dict.get(text)
    the_predicate = predicate_dict.get(text)

    if the_type is None and the_predicate is None:
        raise SystemExit("Undeclared predicate: %s" % text)
    elif the_predicate is not None:
        if the_type is not None and not SEEN_WARNING_TYPE_PREDICATE_NAME_CLASH:
            msg = ("Warning: name clash between type and predicate %r.\n"
                   "Interpreting as predicate in conditions.") % text
            print(msg, file=sys.stderr)
            SEEN_WARNING_TYPE_PREDICATE_NAME_CLASH = True
        return the_predicate.name, the_predicate.get_arity()
    else:
        assert the_type is not None
        return the_type.get_predicate_name(), 1


def _get_probability(tmp_effect):
    """Finds the resulting probability of multiplying each conditional probability in
       tmp_effect. The structure of tmp_effect is the same as above:
       [ConjunctiveEffect] {[UniversalEffect] [ConditionalEffect] SimpleEffect}."""
    if isinstance(tmp_effect, pddl.ConjunctiveEffect):
        base_probability = tmp_effect.probability
        for effect in tmp_effect.effects:
            base_probability *= _get_probability(effect)
        return base_probability
    else:
        return tmp_effect.probability

def _get_inferred_cost(prob):
    # This method infers a cost from a given probability
    # These costs will help heuristic search in the planner
    #return 2 + int((1.3 + (math.log10(1 - min(0.95, prob))))*100)
    scaling_factor = 300.0
    return int((-scaling_factor) * math.log10(min(0.95, max(0.05, prob))))


def parse_effects(alist, result, type_dict, predicate_dict):
    """Parse a PDDL effect (any combination of simple, conjunctive, conditional, and universal)."""
    tmp_effects = parse_effect(alist, type_dict, predicate_dict)
    normalized = [tmp_effect.normalize() for tmp_effect in tmp_effects]
    cost_rest_eff = [norm.extract_cost() for norm in normalized]
    cost_eff_prob_triples = []
    for (cost_eff, rest_effect) in cost_rest_eff:
        res = []
        add_effect(rest_effect, res)
        prob = _get_probability(rest_effect)
        if cost_eff:
            cost_eff_prob_triples.append((cost_eff.effect, res, prob))
        else:
            # Here we can use the probability to assign a cost to help heuristics
            approximated_cost = _get_inferred_cost(prob)
            cost_eff_prob_triples.append((approximated_cost, res, prob))
    return cost_eff_prob_triples

def add_effect(tmp_effect, result):
    """tmp_effect has the following structure:
       [ConjunctiveEffect] [UniversalEffect] [ConditionalEffect] SimpleEffect."""

    if isinstance(tmp_effect, pddl.ConjunctiveEffect):
        for effect in tmp_effect.effects:
            add_effect(effect, result)
        return
    else:
        parameters = []
        condition = pddl.Truth()
        if isinstance(tmp_effect, pddl.UniversalEffect):
            parameters = tmp_effect.parameters
            if isinstance(tmp_effect.effect, pddl.ConditionalEffect):
                condition = tmp_effect.effect.condition
                assert isinstance(tmp_effect.effect.effect, pddl.SimpleEffect)
                effect = tmp_effect.effect.effect.effect
            else:
                assert isinstance(tmp_effect.effect, pddl.SimpleEffect)
                effect = tmp_effect.effect.effect
        elif isinstance(tmp_effect, pddl.ConditionalEffect):
            condition = tmp_effect.condition
            assert isinstance(tmp_effect.effect, pddl.SimpleEffect)
            effect = tmp_effect.effect.effect
        else:
            assert isinstance(tmp_effect, pddl.SimpleEffect)
            effect = tmp_effect.effect
        if effect is None:
            # Nothing to add
            return
        assert isinstance(effect, pddl.Literal)
        # Check for contradictory effects
        condition = condition.simplified()
        new_effect = pddl.Effect(parameters, condition, effect)
        contradiction = pddl.Effect(parameters, condition, effect.negate())
        if not contradiction in result:
            result.append(new_effect)
        else:
            # We use add-after-delete semantics, keep positive effect
            if isinstance(contradiction.literal, pddl.NegatedAtom):
                result.remove(contradiction)
                result.append(new_effect)

def parse_effect(alist, type_dict, predicate_dict):
    tag = alist[0]
    if tag == "and":
        return [pddl.ConjunctiveEffect(conjuncts)
		for conjuncts in cartesian_product(
			*[parse_effect(eff, type_dict, predicate_dict)
				for eff in alist[1:]])]
    elif tag == "forall":
        assert len(alist) == 3
        parameters = parse_typed_list(alist[1])
        effects = parse_effect(alist[2], type_dict, predicate_dict)
        assert 1 == len(effects), \
	    "Error: Cannot embed non-determinism inside of a forall (for now)."
        return [pddl.UniversalEffect(parameters, effect) for effect in effects]
    elif tag == "when":
        assert len(alist) == 3
        condition = parse_condition(
            alist[1], type_dict, predicate_dict)
        effects = parse_effect(alist[2], type_dict, predicate_dict)
        assert all([eff.probability == 1 for eff in effects]), \
            "Error: (probabilistic ...) within (when ...) is currently not supported"
        return [pddl.ConditionalEffect(condition, effect) for effect in effects]
    elif tag == "increase":
        assert len(alist) == 3
        assert alist[1] == ['total-cost']
        assignment = parse_assignment(alist)
        return [pddl.CostEffect(assignment)]
    elif tag == "probabilistic":
        # Generate effects for each outcome and then set their probability appropriately
        assert (len(alist)-1) % 2 == 0,\
	    "Each probabilistic outcome must have an associated probability"
        outcome_pairs = [(alist[i], alist[i+1]) for i in range(1, len(alist), 2)]

        remaining_probability = fractions.Fraction(1)
        outcomes = []
        for pair in outcome_pairs:
            effects = parse_effect(pair[1], type_dict, predicate_dict)
            for eff in effects:
                # Apply the base probability in the pair to this individual effect
                eff.probability *= fractions.Fraction(pair[0]).limit_denominator()
                remaining_probability -= eff.probability
                outcomes.append(eff)
        remaining_probability = remaining_probability.limit_denominator()
        if (remaining_probability > 0):
            remaining_eff = pddl.SimpleEffect(None)
            remaining_eff.probability = remaining_probability
            outcomes.append(remaining_eff)
        return outcomes
    else:
        # We pass in {} instead of type_dict here because types must
        # be static predicates, so cannot be the target of an effect.
        return [pddl.SimpleEffect(parse_literal(alist, {}, predicate_dict))]


def parse_expression(exp):
    if isinstance(exp, list):
        functionsymbol = exp[0]
        return pddl.PrimitiveNumericExpression(functionsymbol, exp[1:])
    elif exp.replace(".", "").isdigit():
        return pddl.NumericConstant(float(exp))
    elif exp[0] == "-":
        raise ValueError("Negative numbers are not supported")
    else:
        return pddl.PrimitiveNumericExpression(exp, [])

def parse_assignment(alist):
    assert len(alist) == 3
    op = alist[0]
    head = parse_expression(alist[1])
    exp = parse_expression(alist[2])
    if op == "=":
        return pddl.Assign(head, exp)
    elif op == "increase":
        return pddl.Increase(head, exp)
    else:
        assert False, "Assignment operator not supported."


def parse_action(alist, type_dict, predicate_dict):
    iterator = iter(alist)
    action_tag = next(iterator)
    assert action_tag == ":action"
    name = next(iterator)
    parameters_tag_opt = next(iterator)
    if parameters_tag_opt == ":parameters":
        parameters = parse_typed_list(next(iterator),
                                      only_variables=True)
        precondition_tag_opt = next(iterator)
    else:
        parameters = []
        precondition_tag_opt = parameters_tag_opt
    if precondition_tag_opt == ":precondition":
        precondition_list = next(iterator)
        if not precondition_list:
            # Note that :precondition () is allowed in PDDL.
            precondition = pddl.Conjunction([])
        else:
            precondition = parse_condition(
                precondition_list, type_dict, predicate_dict)
            precondition = precondition.simplified()
        effect_tag = next(iterator)
    else:
        precondition = pddl.Conjunction([])
        effect_tag = precondition_tag_opt
    assert effect_tag == ":effect"
    effect_list = next(iterator)
    eff = []
    if effect_list:
        try:
            cost_eff_pairs = parse_effects(
                effect_list, eff, type_dict, predicate_dict)
            if 1 == len(cost_eff_pairs):
                cost_eff_pairs = [(cost_eff_pairs[0][0], cost_eff_pairs[0][1], '')]
            else:
                # Convert floats to fractions to output
                # TODO : Benchmark this fraction conversion
                all_fractions = []
                # summed = fractions.Fraction(0)
                for cep in cost_eff_pairs:
                    all_fractions.append(fractions.Fraction(cep[2]).limit_denominator())
                    # summed += all_fractions[-1]
                # assert(summed == fractions.Fraction(1))
                lcm = functools.reduce(lambda a,b: (a*b)/fractions.gcd(a,b), [f.denominator for f in all_fractions], 1)
                # Use the fractions and lcm to build the weights
                cost_eff_pairs = [(cost_eff_pairs[i][0], cost_eff_pairs[i][1], "_DETDUP_%d_WEIGHT_%d_%d" %
                    (i, all_fractions[i].numerator*(lcm/all_fractions[i].denominator), lcm)) for i in range(len(cost_eff_pairs))]
        except ValueError as e:
            raise SystemExit("Error in Action %s\nReason: %s." % (name, e))
    for rest in iterator:
        assert False, rest
    return [pddl.Action(
        name + suffix,
        parameters,
        len(parameters),
        precondition,
        eff,
        cost) for (cost, eff, suffix) in cost_eff_pairs]


def parse_axiom(alist, type_dict, predicate_dict):
    assert len(alist) == 3
    assert alist[0] == ":derived"
    predicate = parse_predicate(alist[1])
    condition = parse_condition(
        alist[2], type_dict, predicate_dict)
    return pddl.Axiom(predicate.name, predicate.arguments,
                      len(predicate.arguments), condition)


def parse_task(domain_pddl, task_pddl):
    domain_name, domain_requirements, types, type_dict, constants, predicates, predicate_dict, functions, actions, axioms \
                 = parse_domain_pddl(domain_pddl)
    task_name, task_domain_name, task_requirements, objects, init, goal, use_metric = parse_task_pddl(task_pddl, type_dict, predicate_dict)

    assert domain_name == task_domain_name
    requirements = pddl.Requirements(sorted(set(
                domain_requirements.requirements +
                task_requirements.requirements)))
    objects = constants + objects
    check_for_duplicates(
        [o.name for o in objects],
        errmsg="error: duplicate object %r",
        finalmsg="please check :constants and :objects definitions")
    init += [pddl.Atom("=", (obj.name, obj.name)) for obj in objects]

    return pddl.Task(
        domain_name, task_name, requirements, types, objects,
        predicates, functions, init, goal, actions, axioms, use_metric)


def parse_domain_pddl(domain_pddl):
    iterator = iter(domain_pddl)

    define_tag = next(iterator)
    assert define_tag == "define"
    domain_line = next(iterator)
    assert domain_line[0] == "domain" and len(domain_line) == 2
    yield domain_line[1]

    ## We allow an arbitrary order of the requirement, types, constants,
    ## predicates and functions specification. The PDDL BNF is more strict on
    ## this, so we print a warning if it is violated.
    requirements = pddl.Requirements([":strips"])
    the_types = [pddl.Type("object")]
    constants, the_predicates, the_functions = [], [], []
    correct_order = [":requirements", ":types", ":constants", ":predicates",
                     ":functions"]
    seen_fields = []
    first_action = None
    for opt in iterator:
        field = opt[0]
        if field not in correct_order:
            first_action = opt
            break
        if field in seen_fields:
            raise SystemExit("Error in domain specification\n" +
                             "Reason: two '%s' specifications." % field)
        if (seen_fields and
            correct_order.index(seen_fields[-1]) > correct_order.index(field)):
            msg = "\nWarning: %s specification not allowed here (cf. PDDL BNF)" % field
            print(msg, file=sys.stderr)
        seen_fields.append(field)
        if field == ":requirements":
            requirements = pddl.Requirements(opt[1:])
        elif field == ":types":
            the_types.extend(parse_typed_list(
                    opt[1:], constructor=pddl.Type))
        elif field == ":constants":
            constants = parse_typed_list(opt[1:])
        elif field == ":predicates":
            the_predicates = [parse_predicate(entry)
                              for entry in opt[1:]]
            the_predicates += [pddl.Predicate("=",
                                 [pddl.TypedObject("?x", "object"),
                                  pddl.TypedObject("?y", "object")])]
        elif field == ":functions":
            the_functions = parse_typed_list(
                opt[1:],
                constructor=parse_function,
                default_type="number")
    set_supertypes(the_types)
    yield requirements
    yield the_types
    type_dict = dict((type.name, type) for type in the_types)
    yield type_dict
    yield constants
    yield the_predicates
    predicate_dict = dict((pred.name, pred) for pred in the_predicates)
    yield predicate_dict
    yield the_functions

    entries = []
    if first_action is not None:
        entries.append(first_action)
    entries.extend(iterator)

    the_axioms = []
    the_actions = []
    for entry in entries:
        if entry[0] == ":derived":
            axiom = parse_axiom(entry, type_dict, predicate_dict)
            the_axioms.append(axiom)
        else:
            action = parse_action(entry, type_dict, predicate_dict)
            # if action is not None:
            the_actions.extend(action)
    yield the_actions
    yield the_axioms

def parse_task_pddl(task_pddl, type_dict, predicate_dict):
    iterator = iter(task_pddl)

    define_tag = next(iterator)
    assert define_tag == "define"
    problem_line = next(iterator)
    assert problem_line[0] == "problem" and len(problem_line) == 2
    yield problem_line[1]
    domain_line = next(iterator)
    assert domain_line[0] == ":domain" and len(domain_line) == 2
    yield domain_line[1]

    requirements_opt = next(iterator)
    if requirements_opt[0] == ":requirements":
        requirements = requirements_opt[1:]
        objects_opt = next(iterator)
    else:
        requirements = []
        objects_opt = requirements_opt
    yield pddl.Requirements(requirements)

    if objects_opt[0] == ":objects":
        yield parse_typed_list(objects_opt[1:])
        init = next(iterator)
    else:
        yield []
        init = objects_opt

    assert init[0] == ":init"
    initial = []
    initial_true = set()
    initial_false = set()
    initial_assignments = dict()
    for fact in init[1:]:
        if fact[0] == "=":
            try:
                assignment = parse_assignment(fact)
            except ValueError as e:
                raise SystemExit("Error in initial state specification\n" +
                                 "Reason: %s." %  e)
            if not isinstance(assignment.expression,
                              pddl.NumericConstant):
                raise SystemExit("Illegal assignment in initial state " +
                    "specification:\n%s" % assignment)
            if assignment.fluent in initial_assignments:
                prev = initial_assignments[assignment.fluent]
                if assignment.expression == prev.expression:
                    print("Warning: %s is specified twice" % assignment,
                          "in initial state specification")
                else:
                    raise SystemExit("Error in initial state specification\n" +
                                     "Reason: conflicting assignment for " +
                                     "%s." %  assignment.fluent)
            else:
                initial_assignments[assignment.fluent] = assignment
                initial.append(assignment)
        elif fact[0] == "not":
            atom = pddl.Atom(fact[1][0], fact[1][1:])
            check_atom_consistency(atom, initial_false, initial_true, False)
            initial_false.add(atom)
        else:
            atom = pddl.Atom(fact[0], fact[1:])
            check_atom_consistency(atom, initial_true, initial_false)
            initial_true.add(atom)
    initial.extend(initial_true)
    yield initial

    goal = next(iterator)
    assert goal[0] == ":goal" and len(goal) == 2
    yield parse_condition(goal[1], type_dict, predicate_dict)

    use_metric = False
    for entry in iterator:
        if entry[0] == ":metric":
            if entry[1]=="minimize" and entry[2][0] == "total-cost":
                use_metric = True
            else:
                assert False, "Unknown metric."
    yield use_metric

    for entry in iterator:
        assert False, entry


def check_atom_consistency(atom, same_truth_value, other_truth_value, atom_is_true=True):
    if atom in other_truth_value:
        raise SystemExit("Error in initial state specification\n" +
                         "Reason: %s is true and false." %  atom)
    if atom in same_truth_value:
        if not atom_is_true:
            atom = atom.negate()
        print("Warning: %s is specified twice in initial state specification" % atom)


def check_for_duplicates(elements, errmsg, finalmsg):
    seen = set()
    errors = []
    for element in elements:
        if element in seen:
            errors.append(errmsg % element)
        else:
            seen.add(element)
    if errors:
        raise SystemExit("\n".join(errors) + "\n" + finalmsg)
