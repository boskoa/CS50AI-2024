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
    page_probabilities = dict()

    if not corpus[page]:
        for corpus_page in corpus:
            page_probabilities[corpus_page] = 1 / len(corpus)

    else:
        for p in corpus:
            page_probabilities[p] = (1 - damping_factor) / len(corpus)

        for link in corpus[page]:
            page_probabilities[link] += damping_factor / len(corpus[page]) + (
                1 - damping_factor
            ) / (len(corpus[page]) + 1)

    return page_probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page = random.choice(list(corpus.keys()))
    sample = transition_model(
        corpus, page, damping_factor
    )
    ranks = dict.fromkeys(corpus.keys(), 0)

    for x in range(n):
        ranks[page] += 1
        page = list(
            random.choices(
                list(sample.keys()), weights=list(sample.values()), k=1
            )
        )[0]
        sample = transition_model(corpus, page, damping_factor)

    for key, value in ranks.items():
        ranks[key] = value / n

    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = corpus.keys()
    N = len(corpus)
    ranks = dict.fromkeys(pages, 1 / N)
    condition = True

    while condition:
        condition = False
        previous_ranks = ranks.copy()
        for page in pages:
            first_condition = (1 - damping_factor) / N
            second_condition = 0
            for p, links in corpus.items():
                if page in links:
                    second_condition += previous_ranks[p] / len(links)
                elif len(links) == 0:
                    second_condition += previous_ranks[p] / N
            ranks[page] = first_condition + damping_factor * second_condition
            if abs(ranks[page] - previous_ranks[page]) > 0.001:
                condition = True

    return ranks


if __name__ == "__main__":
    main()
