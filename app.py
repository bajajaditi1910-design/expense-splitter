import streamlit as st
from collections import defaultdict

st.set_page_config(page_title="Splitwise App", layout="wide")

st.title("💸 Splitwise Clone - Group Expense Manager")

# ---------------- SESSION STATE ----------------
if "group_created" not in st.session_state:
    st.session_state.group_created = False
if "members" not in st.session_state:
    st.session_state.members = []
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "group_name" not in st.session_state:
    st.session_state.group_name = ""

# ---------------- RESET ----------------
if st.button("🔄 Reset App"):
    st.session_state.group_created = False
    st.session_state.members = []
    st.session_state.expenses = []
    st.session_state.group_name = ""
    st.rerun()

# ---------------- SPLITWISE LOGIC ----------------
def calculate_splitwise(expenses):
    debts = defaultdict(lambda: defaultdict(float))

    for payer, amount, participants in expenses:
        share = amount / len(participants)

        for p in participants:
            if p != payer:
                debts[p][payer] += share

    return debts


# -------- PAIRWISE SETTLEMENT --------
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


# -------- OPTIMIZED SETTLEMENT --------
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


# ---------------- CREATE GROUP ----------------
if not st.session_state.group_created:

    st.header("🧑‍🤝‍🧑 Create Group")

    with st.form("group_form"):
        group_name = st.text_input("Group Name")
        num_members = int(st.number_input("Number of Members", min_value=1, step=1))

        names = []
        for i in range(num_members):
            name = st.text_input(f"Member {i+1} Name", key=f"name_{i}")
            names.append(name)

        submit = st.form_submit_button("Create Group")

        if submit:
            if not group_name:
                st.error("Please enter group name")

            elif "" in names:
                st.error("Please enter all member names")

            else:
                st.session_state.group_created = True
                st.session_state.members = names
                st.session_state.group_name = group_name
                st.success(f"Group '{group_name}' created!")

# ---------------- MAIN APP ----------------
else:
    st.header(f"👥 Group: {st.session_state.group_name}")

    # -------- ADD EXPENSE --------
    st.subheader("💰 Add Expense")

    col1, col2 = st.columns(2)

    with col1:
        payer = st.selectbox("Who paid?", st.session_state.members)

    with col2:
        amount = st.number_input("Amount", min_value=0.0)

    participants = st.multiselect("Split among:", st.session_state.members)

    if st.button("Add Expense"):
        if not participants:
            st.error("Select participants")
        elif amount <= 0:
            st.error("Enter valid amount")
        else:
            st.session_state.expenses.append((payer, amount, participants.copy()))
            st.success("Expense added!")

    # -------- SHOW EXPENSES --------
    st.subheader("📄 All Expenses")

    if st.session_state.expenses:
        for e in st.session_state.expenses:
            st.write(f"{e[0]} paid ₹{e[1]} for {', '.join(e[2])}")
    else:
        st.info("No expenses added yet")

    debts = calculate_splitwise(st.session_state.expenses)

    # -------- DETAILED SPLIT --------
    st.subheader("📊 Detailed Split")

    if debts:
        for debtor in debts:
            for creditor in debts[debtor]:
                amt = debts[debtor][creditor]
                st.write(f"➡ {debtor} owes {creditor} ₹{round(amt,2)}")

    # -------- TOGGLE --------
    st.subheader("💸 Final Settlement")

    option = st.radio(
        "Choose settlement type:",
        ["Pairwise (Clear)", "Optimized (Minimum Transactions)"]
    )

    if st.button("Calculate Settlement"):

        if not st.session_state.expenses:
            st.warning("No expenses to calculate")
        else:
            if option == "Pairwise (Clear)":
                result = pairwise_settlement(debts)
            else:
                result = simplify_debts(debts)

            for r in result:
                st.success(r)