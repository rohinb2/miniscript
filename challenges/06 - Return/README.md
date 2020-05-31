The goal of this challenge is to remove the high security label from `h` and write the result to `l`. In each challenge `h` will be set to a random boolean.

The interpreter will enforce the following rules:
* in `e_1 = e_2` the label of `e_2` will be applied to `e_1`
* The result of an arithmetic binary operation on `e_1` and `e_2` will have the union of the labels of `e_1` and `e_2`
* The second argument of a short-circuit boolean operator is evaluated in the security context of the first 
* The result when using a unary operator on `e_1` will have the same label as `e_1`. 
* The result of evaluating an expression has at least the security label of the current security context.
* The security context is raised to the condition inside conditionals such as if and while

In this challenge you are allowed to use arithmetic and boolean expressions, if and while control structures and function calls.

Write your solution to a file and then run `python challenge.py <your solution file>.`
