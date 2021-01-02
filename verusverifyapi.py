#!/usr/bin/env python

'''
Basic Functionality:
    curl -H "Content-Type:application/json" -X POST -d {"message" : "This is a test message", "signer" : "jbsci@", 
    "signature" : "Af+4EQrrrABQSA1qs5h3yc553W8ulMVU+cVhJgXnkXHeZyEvP7oX9Iiizq3LIY1kWCyrWromhRv7CO1mdViKffFd6jGku0SiCSM"}' localhost:5000/verifymessage

Requires configuraiton under the config heading for RPC communication and API port. Requires uWSGI for hosting.

Written 2020 by jbsci <j@jbsci.dev>
'''

#-# Imports #-#

import sys
import requests
import json
from requests.auth import HTTPBasicAuth

#--# Config #--#

#Verus RPC
rpchost='http://localhost'
rpcport=27486
rpcuser='verus'
rpcpass='<rpcpassword>'

#---# Functions #---#

def verusquery(method, params, rpcid=" "):
    '''
    Function to query the Verus RPC client. Builds payload based on methods and parameters.
    '''
    if type(params) != list:
        print("ERROR: Params must be given as a list")
    payload = {"jsonrpc" : 1.0, "id" : rpcid, "method" : method, "params" : params}
    response = requests.post("{:s}:{:d}".format(rpchost, rpcport), json=payload, headers={"content-type" : "text/plain;"}, auth=HTTPBasicAuth(rpcuser, rpcpass)).json()
    return response

def verusverify(thing_to_verify, signer, signature, method, rpcid):
    '''
    Uses given rpc method to perform verification of a File (verifyfile), Filehash (verifyhash),
    or message (verifymessage)
    '''
    result = verusquery(method, [signer, signature, thing_to_verify], rpcid=rpcid)
    return result

def verusidentity(identity):
    '''
    Queries RPC to check if identity exists and returns information.

    Can use identity or identity address.
    '''
    result = verusquery("getidentity", [identity], rpcid="getidentity")
    if result["result"]:
        del result['result']['cansignfor']
        del result['result']['canspendfor']
        return result
    else:
        return result


#----# API #----#

def verifyhash(payload):
    result = verusverify(payload["hash"], payload["signer"], payload["signature"], 'verifyhash', rpcid='verifyhash')['result']
    if result:
        return {"valid" : "true"}
    else:
        return {"valid" : "false"}

def verifymessage(payload):
    result =  verusverify(payload['message'], payload['signer'], payload['signature'], 'verifymessage', rpcid='verifymessage')['result']
    if result:
        return {"valid" : "true"}
    else:
        return {"valid" : "false"}

def getid(payload):
    if "id" not in payload.keys():
        return {"error" : 4, "error_detail" : "1 parameter given, but no ID specified"}
    idresult = verusidentity(payload["id"])
    if idresult["result"] is None:
        return {"error" : 5, "error_detail" : "ID not found"}
    else:
        return idresult["result"]

def verifyparser(payload):
    inparams = list(payload.keys())
    if len(inparams) > 3:
        return {"error" : 1, "error_detail" : "Too many input parameters"}
    elif len(inparams) == 3:
        if "signer" and "signature" not in inparams:
            return {"error" : 2, "error_detail" : "Missing signer or signature"}
        else:
            inparams.remove('signer')
            inparams.remove('signature')
            verifytype = inparams[0]
            if verifytype == "hash":
                result = verifyhash(payload)
            elif verifytype == "message":
                result = verifymessage(payload)
            else:
                return {"error" : 3, "error_detail" : "Missing hash or message to verify"}
    else:
        return {"error" : 1, "error_detail" : "Invalid number of input parameters"}
    return result

def application(environ, start_response):
    if environ["REQUEST_METHOD"] == 'POST':
        headers =   [('content-type', 'application/json')]
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size=0
        request_body = environ['wsgi.input'].read(request_body_size)
        path = environ['PATH_INFO'].split('/')[1]
        data = json.loads(request_body)
        if path == "verify":
            result = verifyparser(data)
        elif path == "id":
            result = getid(data)
        else:
            start_response('406 Not Acceptable', headers)
            result = {'error' : 0, "error_detail" : "Invalid request"}
            return [json.dumps(result).encode('utf-8')]
        start_response('200 OK', headers)
        return [json.dumps(result).encode('utf-8')]
    else:
        start_response('406 Not Acceptable', headers)
        result = {'error' : 0, "error_detail" : "Invalid Request"}
        return [json.dumps(result).encode('utf-8')]