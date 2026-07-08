import logging
from Bio import Entrez
from pprint import pprint
import argparse

Entrez.email = 'robert.toth@thetatech.ai'
MAX_RESULTS = 3

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(emoji)s %(message)s')
    return logging.getLogger(__name__)

def search_pubmed(query):
    handle = Entrez.esearch(db='pubmed', term=query, sort='relevance', retmode='xml', retmax=MAX_RESULTS)
    return Entrez.read(handle)['IdList']

def fetch_papers(id_list):
    ids = ','.join(id_list)
    handle = Entrez.efetch(db='pubmed', retmode='xml', id=ids)
    return Entrez.read(handle)['PubmedArticle']

def extract_paper_info(paper):
    article = paper['MedlineCitation']['Article']
    return {
        'title': article['ArticleTitle'],
        'authors': ', '.join([author['LastName'] for author in article['AuthorList']]),
        'journal': article['Journal']['ISOAbbreviation'],
        'year': article['ArticleDate'][0]['Year'] if 'ArticleDate' in article and article['ArticleDate'] else 'N/A',
        'doi': next((elem for elem in article['ELocationID'] if elem.attributes['EIdType'] == 'doi'), 'N/A') if 'ELocationID' in article and article['ELocationID'] else 'N/A',
        'pmid': paper['MedlineCitation']['PMID'],
        'abstract': article['Abstract']['AbstractText'][0] if 'Abstract' in article else 'No abstract available'
    }

def print_paper_info(logger, paper_info, index):
    print(f"\n{'='*80}")
    logger.info(f'📄 Paper {index}:', extra={'emoji': ''})
    print(f"📌 Title: {paper_info['title']}")
    print(f"👥 Authors: {paper_info['authors']}")
    print(f"📰 Journal: {paper_info['journal']}")
    print(f"📅 Year: {paper_info['year']}")
    print(f"🔗 DOI: {'https://doi.org/' + paper_info['doi'] if paper_info['doi'] != 'N/A' else 'N/A'}")
    print(f"🔍 PubMed: https://www.ncbi.nlm.nih.gov/pubmed/{paper_info['pmid']}")
    print(f"\n📝 ABSTRACT:")
    pprint(paper_info['abstract'], width=80, compact=True)
    print(f"\n{'='*80}\n")

def main(query):
    logger = setup_logging()
    logger.info('Starting PubMed search', extra={'emoji': '🔎'})

    search_results = search_pubmed(query)
    papers = fetch_papers(search_results)

    for i, paper in enumerate(papers, 1):
        paper_info = extract_paper_info(paper)
        print_paper_info(logger, paper_info, i)

    logger.info('PubMed search completed', extra={'emoji': '✅'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search PubMed for a given query.')
    parser.add_argument('--query', type=str, help='The query to search PubMed for.')
    args = parser.parse_args()
    main(args.query)
