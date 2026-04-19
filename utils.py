from collections import defaultdict

def calculate_splitwise(expenses):
    debts = defaultdict(lambda: defaultdict(float))

    for payer, amount, participants in expenses:
        share = amount / len(participants)

        for p in participants:
            if p != payer:
                debts[p][payer] += share

    return debts


def pairwise_settlement(debts):
    people = set(debts.keys())
    for d in debts:
        for c in debts[d]:
            people.add(c)

    people = list(people)
    result = []

    for i in range(len(people)):
        for j in range(i + 1, len(people)):
            a = people[i]
            b = people[j]

            ab = debts[a][b] if b in debts[a] else 0
            ba = debts[b][a] if a in debts[b] else 0

            if ab > ba:
                result.append(f"{a} owes {b} ₹{round(ab - ba, 2)}")
            elif ba > ab:
                result.append(f"{b} owes {a} ₹{round(ba - ab, 2)}")

    return result


def simplify_debts(debts):
    net = defaultdict(float)

    for debtor in debts:
        for creditor in debts[debtor]:
            amt = debts[debtor][creditor]
            net[debtor] -= amt
            net[creditor] += amt

    people = list(net.items())
    result = []

    while True:
        creditor = max(people, key=lambda x: x[1])
        debtor = min(people, key=lambda x: x[1])

        if abs(creditor[1]) < 0.01 and abs(debtor[1]) < 0.01:
            break

        amt = min(creditor[1], -debtor[1])

        result.append(f"{debtor[0]} pays {creditor[0]} ₹{round(amt, 2)}")

        updated = []
        for p, val in people:
            if p == creditor[0]:
                val -= amt
            elif p == debtor[0]:
                val += amt
            updated.append((p, val))

        people = updated

    return result