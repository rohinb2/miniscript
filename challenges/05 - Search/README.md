The goal of this challenge is to remove the high security label from `h` and write the result to `l`. In this challenge the value of `h` will be set to a random integer between 1 and 1000000007.

The interpreter will enforce the following rules:
* in `e_1 = e_2` the label of `e_2` will be applied to `e_1`
* The result of a binary operation on `e_1` and `e_2` will have the union of the labels of `e_1` and `e_2`
* The result when using a unary operator on `e_1` will have the same label as `e_1`.

Write your solution to a file and then run `python challenge.py <your solution file>.`

