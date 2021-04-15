Description

Tool that translates PPDDL [1] to Jani [2].

PPDDL parser is taken from Probabilistic Fast Downward [3,4]. The support of
conditional effects is limited.



Compilation and installation

This translator consists of a python module (the PPDDL compiler), and a C++
module (the Jani instance generator). The C++ module can be compiled by running
make in jani/.

Dependencies: python2.7 lib-boost



Usage

python ppddl2jani.py --jani [destination] [path-to-ppddl-domain] [path-to-ppddl-problem]

where
    [path-to-ppddl-domain] gives the path to the PPDDL domain specification
    file.  This parameter is optional, if omitted the script tries to find the
    domain file corresponding to the given problem file automatically.

    [path-to-ppddl-problem] gives the path to the PPDDL problem specification
    file.

    [destination] gives the destination file to which the Jani output will be
    written. If omitted, the Jani output will be written to
    [path-to-ppddl-problem].jani.



References

[1] H. Younes and M. Littman. PPDDL1.0: An Extension to PDDL for Expressing
Planning Domains with Probabilistic Effects. 2004.
http://reports-archive.adm.cs.cmu.edu/anon/2004/CMU-CS-04-167.pdf

[2] Carlos E.Budde, Christian Dehnert, Ernst Moritz Hahn, Arnd Hartmanns,
Sebastian Junges and Andrea Turrini. JANI: Quantitative Model and Tool
Interaction. In Proc. TACAS'17, 2017.

[3] Malte Helmert. The Fast Downward planning system. Journal of Artificial
Intelligence Research 26:191–246. 2006.

[4] M. Steinmetz, J. Hoffmann, and O. Buffet. Goal Probability Analysis in MDP
Probabilistic Planning: Exploring and Enhancing the State of the Art. Journal
of Artificial Intelligence Research, 57:229-271. 2016.

