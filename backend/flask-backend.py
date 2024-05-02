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

#----------------------------------------------------------routing------------------------------------------------------#
#routes the 'query_index' function to local URL 
@app.route('/query', methods=["GET"])
def query_index():
    global index
    # Gets a response from the request 
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
#-------------------------------------------------------end of routing------------------------------------------------#
@app.route("/uploadFile", methods=["POST"])
def upload_file():
    global manager
    if "file" not in request.files:
        return "Please send a POST request with a file", 400

    filepath = None
    try:
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join("documents", os.path.basename(filename))
        uploaded_file.save(filepath)

        if request.form.get("filename_as_doc_id", None) is not None:
            manager.insert_into_index(filepath, doc_id=filename)
        else:
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

