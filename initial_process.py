from database.mongodb import get_source_documents
from database.solrdb import batch_index_to_solr
from functions.documents_operations import process_documents, process_documents_without_vectors
from helpers.mp import create_process_in_pool
import asyncio


async def initial_process(mul:bool=True):
    batch = 100000
    skip = 0
    while True:
        valid_docs = await get_source_documents(batch, skip)
        if len(valid_docs) == 0:
            break
        if mul:
            processed_documents = create_process_in_pool(process_documents, valid_docs)
            processed_documents = [doc for doc in processed_documents if doc is not None]
        else:
            processed_documents = [process_documents(doc) for doc in valid_docs if doc is not None]
            processed_documents = [doc for doc in processed_documents if doc is not None]
        await batch_index_to_solr(processed_documents)
        # processed_documents = [process_documents(document) for document in valid_docs]
        # print(processed_documents[:10])
        skip += batch

if __name__ == '__main__':
    asyncio.run(initial_process(mul=False))