#--------------------------------------------------imports--------------------------------------------------------------#
from flask import Flask
import os
from llama_index.core import (SimpleDirectoryReader,VectorStoreIndex,StorageContext,load_index_from_storage,)
from dotenv import load_dotenv
from multiprocessing import Lock
from multiprocessing.managers import BaseManager
load_dotenv()
#---------------------------------------------------------end of imports-------------------------------------------------#

#creates an instance of the Flask application
app = Flask(__name__)
# a variable named 'api-key' that stores the value of the 'API-KEY' from the local environment
api_key = os.getenv('API_KEY')
#------------------------------------------------------indexing block-----------------------------------#    

index = None
lock = Lock()
def initialize_index():
    # indicates the lexical scope of the 'index' variable
    global index
    # a variable named 'storage_context' that stores the StorageContext instance
    with lock:
        storage_context = StorageContext.from_defaults(persist_dir='backend/document')
        # Check if document directory exists
        if os.path.exists('backend/document'):
            # retrieves vector indices from local storage directory
            index = load_index_from_storage(storage_context)
        else:
            # a variable named 'documents' that loads the documents from the 'paul-graham-file' directory
            documents = SimpleDirectoryReader("backend/paul-graham-file").load_data()
            # generates new vector indices based on loaded documents
            index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
            # store vector indices inside 'backend/document' directory
            storage_context.persist('backend/document')
            pass 
#---------------------------------------------------------end of indexing blocks----------------------------------#

#----------------------------------------------------------routing------------------------------------------------------#
#routes the 'query_index' function to local URL 
@app.route('/query', methods=["GET"])
def query_index(query_text):
    global index
    #creates a query engine instance
    query_engine = index.as_query_engine()
    # uses the query engine to answer the 'query_text' and stores it as 'response'
    response = query_engine.query(query_text)
    # returns a tuple
    return str(response), 200
#-------------------------------------------------------end of routing------------------------------------------------#

def insert_into_index(doc_text, doc_id=None):
    global index
    document = SimpleDirectoryReader(input_files=[doc_text]).load_data()[0]
    if doc_id is not None:
        document.doc_id = doc_id

    with lock:
        index.insert(document)
        index.storage_context.persist()



#root path identification
if __name__ == "__main__":  
    print("initialising index")
    initialize_index()

    # manager listens for changes in the network "" and is assigned the port number '5602' and a password for shared threading processes
    manager = BaseManager(("", 5602), b"password")
    # manager registers the 'query-index' function with the server for client usage
    manager.register("insert_into_index", insert_into_index)
    manager.register("query_index", query_index)
    server = manager.get_server()

    print("starting server...")
    # continual listening on server
    server.serve_forever()

