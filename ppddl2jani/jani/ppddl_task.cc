#include "ppddl_task.h"

#include <cassert>

std::shared_ptr<PPDDLTask> ppddl_task = nullptr;

template<typename T>
bool my_less(const T& x, const T& y);

template<typename T>
bool my_equal(const T& x, const T& u);

template<typename T>
bool
my_less(const std::vector<T>& x, const std::vector<T>& y)
{
    if (x.size() < y.size()) {
        return true;
    } else if (x.size() > y.size()) {
        return false;
    }
    for (unsigned i = 0; i < x.size(); i++) {
        if (my_less(x[i], y[i])) {
            return true;
        } else if (my_less(y[i], x[i])) {
            return false;
        }
    }
    return false;
}

template<>
bool
my_less(const FactPair& p, const FactPair& q)
{
    return p.var < q.var || (p.var == q.var && p.value < q.value);
}

template<>
bool
my_less(const ExplicitEffect& x, const ExplicitEffect& y)
{
    return my_less(x.fact, y.fact)
           || (!my_less(y.fact, x.fact) && my_less(x.conditions, y.conditions));
}

template<>
bool
my_less(const ExplicitProbabilisticOutcome& x,
        const ExplicitProbabilisticOutcome& y)
{
    return x.cost < y.cost || (x.cost == y.cost && my_less(x.effects, y.effects));
}

template<typename T>
bool
my_equal(const std::vector<T>& x, const std::vector<T>& y)
{
    if (x.size() != y.size()) {
        return false;
    }
    for (int i = x.size() - 1; i >= 0; i--) {
        if (!my_equal(x[i], y[i])) {
            return false;
        }
    }
    return true;
}

template<>
bool
my_equal(const FactPair& p, const FactPair& q)
{
    return p.var == q.var && p.value == q.value;
}

template<>
bool
my_equal(const ExplicitEffect& x, const ExplicitEffect& y)
{
    return my_equal(y.fact, x.fact) && my_equal(x.conditions, y.conditions);
}

template<>
bool
my_equal(const ExplicitProbabilisticOutcome& x,
         const ExplicitProbabilisticOutcome& y)
{
    return x.cost == y.cost && my_equal(x.effects, y.effects);
}

template<typename T>
struct Less
{
    bool
    operator()(const T& x, const T& y) const
    {
        return my_less(x, y);
    }
};

template<typename T>
struct Equal
{
    bool
    operator()(const T& x, const T& y) const
    {
        return my_equal(x, y);
    }
};

template<typename T>
struct PointerLess
{
    bool
    operator()(const T* x, const T* y) const
    {
        return my_less(*x, *y);
    }
};

ExplicitEffect canonical(const ExplicitEffect& eff)
{
    std::vector<FactPair> conds(eff.conditions);
    std::sort(conds.begin(), conds.end(), Less<FactPair>());
    conds.erase(std::unique(conds.begin(), conds.end(), Equal<FactPair>()),
                conds.end());
    return ExplicitEffect(eff.fact, std::move(conds));
}


ExplicitProbabilisticOutcome
ExplicitProbabilisticOutcome::canonical() const
{
    std::vector<ExplicitEffect> effs(effects);
    std::sort(effs.begin(), effs.end(), Less<ExplicitEffect>());
    effs.erase(std::unique(effs.begin(), effs.end(), Equal<ExplicitEffect>()),
               effs.end());
    return ExplicitProbabilisticOutcome(std::move(effs), probability, cost);
}

void
ExplicitProbabilisticOutcome::dump() const
{
    std::cout << "p=" << probability
              << " c=" << cost
              << " effs:" << std::endl;
    for (unsigned i = 0; i < effects.size(); i++) {
        std::cout << "    - [";
        for (unsigned j = 0; j < effects[i].conditions.size(); j++) {
            std::cout
                << (j > 0 ? " & " : "")
                << effects[i].conditions[j].var
                << "=" << effects[i].conditions[j].value;
        }
        std::cout << "] -> " << effects[i].fact.var << "=" << effects[i].fact.value << std::endl;
    }
}

void
ExplicitProbabilisticOperator::normalize()
{
    std::vector<ExplicitProbabilisticOutcome> canon;
    canon.reserve(outcomes.size());
    std::map<ExplicitProbabilisticOutcome*, t_value_type, PointerLess<ExplicitProbabilisticOutcome> >
    o_to_p;
    for (unsigned i = 0; i < outcomes.size(); i++) {
        canon.emplace_back(outcomes[i].canonical());
        ExplicitProbabilisticOutcome* key = &canon.back();
        auto it = o_to_p.find(key);
        if (it != o_to_p.end()) {
            it->second += key->probability;
            canon.pop_back();
        } else {
            o_to_p[key] = key->probability;
        }
    }
    for (auto it = o_to_p.begin(); it != o_to_p.end(); it++) {
        it->first->probability = it->second;
    }
    outcomes.swap(canon);
}

struct OutcomeData
{
    int numerator;
    int denominator;
    std::string operator_name;
    OutcomeData(int num, int den, const std::string& name)
        : numerator(num), denominator(den), operator_name(name) {}
};

static OutcomeData
parse_operator_outcome_name(const std::string& name)
{
    std::size_t det_pos = name.find("_DETDUP_");
    if (det_pos != std::string::npos) {
        std::size_t weight_pos = name.find("_WEIGHT_");
        if (weight_pos != std::string::npos) {
            std::size_t weight_num_pos = weight_pos + 8;
            std::string tmp = name.substr(weight_num_pos, std::string::npos);
            weight_num_pos = tmp.find("_");
            double numerator, denominator;
            std::istringstream(tmp.substr(0, weight_num_pos)) >> numerator;
            std::istringstream(tmp.substr(weight_num_pos + 1,
                                          std::string::npos)) >> denominator;
            return OutcomeData((int)numerator,
                               (int)denominator,
                               name.substr(0, det_pos)
                               + name.substr(name.find(" "), std::string::npos));
        } else {
            return OutcomeData(1, 1, name.substr(0, det_pos)
                               + name.substr(name.find(" "), std::string::npos));
        }
    } else {
        return OutcomeData(1, 1, name);
    }
}

static void
get_precondition(std::vector<FactPair>& prec,
                 const PDDLTask& task,
                 int index,
                 bool is_axiom)
{
    for (int i = 0;
            i < task.get_num_operator_preconditions(index, is_axiom);
            i++) {
        prec.push_back(task.get_operator_precondition(index, i, is_axiom));
    }
    std::sort(prec.begin(), prec.end());
}


static void
get_effect(ExplicitEffect& eff,
           const PDDLTask& task,
           int index,
           int eff_index,
           bool is_axiom)
{
    FactPair f = task.get_operator_effect(index, eff_index, is_axiom);
    eff.fact.var = f.var;
    eff.fact.value = f.value;
    for (int i = 0;
            i < task.get_num_operator_effect_conditions(index, eff_index, is_axiom);
            i++) {
        eff.conditions.push_back(task.get_operator_effect_condition(index, eff_index, i,
                                 is_axiom));
    }
}

static void
get_effects(std::vector<ExplicitEffect>& eff,
            const PDDLTask& task,
            int index,
            bool is_axiom)
{
    eff.resize(task.get_num_operator_effects(index, is_axiom));
    for (unsigned i = 0; i < eff.size(); i++) {
        get_effect(eff[i], task, index, i, is_axiom);
    }
}

std::shared_ptr<PPDDLTask>
PPDDLTask::create(const PDDLTask& task, bool )
{
    std::shared_ptr<PPDDLTask> result =
        std::make_shared<PPDDLTask>();

    int num_vars = task.get_num_variables();
    result->m_variable_domain.resize(num_vars);
    result->m_axiom_layers.resize(num_vars);
    result->m_default_axiom_values.resize(num_vars);
    result->m_variable_names.resize(num_vars);
    const std::vector<int>& iv = task.get_initial_state_values();
    result->m_initial_state_values.insert(result->m_initial_state_values.end(),
                                          iv.begin(),
                                          iv.end());
    for (int var = num_vars - 1; var >= 0; var--) {
        result->m_variable_domain[var] = task.get_variable_domain_size(var);
        result->m_axiom_layers[var] = task.get_variable_axiom_layer(var);
        result->m_default_axiom_values[var] = task.get_variable_default_axiom_value(
                var);
        result->m_variable_names[var] = task.get_variable_name(var);
    }

    result->m_fact_names.resize(num_vars);
    result->m_inconsistent_facts.resize(num_vars);
    for (int var = num_vars - 1; var >= 0; var--) {
        auto& names = result->m_fact_names[var];
        names.resize(result->m_variable_domain[var]);
        auto& inco = result->m_inconsistent_facts[var];
        inco.resize(result->m_variable_domain[var]);
        for (int val = result->m_variable_domain[var] - 1; val >= 0; val--) {
            names[val] = task.get_fact_name(FactPair(var, val));
            FactPair p(var, val);
            for (int var2 = num_vars - 1; var2 > var; var2--) {
                for (int val2 = result->m_variable_domain[var] - 1; val2 >= 0; val2--) {
                    FactPair q(var2, val2);
                    if (task.are_facts_mutex(p, q)) {
                        inco[val].insert(q);
                    }
                }
            }
        }
    }

    result->m_goal.reserve(task.get_num_goals());
    for (int i = 0; i < task.get_num_goals(); i++) {
        result->m_goal.push_back(task.get_goal_fact(i));
    }

    for (int axiom = 0; axiom < task.get_num_axioms(); axiom++) {
        result->m_axioms.emplace_back(task.get_operator_name(axiom, true));
        ExplicitProbabilisticOperator& ax = result->m_axioms.back();
        get_precondition(ax.pre, task, axiom, true);
        ax.outcomes.emplace_back(task.get_operator_cost(axiom, true));
        ax.outcomes.back().probability = 1;
        get_effects(ax.outcomes.back().effects, task, axiom, true);
    }

    // reconstructing probabilistic operators from outcomes
    std::map<std::string, unsigned> name_to_i;
    std::vector<std::vector<t_value_type > > probabilities;
    unsigned cur_i = 0;
    for (int orig_op = 0; orig_op < task.get_num_operators(); orig_op++) {
        OutcomeData data =
            parse_operator_outcome_name(task.get_operator_name(orig_op, false));
        if (data.numerator == 0) {
            continue;
        }
        unsigned i;
        auto it = name_to_i.find(data.operator_name);
        if (it == name_to_i.end()) {
            i = cur_i++;
            name_to_i[data.operator_name] = i;
            probabilities.emplace_back();
            result->m_prob_operators.emplace_back(data.operator_name);
            ExplicitProbabilisticOperator& op = result->m_prob_operators.back();
            get_precondition(op.pre, task, orig_op, false);
        } else {
            i = it->second;
#ifndef NDEBUG
            std::vector<FactPair> pre_old(result->m_prob_operators[i].pre);
            std::vector<FactPair> pre_new;
            get_precondition(pre_new, task, orig_op, false);
            assert(pre_old.size() == pre_new.size());
            std::sort(pre_old.begin(), pre_old.end());
            std::sort(pre_new.begin(), pre_new.end());
            for (unsigned j = 0; j < pre_old.size(); j++) {
                for (unsigned k = 0; k < pre_old.size(); k++) {
                    assert(pre_old[k] == pre_new[k]);
                }
            }
#endif
        }
        probabilities[i].emplace_back(data.numerator, data.denominator);
        ExplicitProbabilisticOperator& op = result->m_prob_operators[i];
        op.outcomes.emplace_back(
            task.get_operator_cost(orig_op, false));
        get_effects(op.outcomes.back().effects, task, orig_op, false);
    }

    // computing probabilities
    const t_value_type one(1, 1);
    for (unsigned i = 0; i < result->m_prob_operators.size(); i++) {
        ExplicitProbabilisticOperator& op = result->m_prob_operators[i];
        t_value_type sum = 0;
        for (unsigned j = 0; j < probabilities[i].size(); j++) {
            auto prob = probabilities[i][j];
            op.outcomes[j].probability = prob; 
            sum += prob;
        }
        assert(sum <= one);
        if (sum < one) {
            op.outcomes.emplace_back(0);
            op.outcomes.back().probability = (one - sum);
        }
        op.normalize();
    }

    return result;
}

void
build_ppddl_task(const PDDLTask& task)
{
    ppddl_task = PPDDLTask::create(task, true);
}

