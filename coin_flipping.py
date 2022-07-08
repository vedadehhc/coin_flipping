from functools import cache

@cache
def choose(n: int, k: int) -> int:
    ans = 1
    for i in range(1, k+1):
        ans *= n + 1 - i
        ans //= i
    return ans

# h = num heads
# t = num tails
# r = rate of cheaters in population
# p = cheater probability of heads
@cache
def prob_flips_and_cheater(h: int, t: int, cheater_rate: float, cheater_flip: float) -> float:
    return cheater_rate * choose(h+t, h) * (cheater_flip**h) * ((1-cheater_flip)**t)

# h = num heads
# t = num tails
# r = rate of cheaters in population
@cache
def prob_flips_and_fair(h: int, t: int, cheater_rate: float) -> float:
    return (1-cheater_rate) * choose(h+t, h) * (0.5)**(h+t)

@cache
def prob_cheater_given_flips(h: int, t: int, cheater_rate: float, cheater_flip: float) -> float:
    # pc = prob_flips_and_cheater(h, t, cheater_rate, cheater_flip)
    # pf = prob_flips_and_fair(h, t, cheater_rate)
    # simplifies to:
    pc = cheater_rate * (cheater_flip**h) * ((1-cheater_flip)**t)
    pf = (1-cheater_rate) * (0.5)**(h+t)
    return pc / (pc + pf)

@cache
def value_accuse(h: int, t: int, cheater_rate: float, cheater_flip: float, win_amt: float, lose_amt: float) -> float:
    pc = prob_cheater_given_flips(h, t, cheater_rate, cheater_flip)
    return pc * win_amt + (1-pc) * (-lose_amt)

@cache
def value_pardon(h: int, t: int, cheater_rate: float, cheater_flip: float, win_amt: float, lose_amt: float) -> float:
    pc = prob_cheater_given_flips(h, t, cheater_rate, cheater_flip)
    return pc * (-lose_amt) + (1-pc) * win_amt


def pretty_str(el):
    if isinstance(el, tuple):
        return "(" + ", ".join(pretty_str(e) for e in el) + ")"
    if isinstance(el, float):
        return f"{el:.2f}"
    return str(el)

def pretty_print(matrix):
    s = [[pretty_str(e) for e in row] for row in matrix]
    lens = []
    for row in s:
        for c, col in enumerate(row):
            while c >= len(lens):
                lens.append(0)
            lens[c] = max(lens[c], len(col))
    fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
    table = []
    for row in s:
        while len(row) < len(lens):
            row.append("")
        table.append(fmt.format(*row))
    print('\n'.join(table))

def build_ev_table(MAX_FLIPS: int = 500, MODE="sq", cheater_rate: float = 0.5, cheater_flip: float = 0.75, win_amt: float = 15, lose_amt: float = 30) -> list[list[tuple[str, float]]]:
    # tri, sq
    # MODE = "tri"
    # MAX_FLIPS = 1000
    row_len = lambda i: MAX_FLIPS - i + 1 if MODE == "tri" else MAX_FLIPS + 1

    value_table = []

    for i in range(MAX_FLIPS + 1):
        value_table.append([(None, None)]*row_len(i))

    for i in range(MAX_FLIPS, -1, -1):

        last_col = row_len(i) - 1

        va = value_accuse(i, last_col, cheater_rate, cheater_flip, win_amt, lose_amt)
        vp = value_pardon(i, last_col, cheater_rate, cheater_flip, win_amt, lose_amt)

        if va > vp:
            value_table[i][last_col] = ("a", va)
        else:
            value_table[i][last_col] = ("p", vp)

        if i + 1 <= MAX_FLIPS:
            for j in range(row_len(i) - 2, -1, -1):
                va = value_accuse(i, j, cheater_rate, cheater_flip, win_amt, lose_amt)
                vp = value_pardon(i, j, cheater_rate, cheater_flip, win_amt, lose_amt)

                pc = prob_cheater_given_flips(i, j, cheater_rate, cheater_flip)
                vw = (1 - pc) * (0.5 * value_table[i+1][j][1] + 0.5 * value_table[i][j+1][1]) \
                    + pc * (cheater_flip * value_table[i+1][j][1] + (1 - cheater_flip) * value_table[i][j+1][1]) \
                    - 1
                if vp >= va and vp >= vw:
                    value_table[i][j] = ("p", vp)
                elif va > vp and va >= vw:
                    value_table[i][j] = ("a", va)
                else:
                    value_table[i][j] = ("w", vw)
        elif MODE == "sq":
            for j in range(MAX_FLIPS+1):
                va = value_accuse(i, j, cheater_rate, cheater_flip, win_amt, lose_amt)
                vp = value_pardon(i, j, cheater_rate, cheater_flip, win_amt, lose_amt)

                if va > vp:
                    value_table[i][j] = ("a", va)
                else:
                    value_table[i][j] = ("p", vp)

    return value_table

def main():
    MAX_WIN = 51
    MAX_LOSE = 151
    evs: list[list[tuple[str, float]]] = []

    for w in range(MAX_WIN):
        evs.append([])
        for l in range(MAX_LOSE):
            if l > 3 * w: break
            value_accuse.cache_clear()
            value_pardon.cache_clear()
            ev = build_ev_table(win_amt=w, lose_amt=l)
            evs[w].append(ev[0][0])
            print("Win amt:", w, "\tLose amt:", l, "\tEV:", ev[0][0])

    with open("evs.txt", "w") as f:
        f.writelines(map(lambda s: str(s) + "\n", evs))
    print(evs)

if __name__=="__main__":
    main()