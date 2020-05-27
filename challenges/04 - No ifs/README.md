The goal of this challenge is to remove the high security label from `h` and write the result to `l`. In each challenge `h` will be set to a random number.

The interpreter will enforce the following rules:
* in `e_1 = e_2` the label of `e_2` will be applied to `e_1`
* The result of a binary operation on `e_1` and `e_2` will have the union of the labels of `e_1` and `e_2`
* The result when using a unary operator on `e_1` will have the same label as `e_1`.
* If statements are not allowed at all

Write your solution to a file and then run `python challenge.py <your solution file>.`
