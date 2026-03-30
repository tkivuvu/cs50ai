import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def count_gene(name, one_gene, two_genes):

    # What to return when basing off of this person's sets
    if name in two_genes:
        return 2
    if name in one_gene:
        return 1

    return 0


def proba_pass(parent_name, one_gene, two_genes):

    # Basing it off of the parent's genes and mutation; compute prob that
    # parent passes gene to child
    genes = count_gene(parent_name, one_gene, two_genes)
    m = PROBS["mutation"]

    if genes == 2:
        return 1 - m
    if genes == 1:
        return 0.5
    return m


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint = 1.0

    for n, i in people.items():
        g = count_gene(n, one_gene, two_genes)
        has_trait = (n in have_trait)

        mother = i["mother"]
        father = i["father"]

        # Gene count probability
        if mother is None and father is None:
            p_gene = PROBS["gene"][g]
        else:
            p_m = proba_pass(mother, one_gene, two_genes)
            p_f = proba_pass(father, one_gene, two_genes)

            if g == 2:
                p_gene = p_m * p_f
            elif g == 1:
                p_gene = p_m * (1 - p_f) + (1 - p_m) * p_f
            else:
                p_gene = (1 - p_m) * (1 - p_f)

        # Based off of gene count; trait probablity
        p_trait = PROBS["trait"][g][has_trait]

        joint *= (p_gene * p_trait)

    return joint


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for pers in probabilities:
        genes = count_gene(pers, one_gene, two_genes)
        trait = (pers in have_trait)

        probabilities[pers]["gene"][genes] += p
        probabilities[pers]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for pers in probabilities:

        # Gene distr normalization
        total_g = sum(probabilities[pers]["gene"].values())
        if total_g != 0:
            for gene_count in probabilities[pers]["gene"]:
                probabilities[pers]["gene"][gene_count] /= total_g

        # Trait distr normalization
        total_t = sum(probabilities[pers]["trait"].values())
        if total_t != 0:
            for has_trait in probabilities[pers]["trait"]:
                probabilities[pers]["trait"][has_trait] /= total_t


if __name__ == "__main__":
    main()
