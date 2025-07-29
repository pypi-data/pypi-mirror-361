# infodata' u2python module to work with ..GRAPH... intools
# efv 20240403 elimine le finaly car cela efface les erreurs 
import sys
import json
import msal


def helloWorld():
    print("hello from inpython.ingraph")


def getGraphTokenFromCertificate(path):
    # fonctions pour générer un token Graph avec un certificat
    # retourne un objet string json ou un erreur python
    # {
    #      "token_type": "Bearer",
    #      "expires_in": 3599,
    #      "ext_expires_in": 3599,
    #      "access_token": "eyJ0eXAiOiJKV1QiLCJub25jZS..."
    # }
    # c.f. https://github.com/Azure-Samples/ms-identity-python-daemon/tree/master/2-Call-MsGraph-WithCertificate
    #-------------------------------------------------------------------------------------------------------------
    # load config file .json
    # {
    #   "authority": "https://login.microsoftonline.com/infodata.lu",
    #   "tenant_id": "e2a26e34-3...",
    #   "client_id": "15855fc2-...",
    #   "scope": [ "https://graph.microsoft.com/.default" ],
    #   "thumbprint": "9615472D8...",
    #   "private_key_file": "...//9615472D8...//9615472D8....privatekey"
    # }
    result = ''
    try:
        # open & load config
        f_path = open(path)
        config = json.load(f_path)
        # open & load private key
        f_privatekey = open(config['private_key_file'])
        privatekey = f_privatekey.read()
        # connect to the app
        msal_app = msal.ConfidentialClientApplication(
            config["client_id"],
            authority=config["authority"],
            client_credential={"thumbprint": config["thumbprint"],
                               "private_key": privatekey},
            )
        # try to get a token
        result = msal_app.acquire_token_for_client(scopes=config["scope"])
        result = json.dumps(result)
        return result 
    except:
        # toute exception issue de la séquence try arrive ici et est remontée à l'appelant 'uvpython'  
        raise  # pour que l'appelant reçoive l'exception
