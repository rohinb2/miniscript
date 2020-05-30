l = 0;
var u;
u = 1000000007;
while (l < u - 1) {
    var m;
    m = (l + u - (l + u) % 2) / 2;
    print(l, m, u);
    if (h >= m) {
        l = m;
    } else {
        u = m;
    }
}
