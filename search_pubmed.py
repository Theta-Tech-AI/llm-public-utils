from Bio import Entrez

Entrez.email = 'robert.toth@thetatech.ai'
MAX_RESULTS = 10

def search_pubmed(query):
    handle = Entrez.esearch(
        db      = 'pubmed',
        term    = query,
        sort    = 'relevance',
        retmode = 'xml',
        retmax  = MAX_RESULTS,
    )
    return Entrez.read(handle)['IdList']

def fetch_papers(id_list):
    ids = ','.join(id_list)
    handle = Entrez.efetch(
        db      = 'pubmed',
        retmode = 'xml',
        id      = ids
    )
    return Entrez.read(handle)['PubmedArticle']

def citation_to_string(paper):
    article = paper["MedlineCitation"]["Article"]
    title = article["ArticleTitle"]
    first_author = article["AuthorList"][0]["LastName"]
    journal = article["Journal"]["ISOAbbreviation"]
    year = article["ArticleDate"][0]["Year"] if "ArticleDate" in article and article["ArticleDate"] else None
    if year: year = f' ({year})'
    doi = article["ELocationID"][0] if "ELocationID" in article and article["ELocationID"] else None
    if doi: doi = f' https://doi.org/{doi}'
    return f'{title} by {first_author} et al., {journal}{year}{doi}'

def main():
    query = 'glioblastoma'
    search_results = search_pubmed(query)
    papers = fetch_papers(search_results)
    for i, paper in enumerate(papers):
        citation = citation_to_string(paper)
        print(f'{i+1}) {citation}')
    

if __name__ == '__main__':
    main()
