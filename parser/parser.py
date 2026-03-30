import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> S Conj S
AdjP -> Adj
AdjP -> Adj AdjP
AP -> PP
AP -> Adv
AP -> PP Adv
AP -> Adv PP
NP -> N
NP -> Det N
NP -> Det AdjP N
NP -> NP PP
PP -> P NP
VP -> V
VP -> V NP
VP -> V PP
VP -> V Adv
VP -> V NP PP
VP -> V PP Adv
VP -> V Adv PP
VP -> Adv VP
VP -> VP Conj VP
VP -> V NP NP
VP -> V AP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Turn sentence into individual tokens
    tokenized = nltk.word_tokenize(sentence)
    words = []

    # Process each token
    for token in tokenized:
        # Convert it to lowercase
        token = token.lower()

        # Only keep it if it has at least one alphabetic character
        if any(char.isalpha() for char in token):
            words.append(token)

    # Return words post-cleanup
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []

    # Go through every subtree and check if it is a NP
    for sub_t in tree.subtrees():
        if sub_t.label() == "NP":
            np_inside = False

            # Now go through all subtrees that are with that NP
            for c in sub_t.subtrees():
                # Ignore the subtree itself and check for nested NPs
                if c != sub_t and c.label() == "NP":
                    np_inside = True
                    break

            # If there is no nested NP found; it means it is a NP chunk
            if not np_inside:
                chunks.append(sub_t)

    return chunks


if __name__ == "__main__":
    main()
