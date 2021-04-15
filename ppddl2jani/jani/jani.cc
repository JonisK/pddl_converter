#include "jani.h"
#include "utils.h"

#include <sstream>
#include <limits>

static const t_value_type ONE(1, 1);

std::string
sp(int x)
{
    std::ostringstream s;
    for (int i = 0; i < x; i++) {
        s << " ";
    }
    return s.str();
}

void
verify_no_axioms_no_conditional_effects(const PPDDLTask& task)
{
    if (task.get_num_axioms() > 0) {
        exit_with(ExitCode::UNSUPPORTED_FEATURE_REQUESTED);
    }
    for (int op = 0; op < task.get_num_operators(); op++) {
        for (int out = 0; out < task.get_num_operator_outcomes(op); out++) {
            for (int eff = 0; eff < task.get_num_outcome_effects(op, out); eff++) {
                if (task.get_num_outcome_effect_conditions(op, out, eff) > 0) {
                    // conditional effects
                    exit_with(ExitCode::UNSUPPORTED_FEATURE_REQUESTED);
                }
            }
        }
    }
}

void
verify_no_axioms(const PPDDLTask& task)
{
    if (task.get_num_axioms() > 0) {
        exit_with(ExitCode::UNSUPPORTED_FEATURE_REQUESTED);
    }
}




BoundedVariable::BoundedVariable(int id, int initial, int domain)
    : id(id), initial(initial), domain(domain)
{}

void
BoundedVariable::dump(std::ostream& out) const
{
    out << sp(2) << "{" << std::endl;
    out << sp(4) << "\"name\": \"var" << id << "\"," << std::endl;
    out << sp(4) << "\"type\": {" << std::endl;
    out << sp(6) << "\"kind\": \"bounded\"," << std::endl;
    out << sp(6) << "\"base\": \"int\"," << std::endl;
    out << sp(6) << "\"lower-bound\": 0," << std::endl;
    out << sp(6) << "\"upper-bound\": " << domain << std::endl;
    out << sp(4) << "}," << std::endl;
    out << sp(4) << "\"initial-value\": " << initial << std::endl;
    out << sp(2) << "}";
}


Automaton::Automaton(const std::string& name,
                     const std::string& loc_name,
                     int num_locs,
                     int initial_loc)
    : name(name)
    , loc_name(loc_name)
    , num_locations(num_locs)
    , initial_location(initial_loc)
{
}

Automaton::Edge::Outcome::Outcome(int to)
    : probability(ONE)
    , to(to)
{}

Automaton::Edge::Outcome::Outcome(t_value_type p, int to)
    : probability(p)
    , to(to)
{}

Automaton::Edge::Edge(const std::string& name, int from)
    : name(name), from(from), guard(nullptr)
{}

Automaton::Edge::Edge(int from)
    : name(""), from(from), guard(nullptr)
{}

void
Automaton::dump(std::ostream& out) const
{
    out << sp(2) << "{" << std::endl;
    out << sp(4) << "\"name\": \"" << name << "\"," << std::endl;
    out << sp(4) << "\"locations\": [";
    for (int loc = 0; loc < num_locations; loc++) {
        out << "{\"name\": \"" << loc_name << loc << "\"}"
            << (loc + 1 < num_locations ? ", " : "");
    }
    out << "]," << std::endl;
    out << sp(4) << "\"initial-locations\": [\"" << loc_name << initial_location <<
        "\"]," << std::endl;
    out << sp(4) << "\"edges\": [";
    for (unsigned e = 0; e < edges.size(); e++) {
        out << std::endl;
        edges[e].dump(out, loc_name);
        out << (e + 1 < edges.size() ? ", " : "");
    }
    out << "]" << std::endl;
    out << sp(2) << "}";
}

void
Automaton::Edge::dump(std::ostream& out,
                      const std::string& loc_name) const
{
    out << sp(6) << "{" << std::endl;
    if (name.length() > 0) {
        out << sp(6) << "\"action\": \"" << name << "\"," << std::endl;
    }
    out << sp(6) << "\"location\": \"" << loc_name << from << "\"," << std::endl;
    if (guard != nullptr && guard->is_defined()) {
        out << sp(6) << "\"guard\": { \"exp\": "  << std::endl;
        guard->dump(out, 8);
        out << "}," << std::endl;
    }
    out << sp(6) << "\"destinations\": [";
    for (unsigned i = 0; i < outcomes.size(); i++) {
        out << std::endl;
        outcomes[i].dump(out, loc_name);
        if (i + 1 < outcomes.size()) {
            out << ",";
        }
    }
    out << "]" << std::endl;
    out << sp(6) << "}";
}

bool
Conjunction::is_defined() const
{
    return !conjuncts.empty();
}

void
Conjunction::dump(std::ostream& out, unsigned off) const
{
    dump(out, off, 0);
}

void
Conjunction::dump(std::ostream& out, unsigned off, unsigned depth) const
{
    if (depth + 1 < conjuncts.size()) {
        out << sp(off + depth * 2) << "{" << std::endl;
        // out << sp(off + depth * 2) << "\"exp\": {" << std::endl;
        out << sp(off + depth * 2) << "\"op\": \"∧\"," << std::endl;
        out << sp(off + depth * 2) << "\"left\": ";
        dump(out, off, depth + 1);
        out << "," << std::endl;
        out << sp(off + depth * 2) << "\"right\": "
            << "{\"op\": \"=\", \"left\": \"var" << conjuncts[depth].first << "\""
            << ", \"right\": " << conjuncts[depth].second << "}" << std::endl;
        out << sp(off + depth * 2) << "}";
    } else {
        out << sp(off + depth * 2)
            << "{\"op\": \"=\", \"left\": \"var" << conjuncts[depth].first << "\""
            << ", \"right\": " << conjuncts[depth].second << "}";
    }
}

bool
DisjunctionInequal::is_defined() const
{
    return !disjuncts.empty();
}

void
DisjunctionInequal::dump(std::ostream& out, unsigned off) const
{
    dump(out, off, 0);
}

void
DisjunctionInequal::dump(std::ostream& out, unsigned off, unsigned depth) const
{
    if (depth + 1 < disjuncts.size()) {
        out << sp(off + depth * 2) << "{" << std::endl;
        // out << sp(off + depth * 2) << "\"exp\": {" << std::endl;
        out << sp(off + depth * 2) << "\"op\": \"∨\"," << std::endl;
        out << sp(off + depth * 2) << "\"left\": ";
        dump(out, off, depth + 1);
        out << "," << std::endl;
        out << sp(off + depth * 2) << "\"right\": "
            << "{\"op\": \"≠\", \"left\": \"var" << disjuncts[depth].first << "\""
            << ", \"right\": " << disjuncts[depth].second << "}" << std::endl;
        out << sp(off + depth * 2) << "}";
    } else {
        out << sp(off + depth * 2)
            << "{\"op\": \"≠\", \"left\": \"var" << disjuncts[depth].first << "\""
            << ", \"right\": " << disjuncts[depth].second << "}";
    }
}

void
Automaton::Edge::Outcome::dump(std::ostream& out,
                               const std::string& loc_name) const
{
    out << sp(8) << "{" << std::endl;
    out << sp(8) << "\"location\": \"" << loc_name << to << "\"," << std::endl;
    if (probability != ONE) {
        out << sp(8) << "\"probability\": {\"exp\": { \"op\": \"/\", "
            << "\"left\": " << probability.numerator() << ", "
            << "\"right\": " << probability.denominator()
            << "} }," << std::endl;
    }
    out << sp(8) << "\"assignments\": [" << std::endl;
    bool first = true;
    for (const auto& p : assignment) {
        if (!first) {
            out << "," << std::endl;
        }
        first = false;
        out << sp(10)
            << "{ \"ref\": \"var" << p.first << "\""
            << ", \"value\": " << p.second << " }";
    }
    out << "]" << std::endl;
    out << sp(8) << "}";
}

void
JaniModel::dump(std::ostream& out) const
{
    out.precision(std::numeric_limits<double>::max_digits10);
    out << "{" << std::endl;

    out << "\"jani-version\": 1," << std::endl;
    out << "\"name\": \"jani_from_ppddl\"," << std::endl;
    out << "\"type\": \"mdp\"," << std::endl;
    out << "\"features\": [\"derived-operators\"]," << std::endl;
    bool first = true;
    if(!synced.empty()) {
        out << "\"actions\": [" << std::endl;
        for (const auto& sync : synced) {
            if (!first) {
                out << "," << std::endl;
            }
            first = false;
            out << sp(2) << "{ \"name\": \"" << sync.action_name << "\" }";
        }
        out << std::endl << "]," << std::endl;
    }

    out << "\"variables\": [" << std::endl;
    first = true;
    for (const auto& var : variables) {
        if (!first) {
            std::cout << "," << std::endl;
        }
        first = false;
        var.dump(out);
    }
    out << "]," << std::endl;

    out << "\"automata\": [" << std::endl;
    first = true;
    for (const auto& aut : automata) {
        if (!first) {
            std::cout << "," << std::endl;
        }
        first = false;
        aut.dump(out);
    }
    out << "]," << std::endl;

    out << "\"system\": {" << std::endl;
    out << sp(2) << "\"elements\": [ " << std::endl;
    first = true;
    for (const auto& aut : automata) {
        if (!first) {
            out << ", " << std::endl;
        }
        first = false;
        out << sp(4) << "{ \"automaton\": \"" << aut.name << "\" }";
    }
    out << "]," << std::endl;
    out << sp(2) << "\"syncs\": [" << std::endl;
    first = true;
    for (const auto& sync : synced) {
        if (!first) {
            out << "," << std::endl;
        }
        first = false;
        out << sp(4) << "{ \"synchronise\": [" << std::endl;
        unsigned j = 0;
        for (unsigned i = 0; i < automata.size(); i++) {
            if (i > 0) {
                out << "," << std::endl;
            }
            if (j < sync.automata_ids.size() && i == sync.automata_ids[j]) {
                out << sp(6) << "\"" << sync.action_name << "\"";
                j++;
            } else {
                out << sp(6) << "null";
            }
        }
        out << "]," << std::endl
            << sp(4) << "\"result\": \"" << sync.action_name << "\"" << std::endl;
        out << sp(4) << "}";
    }
    out << std::endl << sp(2) << "]" << std::endl;
    out << "}," << std::endl;

    out << "\"properties\": [ { \"name\": \"goal_condition\", \"expression\": {" << std::endl;
    out << sp(2) << "\"op\": \"filter\"," << std::endl;
    out << sp(2) << "\"fun\": \"min\"," << std::endl;
    out << sp(2) << "\"values\": {" << std::endl;
    out << sp(4) << "\"op\": \"Pmax\"," << std::endl;
    out << sp(4) << "\"exp\": {" << std::endl;
    out << sp(6) << "\"op\": \"U\"," << std::endl;
    out << sp(6) << "\"left\": true," << std::endl;
    out << sp(6) << "\"right\":" << std::endl;
    property.dump(out, 8);
    out << std::endl << sp(4) << "}" << std::endl;
    out << sp(2) << "}," << std::endl;
    out << sp(2) << "\"states\": { \"op\": \"initial\" }" << std::endl;
    out << sp(2) << "}" << std::endl;
    out << "}]" << std::endl;

    out << "}" << std::endl;
}

JaniModel::SynchronizedTransition::SynchronizedTransition(
    const std::string& name)
    : action_name(name)
{}

JaniModel::JaniModel(const PPDDLTask& task)
{
    verify_no_axioms(task);

    for (int var = 0; var < task.get_num_variables(); var++) {
        variables.emplace_back(var,
                               task.get_initial_state_values()[var],
                               task.get_variable_domain_size(var));
    }

    automata.emplace_back("main", "loc", 1, 0);

    for (int op = 0; op < task.get_num_operators(); op++) {

        int edge_id = automata[0].edges.size();
        automata.front().edges.emplace_back(0);
        std::shared_ptr<Conjunction> prec = std::make_shared<Conjunction>();
        for (int p = 0; p < task.get_num_operator_preconditions(op); p++) {
            auto fact = task.get_operator_precondition(op, p);
            prec->conjuncts.emplace_back(fact.var,
                                         fact.value);
        }
        automata[0].edges[edge_id].guard = prec;

        for (int out = 0; out < task.get_num_operator_outcomes(op); out++) {
            bool ce = false;
            for (int eff = 0; !ce && eff < task.get_num_outcome_effects(op, out); eff++) {
                ce = task.get_num_outcome_effect_conditions(op, out, eff) > 0;
            }
            if (ce) {
                std::ostringstream out_name;
                out_name << "op" << op << "out" << out;

                int loc = (automata[0].num_locations)++;
                automata[0].edges[edge_id].outcomes.emplace_back(
                    task.get_outcome_probability(op, out),
                    loc);
                automata[0].edges.emplace_back(out_name.str(), loc);
                automata[0].edges.back().outcomes.emplace_back(0);

                synced.emplace_back(out_name.str());
                synced.back().automata_ids.push_back(0);

                int leftover = -1;
                for (int eff = 0; eff < task.get_num_outcome_effects(op, out); eff++) {
                    auto eff_fact = task.get_outcome_effect(op, out, eff);

                    // TODO group by conditions (represent effects with same
                    // condition by same automaton)
                    if (task.get_num_outcome_effect_conditions(op, out, eff) > 0) {
                        std::ostringstream aut_name;
                        aut_name << out_name.str() << "eff" << eff;

                        synced.back().automata_ids.push_back(automata.size());
                        automata.emplace_back(aut_name.str(), aut_name.str() + "loc", 1, 0);

                        std::shared_ptr<Conjunction> condition = std::make_shared<Conjunction>();
                        std::shared_ptr<DisjunctionInequal> neg_cond =
                            std::make_shared<DisjunctionInequal>();
                        for (int pre = 0; pre < task.get_num_outcome_effect_conditions(op, out, eff);
                                pre++) {
                            auto fact = task.get_outcome_effect_condition(op, out, eff, pre);
                            condition->conjuncts.emplace_back(
                                fact.var,
                                fact.value);
                            neg_cond->disjuncts.emplace_back(
                                fact.var,
                                fact.value);
                        }

                        automata.back().edges.emplace_back(out_name.str(), 0);
                        automata.back().edges.back().guard = condition;
                        automata.back().edges.back().outcomes.emplace_back(0);
                        automata.back().edges.back().outcomes.back().assignment.emplace_back(
                            eff_fact.var,
                            eff_fact.value);

                        automata.back().edges.emplace_back(out_name.str(), 0);
                        automata.back().edges.back().guard = neg_cond;
                        automata.back().edges.back().outcomes.emplace_back(0);
                    } else {
                        if (leftover < 0) {
                            std::ostringstream aut_name;
                            aut_name << out_name.str() << "nonce";

                            leftover = automata.size();
                            synced.back().automata_ids.push_back(automata.size());
                            automata.emplace_back(aut_name.str(), aut_name.str() + "loc", 1, 0);
                            automata.back().edges.emplace_back(out_name.str(), 0);
                            automata.back().edges.back().outcomes.emplace_back(0);
                        }
                        automata[leftover].edges.back().outcomes.back().assignment.emplace_back(
                            eff_fact.var,
                            eff_fact.value);
                    }
                }
            } else {
                automata[0].edges[edge_id].outcomes.emplace_back(
                    task.get_outcome_probability(op, out),
                    0);
                auto& outcome = automata[0].edges[edge_id].outcomes.back();
                for (int e = 0; e < task.get_num_outcome_effects(op, out); e++)  {
                    auto fact = task.get_outcome_effect(op, out, e);
                    outcome.assignment.emplace_back(fact.var, fact.value);
                }
            }
        }
    }

    for (int g = 0; g < task.get_num_goals(); g++) {
        auto fact = task.get_goal_fact(g);
        property.conjuncts.emplace_back(fact.var, fact.value);
    }
}
