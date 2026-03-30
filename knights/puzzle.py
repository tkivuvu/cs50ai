from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Symbol for what A said regarding puzzle 3
A_knight = Symbol("A said 'I am a Knight'")
A_knave = Symbol("A said 'I am a Knave'")


# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # A is either a Knight or a Knave but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    # If A is a knight their statement is true
    Implication(AKnight, And(AKnight, AKnave)),
    # If A is a knave their statement is false
    Implication(AKnave, Not(And(AKnight, AKnave)))
)


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # A is either a knight or a knave but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    # B is either a knight or a knave but not both
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    # A is a knight if and only if they are telling the truth re "We are both knaves."
    Biconditional(AKnight, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."

# Variable for A statement
same = Or(
    And(AKnight, BKnight),
    And(AKnave, BKnave)
)
# Variable for B statement
different = Or(
    And(AKnight, BKnave),
    And(AKnave, BKnight)
)
knowledge2 = And(
    # A is either a knight or a knave but not both
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    # B is either a knight or a knave but not both
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    # A and B are knights if and only if their statements are truthful
    Biconditional(AKnight, same),
    Biconditional(BKnight, different)

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."

# Variable to check truthfulness of A's possible statements
A_true = Or(
    And(A_knight, AKnight),
    And(A_knave, AKnave)
)
knowledge3 = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),

    Or(A_knight, A_knave),
    Not(And(A_knight, A_knave)),

    Biconditional(AKnight, A_true),

    Biconditional(BKnight, A_knave),

    Biconditional(BKnight, CKnave),

    Biconditional(CKnight, AKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
