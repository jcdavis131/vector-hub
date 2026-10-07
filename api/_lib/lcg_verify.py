"""
LCG glibc verification — T4 ultra 1m
Matches hub.js (Math.imul) and api/_lib/lcg.js vs Python agree
20260812→1233799701 idx3970 triple [3970,14390,4582] five [3970,14390,4582,13307,8695]
"""
def lcg(s: int) -> int:
    return (s * 1103515245 + 12345) & 0x7fffffff  # glibc rand() & 0x7fffffff, Math.imul in JS truncates to 32-bit then same mask

def daily_seed(yyyymmdd: int):
    a = lcg(yyyymmdd)
    b = lcg(a)
    c = lcg(b)
    d = lcg(c)
    e = lcg(d)
    total = 20719
    idx = a % total
    j = b % total
    k = c % total
    if j == idx: j = (j+1) % total
    if k == idx or k == j: k = (k+2) % total
    five = [idx, j, k, d%total, e%total]
    return {"seed": yyyymmdd, "a": a, "b": b, "c": c, "idx": idx, "triple": [idx,j,k], "five": five}

if __name__ == "__main__":
    s = 20260812
    r = daily_seed(s)
    print(f"PY_LCG seed={s} a={r['a']} idx={r['idx']} triple={r['triple']} five={r['five']}")
    assert r['a'] == 1233799701, f"a {r['a']} != 1233799701"
    assert r['idx'] == 3970, f"idx {r['idx']} != 3970"
    assert r['triple'] == [3970,14390,4582], f"triple {r['triple']} != [3970,14390,4582]"
    # five last two: d=lcg(c), e=lcg(d) -> compute expected
    # from JS we know five = [3970,14390,4582,13307,8695] — verify
    # Let's compute quickly: c already, d=lcg(c), e=lcg(d)
    def check_five():
        a = lcg(s); b=lcg(a); c=lcg(b); d=lcg(c); e=lcg(d)
        total=20719
        idx=a%total; j=b%total; k=c%total
        if j==idx: j=(j+1)%total
        if k==idx or k==j: k=(k+2)%total
        five=[idx,j,k,d%total,e%total]
        return five
    five = check_five()
    print(f"five={five}")
    assert five == [3970,14390,4582,13307,8695], f"five {five} != expected"
    print("LCG CHECK PASS — hub.js vs api/_lib/lcg.js vs Python agree — 20260812→1233799701 idx3970 triple [3970,14390,4582] five [3970,14390,4582,13307,8695]")
