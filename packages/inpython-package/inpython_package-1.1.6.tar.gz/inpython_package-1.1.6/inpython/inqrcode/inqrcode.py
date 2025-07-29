"""
script/fonction encode(ErrorCorrection: str = "Q", Valeur: str ) -> str: 
qui execute python qrcode https://pypi.org/project/qrcode/ pour encoder la valeur 
et retourner un tableau de 1010110

Usage :
  - Python ...\inqrcode.py codeErr "Valeur" 
     Dans ce cas, la fonction sort sur un 'print(result)'
  - from inpython.inqrcode import inqrcode.py
    qrc = inqrcode.encode(codeErr, valeur) 

"""
import qrcode
import sys

error_correction = {
    'L': qrcode.ERROR_CORRECT_L,
    'M': qrcode.ERROR_CORRECT_M,
    'Q': qrcode.ERROR_CORRECT_Q,
    'H': qrcode.ERROR_CORRECT_H,
}

def encode(codeErr: str = "M", data: str = "") -> str:
    """fonction qui encode la valeur pour en faire un qrcode avec le module POST 

     Args:
         codeErr (str, optional): Error Correcton level. Defaults to "M". 
               The error_correction parameter controls the error correction used for the QR Code. The following four constants are made available on the qrcode package:
               ERROR_CORRECT_L : About 7% or less errors can be corrected.
               ERROR_CORRECT_M (default) : About 15% or less errors can be corrected.
               ERROR_CORRECT_Q : About 25% or less errors can be corrected.
               ERROR_CORRECT_H. : About 30% or less errors can be corrected
         data (str, optional): _description_. Defaults to "".

     Returns:
         str: sequence de 01010101 emballé sous le format : qrcode<data>\\n-----\\n01010...\\n-----\\n. Separator 'lineFeed' (char(10))
              Exemple : 
               qrcode<content_of_arg'data'>
               ----- 
               111111101111101111111
               100000100011101000001
               -----
               
    """
    qr = qrcode.QRCode(error_correction=error_correction[codeErr])
    qr.add_data(data)
    qr.border = 0
    qrbool = qr.get_matrix()
    out = sys.stdout 
    result = 'qrcode<' + data + '>\n' + '-----\n'
    for l in qrbool:
        s = ''.join(['1' if x else '0' for x in l])
        result += s + '\n'
    result += '-----\n'
    return result 

if __name__ == "__main__":
    print(encode(sys.argv[1],sys.argv[2]))
 