counter = 1;
function f(y) {
    print(y);
    print(counter);
    counter = counter + 1;
    return 3;
};

print(f(123));