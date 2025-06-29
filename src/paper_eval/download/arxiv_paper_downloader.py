import arxiv
import os
import requests
import logging

from typing import Optional

"""
Utility for downloading arXiv papers for a given query (expected to be the paper title).
"""


def _search_arxiv_for_papers(paper_title: str) -> Optional[str]:

    search = arxiv.Search(
        query=paper_title, max_results=1, sort_by=arxiv.SortCriterion.Relevance
    )
    results = list(search.results())
    if not results or len(results) == 0:
        print(f"No results found for query: {paper_title}")
        return None
    if paper_title.lower() not in results[0].title.lower():
        # Ensure we found the correct paper
        print(f"No results found for query: {paper_title}")
        return None

    paper = results[0]
    print(
        f"Found paper: {paper.title}\nAuthors: {', '.join([a.name for a in paper.authors])}\nPublished: {paper.published.date()}\nPDF URL: {paper.pdf_url}"
    )
    return paper.pdf_url


def _dl(pdf_url: str, output_dir: str) -> None:
    """
    Download the PDF from the given URL and save it to the output directory.
    """
    response = requests.get(pdf_url)
    if response.status_code == 200:
        # Try to extract arxiv_id from the URL
        arxiv_id = pdf_url.split("/")[-1].replace(".pdf", "")
        pdf_path = os.path.join(output_dir, f"{arxiv_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print(f"PDF downloaded to: {pdf_path}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")


def download_arxiv_paper(paper_title: str, output_dir="."):
    """
    Search arXiv for the given query and download the PDF of the top result.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf_url = _search_arxiv_for_papers(paper_title)

    if not pdf_url:
        logging.error(f"No results found for query: {paper_title}")
        return

    _dl(pdf_url, output_dir)


if __name__ == "__main__":
    download_arxiv_paper(
        paper_title="A Fast Iterative Robust Principal Component Analysis Method",
        output_dir=".",
    )
