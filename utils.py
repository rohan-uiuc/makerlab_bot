import os
import pickle
import time
from urllib.parse import urlparse, urljoin

import faiss
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

book_url = 'https://g.co/kgs/2VFC7u'
book_file = "Book.pdf"
url = 'https://makerlab.illinois.edu/'
def get_search_index(pickle_file, index_file, embeddings):

    if os.path.isfile(pickle_file) and os.path.isfile(index_file) and os.path.getsize(pickle_file) > 0:
        # Load index from pickle file
        with open(pickle_file, "rb") as f:
            search_index = pickle.load(f)
    else:
        source_chunks = create_chunk_documents()

        search_index = search_index_from_docs(source_chunks, embeddings=embeddings)

        faiss.write_index(search_index.index, index_file)

        # Save index to pickle file
        with open(pickle_file, "wb") as f:
            pickle.dump(search_index, f)

    return search_index


def create_chunk_documents():
    sources = fetch_data_for_embeddings(url, book_file, book_url)
    # print("sources" + str(len(sources)))

    splitter = CharacterTextSplitter(separator=" ", chunk_size=800, chunk_overlap=0)

    source_chunks = splitter.split_documents(sources)

    for chunk in source_chunks:
        print("Size of chunk: " + str(len(chunk.page_content) + len(chunk.metadata)))
        if chunk.page_content is None or chunk.page_content == '':
            print("removing chunk: "+ chunk.page_content)
            source_chunks.remove(chunk)
        elif len(chunk.page_content) >=1000:
            print("splitting document")
            source_chunks.extend(splitter.split_documents([chunk]))
    # print("Chunks: " + str(len(source_chunks)) + "and type " + str(type(source_chunks)))
    return source_chunks


def fetch_data_for_embeddings(url, book_file, book_url):
    sources = get_website_data(url)
    sources.extend(get_document_data(book_file, book_url))
    return sources

def get_website_data(index_url):
    # Get all page paths from index
    paths = get_paths(index_url)

    # Filter out invalid links and join them with the base URL
    links = get_links(index_url, paths)

    return get_content_from_links(links, index_url)


def get_content_from_links(links, index_url):
    content_list = []
    for link in set(links):
        if link.startswith(index_url):
            page_data = requests.get(link).content
            soup = BeautifulSoup(page_data, "html.parser")

            # Get page content
            content = soup.get_text(separator="\n")
            # print(link)

            # Get page metadata
            metadata = {"source": link}

            content_list.append(Document(page_content=content, metadata=metadata))
    time.sleep(1)
    # print("content list" + str(len(content_list)))
    return content_list


def get_paths(index_url):
    index_data = requests.get(index_url).content
    soup = BeautifulSoup(index_data, "html.parser")
    paths = set([a.get('href') for a in soup.find_all('a', href=True)])
    return paths


def get_links(index_url, paths):
    links = []
    for path in paths:
        url = urljoin(index_url, path)
        parsed_url = urlparse(url)
        if parsed_url.scheme in ["http", "https"] and "squarespace" not in parsed_url.netloc:
            links.append(url)
    return links


def get_document_data(book_file, book_url):
    document_list = []
    with open(book_file, 'rb') as f:
        pdf_reader = PdfReader(f)
        for i in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[i].extract_text()
            metadata = {"source": book_url}
            document_list.append(Document(page_content=page_text, metadata=metadata))

    # print("document list" + str(len(document_list)))
    return document_list

def search_index_from_docs(source_chunks, embeddings):
    # Create index from chunk documents
    # print("Size of chunk" + str(len(source_chunks)))
    search_index = FAISS.from_texts([doc.page_content for doc in source_chunks], embeddings, metadatas=[doc.metadata for doc in source_chunks])
    return search_index
def generate_answer(chain, index, question):
    #Get answer
    answer = chain(
        {
            "input_documents": index.similarity_search(question, k=4),
            "question": question,
        },
        return_only_outputs=True,
    )["output_text"]

    return answer