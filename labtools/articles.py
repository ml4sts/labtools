import os
import re 
import subprocess
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import click


def paperinfos(url):
    if "https://arxiv.org/html" in url:
        return scrape_arxviv(url)
    elif  "https://arxiv.org/abs" in url:
        return scrape_arxv(url)
    elif "https://proceedings.neurips.cc" in url or "https://papers.nips.cc" in url:
        return scrape_neurips(url)
    else:
        raise ValueError("Unsupported website. Please provide an Arxviv or Neurips URL.")

def format_authors(authors_raw):
    """Ensure authors are formatted correctly by adding spaces between first and last names."""
    # If authors_raw is a list, process each author separately
    if isinstance(authors_raw, list):
        authors_list = [
            re.sub(r'([a-z])([A-Z])', r'\1 \2', author).strip() 
            for author in authors_raw
        ]
    else:
        authors_list = [
            re.sub(r'([a-z])([A-Z])', r'\1 \2', author).strip() 
            for author in authors_raw.split(",")
        ]
    return ", ".join(authors_list)

def scrape_arxviv(url):
    """Scrape data from the Arxviv website."""
    Arx_html = requests.get(url).content
    Arx_content = BeautifulSoup(Arx_html,'html.parser')
    title = Arx_content.find('h1',{'class':"ltx_title ltx_title_document"}).get_text(strip=True)
    authors_section = Arx_content.find('div', {'class': 'ltx_authors'})
    authors_raw= [author.get_text().strip() for author in authors_section.find_all('span',{'class':"ltx_personname"})]
    authors = format_authors(authors_raw)
    abstract_section = Arx_content.find('div', {'class':"ltx_abstract"})
    abstract = abstract_section.find('h6', {'class': 'ltx_title_abstract'}).find_next('p').get_text(strip=True)
    pdf_link_element = Arx_content.find('a', class_='ar5iv-footer-button')
    pdf_link = pdf_link_element['href'] if pdf_link_element else url.replace('/html/', '/pdf/') + '.pdf'
    return title, authors, abstract, pdf_link


def scrape_arxv(url):
    """Scrape data from the Arxviv website."""
    Arxv_html = requests.get(url).content
    Arxv_content = BeautifulSoup(Arxv_html,'html.parser')
    title = Arxv_content.find('h1',{'class':"title mathjax"}).get_text(strip=True)
    authors_section = Arxv_content.find('div', {'class': 'authors'})
    authors_raw= [link.get_text() for link in authors_section.find_all('a')]
    authors = format_authors(authors_raw)
    abstract_block = Arxv_content.find('blockquote', class_='abstract')
    abstract = abstract_block.get_text(strip=True).replace('Abstract:', '').strip()
    pdf = Arxv_content.find('a', class_='abs-button download-pdf')['href']
    pdf_link = "https://arxiv.org" + pdf
    return title, authors, abstract, pdf_link
    
def scrape_neurips(url):
    """Scrape data from the Neurips website."""
    neurips_html = requests.get(url).content
    neurips_content = BeautifulSoup(neurips_html , 'html.parser')
    title= neurips_content.find('h4').get_text(strip=True)
    authors_raw = [a.get_text(strip=True) for a in neurips_content.find_all('i')]
    authors = format_authors(authors_raw)  
    abstract_header = neurips_content.find('h4', string="Abstract")
    abstract = abstract_header.find_next('p').find_next('p').get_text(strip=True)
    pdf_link_relative = neurips_content.find('a', {'class': 'btn btn-primary btn-spacer'})['href']
    base_url = url.rsplit('/', 1)[0] 
    pdf_link = urljoin(base_url, pdf_link_relative) 
    return title,authors, abstract, pdf_link


# GitHub integration functions
def create_github_issue(title, authors, abstract, pdf_link, reason):
    """Create a GitHub issue using gh CLI"""
    issue_title = f"Paper Review: {title}"
    issue_body = (
        f"**Authors:** {authors}\n\n"
        f"**Abstract:**\n{abstract}\n\n"
        f"[Read Full Paper]({pdf_link})\n\n"
        f"**Why Read This?**\n{reason}"
    )
    
    command = [
        "gh", "issue", "create",
        "--title", issue_title,
        "--body", issue_body
    ]
    
    env_vars = os.environ.copy()
    env_vars["GH_TOKEN"] = os.getenv("GH_TOKEN", "")
    
    result = subprocess.run(command, env=env_vars, capture_output=True, text=True, check=True)
    
    if result.returncode == 0:
        return True, "✅ Issue created successfully!"
    else:
        return False, f"❌ Failed to create issue. Error:\n{result.stderr}"


def create_github_paper_issue(paper_url , reason):
    """Create a GitHub issue for the specified paper URL with a reason."""
    # If reason is not provided, prompt the user
    if reason:
        click.echo(f"Creating issue for paper: {paper_url} with reason: {reason}")
    else:
        click.echo(f"Creating issue for paper: {paper_url} without a specified reason.")
    # Scrape paper details
    try:
        title, authors, abstract, pdf_link = paperinfos(paper_url)
        print(f"🔍 Debug - Raw Authors: {authors}")  # Debugging line
        if not title or not authors or not abstract or not pdf_link:
            raise ValueError("Scraper returned empty fields.")
        print(f"🔍 Debug - Title: {title}")
        print(f"🔍 Debug - Authors: {authors}")  # Should be a list
        print(f"🔍 Debug - Abstract: {abstract}")
        print(f"🔍 Debug - PDF Link: {pdf_link}")
    except Exception as e: 
        print(f"❌ Error scraping paper info: {e}") 
        return
# Create GitHub Issue with scraped details
    create_github_issue(title, authors, abstract, pdf_link, reason)
if __name__ == "__main__":
    create_github_paper_issue()