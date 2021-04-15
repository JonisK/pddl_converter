#ifndef PPDDL_TASK_H
#define PPDDL_TASK_H

#include "pddl_task.h"

#include <map>
#include <set>
#include <algorithm>
#include <string>
#include <sstream>
#include <iostream>

#include <boost/rational.hpp>

typedef boost::rational<int> t_value_type;

struct ExplicitProbabilisticOutcome
{
    std::vector<ExplicitEffect> effects;
    t_value_type probability;
    int cost;
    ExplicitProbabilisticOutcome(int cost)
        : probability(0), cost(cost) {}
    ExplicitProbabilisticOutcome(
        ExplicitProbabilisticOutcome&& outcome)
        : effects(std::move(outcome.effects))
        , probability(std::move(outcome.probability))
        , cost(outcome.cost)
    {}
    ExplicitProbabilisticOutcome(
        std::vector<ExplicitEffect>&& effects,
        t_value_type probability,
        int cost)
        : effects(std::move(effects))
        , probability(probability)
        , cost(cost)
    {}
    ExplicitProbabilisticOutcome canonical() const;
    void dump() const;
};

struct ExplicitProbabilisticOperator
{
    std::vector<FactPair> pre;
    std::vector<ExplicitProbabilisticOutcome> outcomes;
    std::string name;
    ExplicitProbabilisticOperator(const std::string& name)
        : name(name) {}
    void normalize();
};

class PPDDLTask
{
private:
    std::vector<int> m_variable_domain;
    std::vector<int> m_axiom_layers;
    std::vector<int> m_default_axiom_values;
    std::vector<std::string> m_variable_names;
    std::vector<std::vector<std::string> > m_fact_names;
    std::vector<std::vector<std::set<FactPair> > > m_inconsistent_facts;
    std::vector<int> m_initial_state_values;
    std::vector<FactPair> m_goal;
    std::vector<ExplicitProbabilisticOperator> m_axioms;
    std::vector<ExplicitProbabilisticOperator> m_prob_operators;

    const ExplicitProbabilisticOperator&
    get_operator_or_axiom(int index, bool ax) const
    {
        return ax ? m_axioms[index] : m_prob_operators[index];
    }

public:
    explicit
    PPDDLTask()
    {}


    ~PPDDLTask() {}

    int
    get_num_variables() const
    {
        return m_variable_domain.size();
    }

    std::string
    get_variable_name(int var) const
    {
        return m_variable_names[var];
    }

    int
    get_variable_domain_size(int var) const
    {
        return m_variable_domain[var];
    }

    int
    get_variable_axiom_layer(int var) const
    {
        return m_axiom_layers[var];
    }

    int
    get_variable_default_axiom_value(int var) const
    {
        return m_default_axiom_values[var];
    }

    std::string
    get_fact_name(const FactPair& fact) const
    {
        return m_fact_names[fact.var][fact.value];
    }

    bool
    are_facts_mutex(const FactPair& fact1,
                    const FactPair& fact2) const
    {
        if (fact1.var == fact2.var) {
            return fact1.value != fact2.value;
        } else if (fact1.var < fact2.var) {
            return m_inconsistent_facts[fact1.var][fact1.value].count(fact2);
        } else {
            return m_inconsistent_facts[fact2.var][fact2.value].count(fact1);
        }
    }

    std::string
    get_operator_name(int index, bool is_axiom = false) const
    {
        return get_operator_or_axiom(index, is_axiom).name;
    }

    int
    get_num_operators() const
    {
        return m_prob_operators.size();
    }

    int
    get_num_operator_preconditions(int index, bool is_axiom = false) const
    {
        return get_operator_or_axiom(index, is_axiom).pre.size();
    }

    FactPair
    get_operator_precondition(
        int op_index, int fact_index, bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index, is_axiom).pre[fact_index];
    }

    int
    get_num_operator_outcomes(int op_index,
                              bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index, is_axiom).outcomes.size();
    }

    OperatorID
    get_global_operator_id(OperatorID id) const
    {
        return id;
    }

    int
    get_outcome_cost(int op_index,
                     int out_index,
                     bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index, is_axiom).outcomes[out_index].cost;
    }

    int
    get_num_outcome_effects(int op_index,
                            int out_index,
                            bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index,
                                     is_axiom).outcomes[out_index].effects.size();
    }

    int
    get_num_outcome_effect_conditions(
        int op_index,
        int out_index,
        int eff_index,
        bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index,
                                     is_axiom).outcomes[out_index].effects[eff_index].conditions.size();
    }

    FactPair
    get_outcome_effect_condition(
        int op_index,
        int out_index,
        int eff_index,
        int cond_index,
        bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index,
                                     is_axiom).outcomes[out_index].effects[eff_index].conditions[cond_index];
    }

    FactPair
    get_outcome_effect(
        int op_index, int out_index, int eff_index,
        bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index,
                                     is_axiom).outcomes[out_index].effects[eff_index].fact;
    }

    t_value_type
    get_outcome_probability(
        int op_index, int out_index, bool is_axiom = false) const
    {
        return get_operator_or_axiom(op_index,
                                     is_axiom).outcomes[out_index].probability;
    }

    int
    get_num_axioms() const
    {
        return m_axioms.size();
    }

    int
    get_num_goals() const
    {
        return m_goal.size();
    }

    FactPair
    get_goal_fact(int index) const
    {
        return m_goal[index];
    }

    std::vector<int>
    get_initial_state_values() const
    {
        return m_initial_state_values;
    }

    static std::shared_ptr<PPDDLTask> create(
        const PDDLTask& task,
        bool progress = false);
};


extern std::shared_ptr<PPDDLTask> ppddl_task;
extern void build_ppddl_task(const PDDLTask& task);

#endif
