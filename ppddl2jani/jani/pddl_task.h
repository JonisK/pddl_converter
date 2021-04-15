#ifndef PDDL_TASK_H
#define PDDL_TASK_H

#include "utils.h"

#include <memory>
#include <string>
#include <utility>
#include <vector>
#include <set>
#include <iostream>

class OperatorID
{
    int index;

public:
    explicit
    OperatorID(int index)
        : index(index)
    {
    }

    static const OperatorID no_operator;

    int
    get_index() const
    {
        return index;
    }

    bool
    operator==(const OperatorID& other) const
    {
        return index == other.index;
    }

    bool
    operator!=(const OperatorID& other) const
    {
        return !(*this == other);
    }

    size_t
    hash() const
    {
        return index;
    }
};


struct FactPair
{
    int var;
    int value;

    FactPair(int var, int value)
        : var(var), value(value)
    {
    }

    bool
    operator<(const FactPair& other) const
    {
        return var < other.var || (var == other.var && value < other.value);
    }

    bool
    operator==(const FactPair& other) const
    {
        return var == other.var && value == other.value;
    }

    bool
    operator!=(const FactPair& other) const
    {
        return var != other.var || value != other.value;
    }

    /*
      This special object represents "no such fact". E.g., functions
      that search a fact can return "no_fact" when no matching fact is
      found.
    */
    static const FactPair no_fact;
};

struct ExplicitVariable
{
    int domain_size;
    std::string name;
    std::vector<std::string> fact_names;
    int axiom_layer;
    int axiom_default_value;

    explicit ExplicitVariable(std::istream& in);
};


struct ExplicitEffect
{
    FactPair fact;
    std::vector<FactPair> conditions;

    ExplicitEffect() : fact(-1, -1) {}
    ExplicitEffect(const FactPair& fact,
                   std::vector<FactPair>&& conds)
        : fact(fact)
        , conditions(std::move(conds)) {}
    ExplicitEffect(int var, int value, std::vector<FactPair>&& conditions);
};


struct ExplicitOperator
{
    std::vector<FactPair> preconditions;
    std::vector<ExplicitEffect> effects;
    int cost;
    std::string name;
    bool is_an_axiom;

    void read_pre_post(std::istream& in);
    ExplicitOperator(std::istream& in, bool is_an_axiom, bool use_metric);
};


class PDDLTask
{
    std::vector<ExplicitVariable> variables;
    std::vector<std::vector<std::set<FactPair>>> mutexes;
    std::vector<ExplicitOperator> operators;
    std::vector<ExplicitOperator> axioms;
    mutable std::vector<int> initial_state_values;
    std::vector<FactPair> goals;

    const ExplicitVariable& get_variable(int var) const;
    const ExplicitEffect& get_effect(int op_id, int effect_id, bool is_axiom) const;
    const ExplicitOperator& get_operator_or_axiom(int index, bool is_axiom) const;

public:
    explicit PDDLTask(std::istream& in);

    int get_num_variables() const;
    std::string get_variable_name(int var) const;
    int get_variable_domain_size(int var) const;
    int get_variable_axiom_layer(int var) const;
    int get_variable_default_axiom_value(int var) const;
    std::string get_fact_name(const FactPair& fact) const;
    bool are_facts_mutex(
        const FactPair& fact1, const FactPair& fact2) const;

    int get_operator_cost(int index, bool is_axiom) const;
    std::string get_operator_name(
        int index, bool is_axiom) const;
    int get_num_operators() const;
    int get_num_operator_preconditions(
        int index, bool is_axiom) const;
    FactPair get_operator_precondition(
        int op_index, int fact_index, bool is_axiom) const;
    int get_num_operator_effects(
        int op_index, bool is_axiom) const;
    int get_num_operator_effect_conditions(
        int op_index, int eff_index, bool is_axiom) const;
    FactPair get_operator_effect_condition(
        int op_index, int eff_index, int cond_index, bool is_axiom) const;
    FactPair get_operator_effect(
        int op_index, int eff_index, bool is_axiom) const;
    OperatorID get_global_operator_id(OperatorID id) const;

    int get_num_axioms() const;

    int get_num_goals() const;
    FactPair get_goal_fact(int index) const;

    std::vector<int> get_initial_state_values() const;
};

extern std::shared_ptr<PDDLTask> pddl_task;
extern void read_pddl_task(std::istream& in);

#endif
