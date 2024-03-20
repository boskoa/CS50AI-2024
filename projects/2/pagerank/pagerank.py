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
    print("FOO", pages)

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )
    print("BAR", pages)

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
        for link in corpus[page]:
            page_probabilities[link] = damping_factor / len(corpus[page]) + (
                1 - damping_factor
            ) / (len(corpus[page]) + 1)
        random_page = random.choice([x for x in corpus if x != page])
        if random_page in page_probabilities.keys():
            page_probabilities[random_page] += (1 - damping_factor) / (
                len(corpus[page]) + 1
            )
        else:
            page_probabilities[random_page] = (1 - damping_factor) / (
                len(corpus[page]) + 1
            )

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
                list(sample.keys()), cum_weights=list(sample.values()), k=1
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
    ranks = dict.fromkeys(pages, 1 / len(corpus))
    ranks_copy = dict.fromkeys(ranks, 1)
    links_to_page = dict()
    condition = True

    for page in corpus.items():
        for link in page[1]:
            if link not in links_to_page.keys():
                links_to_page[link] = set()
                links_to_page[link].add(page[0])
            else:
                links_to_page[link].add(page[0])
    print("LINKS", links_to_page)
    while condition:
        condition = False
        ranks_copy = ranks.copy()
        for page in links_to_page.items():
            ranks[page[0]] = (1 - damping_factor) / len(pages)
            for i in page[1]:
                ranks[page[0]] += ranks_copy[i] / len(corpus[i])
        for page in pages:
            if ranks_copy[page] - ranks[page] > 0.001:
                condition = True

    print("START", ranks)
    return ranks


if __name__ == "__main__":
    main()
