#--------------------------------------------------------
# Manipulates a Json web token
# 
#--------------------------------------------------------
# 22/08/2024 (JCD) : Creation fonction generateJwtClientAssertion
#--------------------------------------------------------
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import jwt
import datetime
import sys
import getopt

# Generates a jwt client assertion from a private key
def generateJwtClientAssertion(mode,path_certificate,private_key,client_id,audience,expirationTime=10):
    """ Return jwt token assertion
    
    Parameters
    ------------
        mode:int
           = 1 : Private key
           = 2 : Private password
        path_certificate: string
            Path crt/cer file if mode = 1
            Path pfx file if mode = 2
        private_key: byte
            Path key file file if mode = 1
            Private password if mode = 2
        client_id: string
        audience: string
        expirationTime: string, Optional
            in minutes. Default to 10 minutes
    """
    try:
        if mode != "1" and mode != "2" :
            raise Exception("Unmanaged mode")

        if not expirationTime:  
            expirationTime = 10
        else:    
            expirationTime = int(expirationTime)
            
        # Load the public certificate
        with open(path_certificate, "rb") as cert_file:
            certificate_data = cert_file.read()
            
        # Load the private key
        if mode == "1":
            with open(private_key, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
        else:
            private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
                certificate_data, private_key.encode(), backend=default_backend()
            ) 
        
        now = datetime.datetime.now(datetime.timezone.utc)
        # Define the JWT claims
        claims = {
            "iss": client_id,        # The issuer, typically your client ID
            "sub": client_id,        # The subject, typically your client ID
            "aud": audience,   # The audience, typically the token endpoint URL
            "exp": now + datetime.timedelta(expirationTime),  # Expiration time
            "jti": "unique-identifier",     # JWT ID, a unique identifier for the JWT
        }

        # Create the JWT (client assertion)
        if mode == 1:
            client_assertion = jwt.encode(
                claims,
                private_key,
                algorithm="RS256",
                headers={"x5c": [certificate_data.decode("utf-8").replace("\n", "")]}
            )
        else:
            client_assertion = jwt.encode(
            claims, private_key, algorithm="RS256", headers={"alg": "RS256","typ": "JWT"}
        )    
        return client_assertion
    except:
        raise  # so that the caller receives the exception

def main(argv):
    #mode = "1"
    #private_key = "C:\\TRF\\cleanup\\Cleanup1_private.key"
    #path_certificate = "C:\\TRF\\cleanup\\Cleanup1_request.crt"
    #client_id = "self_service_chaman_109660_shr5ppy83v"
    
    #mode = "2"
    #path_certificate = "/tmp/jcd/CermiaRest.pfx"
    #private_key = "2024infodd1648!"  # Use b'' for an empty password
    #client_id = "self_service_chaman_108306_safnfiag3h"
    #audience = "https://services.socialsecurity.be/REST/oauth/v5/token"
    mode = ''
    private_key = ''
    path_certificate = ''
    client_id = ''
    audience = ''
    expirationTime = None
    try:
        opts, args = getopt.getopt(argv, "m:k:x:c:a:e:", ["mode=", "private_key=", "path_certificate=", "client_id=", "audience=", "expirationTime="])
    except getopt.GetoptError:
        print('script.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-k", "--private_key"):
            private_key = arg
        elif opt in ("-x", "--path_certificate"):
            path_certificate = arg
        elif opt in ("-c", "--client_id"):
            client_id = arg    
        elif opt in ("-a", "--audience"):
            audience = arg    
        elif opt in ("-e", "--expirationTime"):
            if arg != "":
                expirationTime = arg        
            
    result = generateJwtClientAssertion(mode,path_certificate,private_key,client_id,audience,expirationTime)
    print(result)

if __name__ == "__main__":
    main(sys.argv[1:])
    

