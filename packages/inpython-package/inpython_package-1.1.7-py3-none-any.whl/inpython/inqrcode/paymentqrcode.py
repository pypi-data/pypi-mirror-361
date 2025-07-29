import requests
import qrcode
from dotenv import load_dotenv
import os
from PIL import Image 

load_dotenv()

ADYEN_API_KEY = os.getenv("ADYEN_API_KEY")
MERCHANT_ACCOUNT = os.getenv("MERCHANT_ACCOUNT")
URL = os.getenv("ADYEN_API_URL")

HEADERS = {
    "X-API-Key": ADYEN_API_KEY,
    "Content-Type": "application/json"
}

def create_payment_link_adyen(amount_cents: int, currency: str, reference: str, mode: str = 1, logo_path: str = None, env_path: str = None, qrcode_path: str = None ) -> str:
    """Crée un lien de paiement via l'API Adyen. Si mode=2, génère aussi un QR code (avec logo si fourni). Si env_path est fourni, charge les variables d'environnement depuis ce fichier."""
    if env_path and os.path.exists(env_path):
        from dotenv import dotenv_values
        env_vars = dotenv_values(env_path)
        adyen_api_key = env_vars.get("ADYEN_API_KEY")
        merchant_account = env_vars.get("MERCHANT_ACCOUNT")
        url = env_vars.get("ADYEN_API_URL")
    else:
        adyen_api_key = ADYEN_API_KEY
        merchant_account = MERCHANT_ACCOUNT
        url = URL
    headers = {
        "X-API-Key": adyen_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "amount": {
            "value": amount_cents,
            "currency": currency
        },
        "reference": reference,
        "merchantAccount": merchant_account
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        response.raise_for_status() 
    data = response.json()
    payment_url = data["url"]
    if mode == 2:
        qr_path = generate_qr_code(payment_url, reference, logo_path,qrcode_path)
        return qr_path
    return payment_url

def generate_qr_code(url: str, reference: str, logo_path: str = None, qrcode_path: str = None) -> None:
    """Génère un QR code dans le dossier ./qrcode/ (au même niveau que paymentqrcode.py), avec logo si fourni. Crée/écrase un fichier qrcode_logs.txt pour le diagnostic."""
    import traceback
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "qrcode")

    os.makedirs(output_dir, exist_ok=True)
    print("qrcode_path : ",qrcode_path)
    if qrcode_path:
        filename = os.path.join(qrcode_path, f"{reference}.jpg")
        log_file = os.path.join(qrcode_path, "qrcode_debug.log")
    else:
        filename = os.path.join(output_dir, f"{reference}.jpg")
        log_file = os.path.join(output_dir, "qrcode_debug.log")

    # Supprime le fichier s’il existe
    if os.path.exists(log_file):
        os.remove(log_file)

    log_lines = []
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        log_lines.append(f"QR code généré pour l'URL: {url}\n")
        if logo_path:
            log_lines.append(f"Chemin du logo fourni: {logo_path}\n")
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path)
                    log_lines.append(f"Logo ouvert avec succès. Mode: {logo.mode}, Taille: {logo.size}\n")
                    qr_width, qr_height = img_qr.size
                    logo_size = int(qr_width * 0.2)
                    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                    log_lines.append(f"Logo redimensionné à: {logo.size}\n")
                    pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                    img_qr.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)
                    log_lines.append(f"Logo collé au centre du QR code.\n")
                except Exception as e:
                    log_lines.append(f"Erreur lors de l'ouverture ou du collage du logo: {e}\n{traceback.format_exc()}\n")
            else:
                log_lines.append(f"Logo non trouvé : {logo_path}, QR code généré sans logo.\n")
        else:
            log_lines.append("Aucun chemin de logo fourni, QR code généré sans logo.\n")
        img_qr.save(filename, format="JPEG")
        log_lines.append(f"QR code enregistré : {filename}\n")
    except Exception as e:
        log_lines.append(f"Erreur générale lors de la génération du QR code: {e}\n{traceback.format_exc()}\n")
    # Toujours écrire le log, même si une exception a eu lieu
    with open(log_file, 'w') as f:
        f.writelines(log_lines)
    return filename


def clean(s):
    return s.strip('"').strip("'")

if __name__ == "__main__":
    import sys
    try:
        # Utilisation : python paymentqrcode.py <mode> <montant> <devise> <reference> [chemin_logo] [chemin_env]
        mode = int(clean(sys.argv[1]))
        amount = int(clean(sys.argv[2]))
        currency = sys.argv[3]
        reference = sys.argv[4]
        logo_path = sys.argv[5] if len(sys.argv) > 5 else ''
        env_path = sys.argv[6] if len(sys.argv) > 6 else ''
        qrcode_path = sys.argv[7] if len(sys.argv) > 7 else ''
        result = create_payment_link_adyen(amount, currency, reference, mode, logo_path, env_path,qrcode_path)
        print(result)
    except Exception as e:
        print("Erreur :", e)
