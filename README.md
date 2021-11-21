# VerusVerifyAPI

Simple API to get Verus ID information + verify hashes and messages. Based on WSGI.

### Dependencies

0. Python 3
1. json
2. requests

### Setup

#### RPC Configuration

1. ```rpchost``` Specifies the hostname for the RPC server
2. ```rpcport``` Specifies the port for the RPC server
3. ```rpcuser``` Specifies the RPC user
4. ```rpcpass``` Specifies the RPC password for the aforementioned user

#### Running the API
After setup, run with the desired WSGI server with desired parameters. 

### Basic Usage

```
curl -H "Content-Type : application/json" -X POST -d '{"message" : "This is the VerusVerifyAPI", "signer" : "jbsci@", "signature" : "AXFhFAABQR9zKHrqydslEYVBAJnFh+7SCL5M1Df6as3zIJXjFUaAnRnYmg2EiQEiQcv/JN6OIBKgJZpXsWwA4c0pd87wdNwJ"}' https://<host>:<port>/verify
```

### Input/Output

```
route: /verify
in: {"message" : <message>, "signer" : <signer>, "signature" : <signature>} or {"hash" : <hash>, "signer" : <signer>, "signature" : <signature>} 
out: { valid : true|false }

route: /getidenity
In: {"identity" : <id>}
out: Identity information

route:/getvdxfid
In: {"vdxfuri" : <vdxfid>}
Out: VDXFID information
```
