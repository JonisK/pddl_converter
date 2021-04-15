#ifndef JANI_H
#define JANI_H

#include "ppddl_task.h"

#include <vector>
#include <string>
#include <memory>
#include <iostream>

#include <boost/rational.hpp>

struct BoundedVariable
{
    int id;
    int initial;
    int domain;
    BoundedVariable(int id, int initial, int domain);
    void dump(std::ostream& out) const;
};

struct Condition {
    virtual bool is_defined() const = 0;
    virtual void dump(std::ostream& out, unsigned off) const = 0;
};

struct Conjunction : public Condition
{
    std::vector<std::pair<int, int> > conjuncts;
    virtual bool is_defined() const override;
    void dump(std::ostream& out, unsigned off) const;
    void dump(std::ostream& out, unsigned off, unsigned depth) const;
};

struct DisjunctionInequal : public Condition
{
    std::vector<std::pair<int, int> > disjuncts;
    virtual bool is_defined() const override;
    void dump(std::ostream& out, unsigned off) const;
    void dump(std::ostream& out, unsigned off, unsigned depth) const;
};

struct Automaton
{
    struct Edge
    {
        struct Outcome
        {
            t_value_type probability;
            int to;
            std::vector<std::pair<int, int> > assignment;
            Outcome(int to);
            Outcome(t_value_type probability, int to);
            void dump(std::ostream& out,
                      const std::string& loc_name) const;
        };
        std::string name;
        int from;
        std::shared_ptr<Condition> guard;
        std::vector<Outcome> outcomes;
        Edge(const std::string& name, int from);
        Edge(int from);
        void dump(std::ostream& out,
                  const std::string& loc_name) const;
    };
    std::string name;
    std::string loc_name;
    int num_locations;
    int initial_location;
    std::vector<Edge> edges;
    Automaton(const std::string& name,
              const std::string& loc_name,
              int num_locs,
              int initial_loc);
    void dump(std::ostream& out) const;
};

struct JaniModel
{
    struct SynchronizedTransition {
        std::string action_name;
        std::vector<unsigned> automata_ids;
        SynchronizedTransition(const std::string& action_name);
    };
    std::vector<BoundedVariable> variables;
    std::vector<Automaton> automata;
    std::vector<SynchronizedTransition> synced;
    Conjunction property;
    JaniModel(const PPDDLTask& task);
    void dump(std::ostream& out) const;
};

#endif
