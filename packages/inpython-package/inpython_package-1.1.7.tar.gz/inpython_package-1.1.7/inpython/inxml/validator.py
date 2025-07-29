# ----------------------------------------------------------------------------
# Valide un xml à l'aide d'un xsdd
# ----------------------------------------------------------------------------
# * Parametres : 
#   Input : 
#       Path du xml
#       Path du xsd
#   Output :
#       1 si xml valide sinon 0
# ----------------------------------------------------------------------------
#    05/04/2024 [JCD] : creation
# ----------------------------------------------------------------------------
import sys
from lxml import etree

def validateXml(xml_path: str, xsd_path: str) -> bool:

    xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)
    result = xmlschema.validate(xml_doc)

    return result

if __name__ == '__main__':
    arguments = sys.argv
    try:
        if len(arguments) == 3:
            xml_filename = arguments[1].replace('\\','/')  # Premier argument
            xsd_filename = arguments[2].replace('\\','/')  # Deuxième argument
            if validateXml(xml_filename, xsd_filename):
                print('1')    
            else:     
                print('0') 
        else:
            raise Exception("Number of argument incorrect")
    except OSError as ose:
        raise Exception(ose)   
    except:
        # toute exception issue de la séquence try arrive ici et est remontée à l'appelant 'uvpython'  
        raise  # pour que l'appelant reçoive l'exception

