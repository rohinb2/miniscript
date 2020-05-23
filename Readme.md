# Langsec Project

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
