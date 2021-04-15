#include "pddl_task.h"

#include <algorithm>
#include <cassert>
#include <memory>
#include <set>
#include <vector>


using namespace std;

const FactPair FactPair::no_fact = FactPair(-1, -1);

static const int PRE_FILE_VERSION = 3;
shared_ptr<PDDLTask> pddl_task = nullptr;

static void
check_fact(const FactPair& fact, const vector<ExplicitVariable>& variables)
{
    if (fact.var >= (int) variables.size()) {
        cerr << "Invalid variable id: " << fact.var << endl;
        exit_with(ExitCode::INPUT_ERROR);
    }
    if (fact.value < 0 || fact.value >= variables[fact.var].domain_size) {
        cerr << "Invalid value for variable " << fact.var << ": " << fact.value << endl;
        exit_with(ExitCode::INPUT_ERROR);
    }
}

static void
check_facts(const vector<FactPair>& facts,
            const vector<ExplicitVariable>& variables)
{
    for (FactPair fact : facts) {
        check_fact(fact, variables);
    }
}

static void
check_facts(const ExplicitOperator& action,
            const vector<ExplicitVariable>& variables)
{
    check_facts(action.preconditions, variables);
    for (const ExplicitEffect& eff : action.effects) {
        check_fact(eff.fact, variables);
        check_facts(eff.conditions, variables);
    }
}

void
check_magic(istream& in, const string& magic)
{
    string word;
    in >> word;
    if (word != magic) {
        cerr << "Failed to match magic word '" << magic << "'." << endl
             << "Got '" << word << "'." << endl;
        if (magic == "begin_version") {
            cerr << "Possible cause: you are running the planner "
                 << "on a translator output file from " << endl
                 << "an older version." << endl;
        }
        exit_with(ExitCode::INPUT_ERROR);
    }
}

vector<FactPair>
read_facts(istream& in)
{
    int count;
    in >> count;
    vector<FactPair> conditions;
    conditions.reserve(count);
    for (int i = 0; i < count; ++i) {
        FactPair condition = FactPair::no_fact;
        in >> condition.var >> condition.value;
        conditions.push_back(condition);
    }
    return conditions;
}

ExplicitVariable::ExplicitVariable(istream& in)
{
    check_magic(in, "begin_variable");
    in >> name;
    in >> axiom_layer;
    in >> domain_size;
    in >> ws;
    fact_names.resize(domain_size);
    for (int i = 0; i < domain_size; ++i) {
        getline(in, fact_names[i]);
    }
    check_magic(in, "end_variable");
}


ExplicitEffect::ExplicitEffect(
    int var, int value, vector<FactPair>&& conditions)
    : fact(var, value), conditions(move(conditions))
{
}


void
ExplicitOperator::read_pre_post(istream& in)
{
    vector<FactPair> conditions = read_facts(in);
    int var, value_pre, value_post;
    in >> var >> value_pre >> value_post;
    if (value_pre != -1) {
        preconditions.emplace_back(var, value_pre);
    }
    effects.emplace_back(var, value_post, move(conditions));
}

ExplicitOperator::ExplicitOperator(istream& in, bool is_an_axiom,
                                   bool use_metric)
    : is_an_axiom(is_an_axiom)
{
    if (!is_an_axiom) {
        check_magic(in, "begin_operator");
        in >> ws;
        getline(in, name);
        preconditions = read_facts(in);
        int count;
        in >> count;
        effects.reserve(count);
        for (int i = 0; i < count; ++i) {
            read_pre_post(in);
        }

        int op_cost;
        in >> op_cost;
        cost = use_metric ? op_cost : 1;
        check_magic(in, "end_operator");
    } else {
        name = "<axiom>";
        cost = 0;
        check_magic(in, "begin_rule");
        read_pre_post(in);
        check_magic(in, "end_rule");
    }
    assert(cost >= 0);
}

void
read_and_verify_version(istream& in)
{
    int version;
    check_magic(in, "begin_version");
    in >> version;
    check_magic(in, "end_version");
    if (version != PRE_FILE_VERSION) {
        cerr << "Expected translator output file version " << PRE_FILE_VERSION
             << ", got " << version << "." << endl
             << "Exiting." << endl;
        exit_with(ExitCode::INPUT_ERROR);
    }
}

bool
read_metric(istream& in)
{
    bool use_metric;
    check_magic(in, "begin_metric");
    in >> use_metric;
    check_magic(in, "end_metric");
    return use_metric;
}

vector<ExplicitVariable>
read_variables(istream& in)
{
    int count;
    in >> count;
    vector<ExplicitVariable> variables;
    variables.reserve(count);
    for (int i = 0; i < count; ++i) {
        variables.emplace_back(in);
    }
    return variables;
}

vector<vector<set<FactPair>>>
read_mutexes(istream& in, const vector<ExplicitVariable>& variables)
{
    vector<vector<set<FactPair>>> inconsistent_facts(variables.size());
    for (size_t i = 0; i < variables.size(); ++i) {
        inconsistent_facts[i].resize(variables[i].domain_size);
    }

    int num_mutex_groups;
    in >> num_mutex_groups;

    /*
      NOTE: Mutex groups can overlap, in which case the same mutex
      should not be represented multiple times. The current
      representation takes care of that automatically by using sets.
      If we ever change this representation, this is something to be
      aware of.
    */
    for (int i = 0; i < num_mutex_groups; ++i) {
        check_magic(in, "begin_mutex_group");
        int num_facts;
        in >> num_facts;
        vector<FactPair> invariant_group;
        invariant_group.reserve(num_facts);
        for (int j = 0; j < num_facts; ++j) {
            int var;
            int value;
            in >> var >> value;
            invariant_group.emplace_back(var, value);
        }
        check_magic(in, "end_mutex_group");
        for (const FactPair& fact1 : invariant_group) {
            for (const FactPair& fact2 : invariant_group) {
                if (fact1.var != fact2.var) {
                    /* The "different variable" test makes sure we
                       don't mark a fact as mutex with itself
                       (important for correctness) and don't include
                       redundant mutexes (important to conserve
                       memory). Note that the translator (at least
                       with default settings) removes mutex groups
                       that contain *only* redundant mutexes, but it
                       can of course generate mutex groups which lead
                       to *some* redundant mutexes, where some but not
                       all facts talk about the same variable. */
                    inconsistent_facts[fact1.var][fact1.value].insert(fact2);
                }
            }
        }
    }
    return inconsistent_facts;
}

vector<FactPair>
read_goal(istream& in)
{
    check_magic(in, "begin_goal");
    vector<FactPair> goals = read_facts(in);
    check_magic(in, "end_goal");
    if (goals.empty()) {
        cerr << "Task has no goal condition!" << endl;
        exit_with(ExitCode::INPUT_ERROR);
    }
    return goals;
}

vector<ExplicitOperator>
read_actions(
    istream& in, bool is_axiom, bool use_metric,
    const vector<ExplicitVariable>& variables)
{
    int count;
    in >> count;
    vector<ExplicitOperator> actions;
    actions.reserve(count);
    for (int i = 0; i < count; ++i) {
        actions.emplace_back(in, is_axiom, use_metric);
        check_facts(actions.back(), variables);
    }
    return actions;
}

PDDLTask::PDDLTask(std::istream& in)
{
    read_and_verify_version(in);
    bool use_metric = read_metric(in);
    variables = read_variables(in);
    int num_variables = variables.size();

    mutexes = read_mutexes(in, variables);

    initial_state_values.resize(num_variables);
    check_magic(in, "begin_state");
    for (int i = 0; i < num_variables; ++i) {
        in >> initial_state_values[i];
    }
    check_magic(in, "end_state");

    for (int i = 0; i < num_variables; ++i) {
        variables[i].axiom_default_value = initial_state_values[i];
    }

    goals = read_goal(in);
    check_facts(goals, variables);
    operators = read_actions(in, false, use_metric, variables);
    axioms = read_actions(in, true, use_metric, variables);
    /* TODO: We should be stricter here and verify that we
       have reached the end of "in". */
}

const ExplicitVariable&
PDDLTask::get_variable(int var) const
{
    return variables[var];
}

const ExplicitEffect&
PDDLTask::get_effect(
    int op_id, int effect_id, bool is_axiom) const
{
    const ExplicitOperator& op = get_operator_or_axiom(op_id, is_axiom);
    return op.effects[effect_id];
}

const ExplicitOperator&
PDDLTask::get_operator_or_axiom(
    int index, bool is_axiom) const
{
    if (is_axiom) {
        return axioms[index];
    } else {
        return operators[index];
    }
}

int
PDDLTask::get_num_variables() const
{
    return variables.size();
}

string
PDDLTask::get_variable_name(int var) const
{
    return get_variable(var).name;
}

int
PDDLTask::get_variable_domain_size(int var) const
{
    return get_variable(var).domain_size;
}

int
PDDLTask::get_variable_axiom_layer(int var) const
{
    return get_variable(var).axiom_layer;
}

int
PDDLTask::get_variable_default_axiom_value(int var) const
{
    return get_variable(var).axiom_default_value;
}

string
PDDLTask::get_fact_name(const FactPair& fact) const
{
    return get_variable(fact.var).fact_names[fact.value];
}

bool
PDDLTask::are_facts_mutex(const FactPair& fact1, const FactPair& fact2) const
{
    if (fact1.var == fact2.var) {
        // Same variable: mutex iff different value.
        return fact1.value != fact2.value;
    }
    return bool(mutexes[fact1.var][fact1.value].count(fact2));
}

int
PDDLTask::get_operator_cost(int index, bool is_axiom) const
{
    return get_operator_or_axiom(index, is_axiom).cost;
}

string
PDDLTask::get_operator_name(int index, bool is_axiom) const
{
    return get_operator_or_axiom(index, is_axiom).name;
}

int
PDDLTask::get_num_operators() const
{
    return operators.size();
}

int
PDDLTask::get_num_operator_preconditions(int index, bool is_axiom) const
{
    return get_operator_or_axiom(index, is_axiom).preconditions.size();
}

FactPair
PDDLTask::get_operator_precondition(
    int op_index, int fact_index, bool is_axiom) const
{
    const ExplicitOperator& op = get_operator_or_axiom(op_index, is_axiom);
    return op.preconditions[fact_index];
}

int
PDDLTask::get_num_operator_effects(int op_index, bool is_axiom) const
{
    return get_operator_or_axiom(op_index, is_axiom).effects.size();
}

int
PDDLTask::get_num_operator_effect_conditions(
    int op_index, int eff_index, bool is_axiom) const
{
    return get_effect(op_index, eff_index, is_axiom).conditions.size();
}

FactPair
PDDLTask::get_operator_effect_condition(
    int op_index, int eff_index, int cond_index, bool is_axiom) const
{
    const ExplicitEffect& effect = get_effect(op_index, eff_index, is_axiom);
    return effect.conditions[cond_index];
}

FactPair
PDDLTask::get_operator_effect(
    int op_index, int eff_index, bool is_axiom) const
{
    return get_effect(op_index, eff_index, is_axiom).fact;
}

OperatorID
PDDLTask::get_global_operator_id(OperatorID id) const
{
    return id;
}

int
PDDLTask::get_num_axioms() const
{
    return axioms.size();
}

int
PDDLTask::get_num_goals() const
{
    return goals.size();
}

FactPair
PDDLTask::get_goal_fact(int index) const
{
    return goals[index];
}

vector<int>
PDDLTask::get_initial_state_values() const
{
    return initial_state_values;
}

void
read_pddl_task(std::istream& in)
{
    pddl_task = make_shared<PDDLTask>(in);
}
