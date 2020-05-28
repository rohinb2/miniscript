# Miniscript

## About

Miniscript is an imperative, Javascript-esque language with dynamic information flow control.

The language is interpreted and complete with conditionals, loops, and user function definitions, and support primitive types of strings, numbers and arrays. You can look at in the `samples` folder for more more information on how to write miniscript.

The interesting part about miniscript is the security labels that are built into the language that enable control of information flow. A label l for a value is defined as {s_1, s_2, ..., s_n}, where the s values are unique strings. This makes a label a set of unique strings. In order to "have clearance" for the access to a value the label l_1 of access needs to be a subset of l_2 where l_2 is the label of the variable.

## Installation

Create a python virtual envrionment using `python -m venv .venv` or `virtualenv .venv` and then activate it using `source .venv/bin/activate`. Then run `pip install -r requirements.txt` to set up the development environment.
You should now be able to run `make test` successfully.

## Examples
You can use `runner.py` to run the sample scripts in `samples/`. It can also be used interactively.

```shell
> python runner.py samples/fibo.ms
```

```shell
> python runner.py
x = 5;
print(x);
```
