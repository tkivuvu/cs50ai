import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pgs = list(corpus.keys())
    n_pgs = len(pgs)

    # If there arent any outgoing links even it to all pages
    links = corpus.get(page, set())
    if not links:
        return {p: 1 / n_pgs for p in pgs}

    # Can jum to any random page as base proba
    distr = {p: (1 - damping_factor) / n_pgs for p in pgs}

    link_p = damping_factor / len(links)
    for linked_page in links:
        distr[linked_page] += link_p

    return distr


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pgs = list(corpus.keys())

    # Page vists initially start at 0
    counts = {page: 0 for page in pgs}

    # Start by choosing page at random in uniform fashion
    current_p = random.choice(pgs)
    counts[current_p] += 1

    # And going forward...
    for _ in range(n - 1):
        distribution = transition_model(corpus, current_p, damping_factor)

        # Choose next page based on the distr
        next_p = random.choices(
            population=list(distribution.keys()),
            weights=list(distribution.values()),
            k=1
        )[0]

        counts[next_p] += 1
        current_p = next_p

    # Counts now become probabilities
    return {page: counts[page] / n for page in pgs}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pgs = list(corpus.keys())
    n_pgs = len(pgs)

    # If pages have no outgoing links treat them as linking to all pages
    outgoing_l = {}
    for p in pgs:
        if corpus[p]:
            outgoing_l[p] = set(corpus[p])
        else:
            outgoing_l[p] = set(pgs)

    # Uniform initialization of PageRank values
    ranks = {p: 1 / n_pgs for p in pgs}

    while True:
        newer_ranks = {}

        for p in pgs:

            # Sum over every page linking to p
            total = 0.0
            for q in pgs:
                if p in outgoing_l[q]:
                    total += ranks[q] / len(outgoing_l[q])

            newer_ranks[p] = (1 - damping_factor) / n_pgs + damping_factor * total

        # Values should not change by over 0.001
        change_compute = max(abs(newer_ranks[p] - ranks[p]) for p in pgs)
        ranks = newer_ranks

        if change_compute <= 0.001:
            break

    return ranks


if __name__ == "__main__":
    main()
