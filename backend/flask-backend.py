#--------------------------------------------------imports--------------------------------------------------------------#
import os
from flask import Flask, request, jsonify, make_response
from multiprocessing.managers import BaseManager
from werkzeug.utils import secure_filename
from flask_cors import CORS
#---------------------------------------------------------end of imports-------------------------------------------------#
#creates an instance of the Flask application
app = Flask(__name__)
CORS(app)
# initialize manager connection
manager = BaseManager(("", 5602), b"password")
manager.register("query_index")
manager.connect()
manager.register("insert_into_index")

#----------------------------------------------------------'/query' routing------------------------------------------------------#
#routes the 'query_index' function to local URL 
@app.route('/query', methods=["GET"])
def query_index():
    global index
    # Gets a text response from the request 
    query_text = request.args.get("text",None)
    # Check if query is empty 
    if query_text is None:
        return (
            'No text found please include a text at the text="" parameter in the URL',
            400,
        )
    # manager connects the query index to 
    response = manager.query_index(query_text)._getvalue()
    return str(response), 200
#-------------------------------------------------------'/query' routing------------------------------------------------#
#routes the 'uploadFile' function to local url : accepts only POST requests 
@app.route("/uploadFile", methods=["POST"])
def upload_file():
    global manager
    # Checks if incoming request contains a "file"
    if "file" not in request.files:
        #returns "400" bad request
        return "Please send a POST request with a file", 400
    #initialises file_path to none for reassignment 
    filepath = None
    # Handles exceptions for file uploads 
    try:
        # obtains file POST request from HTML form
        uploaded_file = request.files["file"]
        # runs security checks on "uploaded_file"
        filename = secure_filename(uploaded_file.filename)
        # creates a file path for uploaded file  
        filepath = os.path.join("documents", os.path.basename(filename))
        # saves the 'uploaded_file' in the file path
        uploaded_file.save(filepath)
        # Checks if "file-name" was included as doc_id
        if request.form.get("filename_as_doc_id", None) is not None:
            #if true: stores the 'filename' as 'doc_id' using the manager object
            manager.insert_into_index(filepath, doc_id=filename)
        else:
            # else: use manager object to generate a new 'doc_id'
            manager.insert_into_index(filepath)
    except Exception as e:
        # cleanup temp file
        if filepath is not None and os.path.exists(filepath):
            os.remove(filepath)
        return "Error: {}".format(str(e)), 500

    # cleanup temp file
    if filepath is not None and os.path.exists(filepath):
        os.remove(filepath)

    return "File inserted!", 200
#-------------------------------------------------------------------------------
@app.route("/")
def home():
    return 'Hello World'
#root path identification
if __name__ == "__main__":  
    #route execution in local host
    app.run(host="0.0.0.0", port=5601)

