def bmvj_compress(data: bytes) -> bytes:
    if len(data) > 65535:
        raise ValueError('mode-5 body uses a 16-bit decoded length; maximum 65535 bytes')
    if not data:
        return bytes(7)
    def make_tree(x):
        base = [[i] for i, v in enumerate(x) if v]
        if not base:
            return [""] * len(x)
        elif len(base) == 1:
            return ["0" if v else "" for v in x]
        work = base[:]
        for __ in range(15):
            w = sorted(work, key=lambda a: sum(x[i] for i in a))
            work = base + [w[i] + w[i+1] for i in range(0, len(w) - 1, 2)]
        w = sorted(work, key=lambda a: sum(x[i] for i in a))[:(len(base)-1)*2]
        y = sum(w, [])
        z = [""] * len(x)
        c, l = 0, 0
        for i in sorted(range(len(x)), key=y.count):
            if not x[i]:
                continue
            c <<= (y.count(i) - l)
            l = y.count(i)
            z[i] = f"{{:0{l}b}}".format(c)
            c += 1
        return z
    syms = []
    offs = []
    i = 0
    while i < len(data):
        best_match = 0,
        for j in reversed(range(i - 512, i)):
            if j < 0:
                break
            if data[i:i+3] != data[j:j+3]:
                continue
            k = 3
            while k < 8 and i+k < len(data) and data[i+k] == data[j+k]:
                k += 1
            if best_match[0] < k:
                best_match = k, j
        if best_match[0]:
            syms.append(best_match[0] + 253)
            offs.append(i - best_match[1] - 1)
            i += best_match[0]
        else:
            syms.append(data[i])
            offs.append(None)
            i += 1
    if max(syms) != min(syms):
        syms_count = [syms.count(sym) for sym in range(max(syms) + 1)]
        syms_tree = make_tree(syms_count)
        lens = [len(ch) + 2 for ch in syms_tree]
        lens_extra = ["" for __ in syms_count]
        i = 0
        while i < len(lens):
            if lens[i] > 2:
                i += 1
                continue
            k = 1
            while i+k < len(lens) and lens[i+k] <= 2:
                k += 1
            if k in (2, 19):
                k -= 1
            if k == 1:
                lens[i] = 0
            elif k < 20:
                lens[i:i+k] = [1]
                lens_extra[i:i+k] = [f"{k-3:04b}"]
            else:
                lens[i:i+k] = [2]
                lens_extra[i:i+k] = [f"{k-20:09b}"]
            i += 1
        lens_tree = make_tree([lens.count(l) for l in range(max(lens) + 1)])
    else:
        syms_tree = None
    offs_count = [0] * 10
    for off in offs:
        if off is None:
            continue
        elif off <= 2:
            offs_count[off] += 1
        else:
            shift = 8
            while not (off & (1 << shift)):
                shift -= 1
            offs_count[shift + 1] += 1
    while offs_count and not offs_count[-1]:
        del offs_count[-1]
    offs_tree = make_tree(offs_count)
    if syms_tree:
        next_bin = f"{len(lens_tree):05b}"
        l = 0
        while l < len(lens_tree):
            if l == 3:
                k = 0
                while k < 3 and not lens_tree[l+k]:
                    k += 1
                next_bin += f"{k:02b}"
                l += k
            cl = len(lens_tree[l])
            if cl < 7:
                next_bin += f"{cl:03b}"
            else:
                next_bin += "1" * (cl - 4) + "0"
            l += 1
        next_bin += f"{len(syms_tree):09b}"
        next_bin += "".join(lens_tree[l] + e for l, e in zip(lens, lens_extra))
    else:
        next_bin = f"00001000000000000{syms[0]:09b}"
    if offs_tree:
        next_bin += f"{len(offs_tree):04b}"
        for ch in offs_tree:
            cl = len(ch)
            if cl < 7:
                next_bin += f"{cl:03b}"
            else:
                next_bin += "1" * (cl - 4) + "0"
    else:
        next_bin += "0001000"
    ret = len(syms).to_bytes(2, "big")
    for sym, off in zip(syms, offs):
        ret += bytes(int(next_bin[i:i+8], 2) for i in range(0, len(next_bin) - 7, 8))
        next_bin = next_bin[len(next_bin)&~7:]
        if syms_tree:
            next_bin += syms_tree[sym]
        if off is not None:
            if off < 2:
                next_bin += offs_tree[off]
            else:
                shift = 8
                while not (off & (1 << shift)):
                    shift -= 1
                next_bin += offs_tree[shift + 1] + f"{off:b}"[1:]
    next_bin += "0000000"
    ret += bytes(int(next_bin[i:i+8], 2) for i in range(0, len(next_bin) - 7, 8))
    if len(ret) > 65535:
        raise ValueError('mode-5 compressed stream exceeds its 16-bit length field')
    return b"\0\0\5" + len(ret).to_bytes(2, "little") \
        + len(data).to_bytes(2, "little") + bytes(2) + ret
