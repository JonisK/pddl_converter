This script has been used to translate Jani MDP models with a restriced syntax into PPDDL to use it as input for the probabilistic version of the planning tool [Fast Downward](https://fai.cs.uni-saarland.de/software.html) (Marcel Steinmetz, FAI Group, Saarland University).
The script is referenced in the paper [Compiling Probabilistic Model Checking into Probabilistic Planning](https://aaai.org/ocs/index.php/ICAPS/ICAPS18/paper/view/17740cd).

It can be executed using the following command:

    python jani2ppddl.py \path\to\jani\file\janifile.jani -c \path\to\config\file\config.py
    
The configuration file `config.py` lists the arithmetic expressions used in the model, see the first lines of the script for more details.
An example for the content of this file is:
```python
GREATER = True
LESS = True
LESS_EQUAL = True
GREATER_EQUAL = True
```
