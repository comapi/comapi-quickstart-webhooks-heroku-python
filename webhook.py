# -*- coding: utf-8 -*-
# A basic website to demonstrate Facebook opt-in using Comapi and Python.
import hmac
import hashlib
import json
from flask import Flask, render_template, request
from flask_api import status

# Create our website app
app = Flask(__name__)

#######################
# Methods and functions
#######################
def hmac_sha1(data, key):
    # Create a HMAC-SHA-1 hash for the data, using the key
    raw_utf8 = data.encode("utf-8")
    key_utf8 = key.encode("utf-8")
    hashed = hmac.new(key_utf8, raw_utf8, hashlib.sha1)

    return hashed.hexdigest()


#################
# Register routes
#################
@app.route("/")
def get_index():
    # Render a basic page to make testing the end point easier
    return render_template('index.html')

@app.route('/', methods=['POST'])
def post_index():
    # Process data sent from Comapi
    try:
        # Grab the body and parse to a JSON object
        raw_body = request.get_data().decode("utf-8")

        if (raw_body is None):
            # No body, bad request.
            return "Bad request - No JSON body found!", status.HTTP_400_BAD_REQUEST

        # We have a request body so lets look at what we have

        # First lets ensure it hasn't been tampered with and it came from Comapi
        # We do this by checking the HMAC from the X-Comapi-Signature header
        request_hmac = request.headers.get("x-comapi-signature")

        if (request_hmac is None):
            # No HMAC, invalid request.
            return "Invalid request: No HMAC value found!", status.HTTP_401_UNAUTHORIZED
        else:
            # Validate the HMAC, ensure you has exposed the rawBody, see app.js for how to do this
            hash = hmac_sha1(raw_body, ">>>YOUR SECRET<<<")

            if (request_hmac != hash):
                # The request is not from Comapi or has been tampered with
                return "Invalid request: HMAC hash check failed!", status.HTTP_401_UNAUTHORIZED

        # Store the received event for later processing, remember you only have 10 secs to process, in this simple example we output to the console
        eventObj = json.loads(raw_body)

        print ("")        
        print ("Received a {0} event id: {1}".format(eventObj.get('name',''), eventObj.get('eventId','')))
        print(json.dumps(eventObj, indent=2)) # Pretty print the JSON
        print ("")

        # You could use queuing tech such as RabbitMQ, or possibly a distributed cache such as Redis       

        # Send worked
        return "Data accepted", status.HTTP_200_OK

    except Exception as ex:
        # Send failed
        print ("An error occurred: ")
        print ("{0}".format(ex))
        raise

# Fire up the local server
if __name__ == "__main__":
    app.run()