from Bio import Entrez

Entrez.email = 'robert.toth@thetatech.ai'

def search_pubmed(query):
    handle = Entrez.esearch(
        db      = 'pubmed',
        term    = query,
        sort    = 'relevance',
        retmode = 'xml',
        retmax  = 20,
    )
    records = Entrez.read(handle)
    return records

def main():
    query = 'glioblastoma'
    records = search_pubmed(query)
    print(f'Number of results for \'{query}\': {len(records["IdList"])}')

if __name__ == '__main__':
    main()
