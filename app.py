from flask import Flask, render_template, request
import requests
import hashlib
import base64
import xml.etree.ElementTree as ET
from datetime import datetime

app = Flask(__name__)

# Sabit Parametreler
CLIENT_CODE = "10738"
GUID = "0c13d406-873b-403b-9c09-a5766840d98c"
CLIENT_USERNAME = "Test"
CLIENT_PASSWORD = "Test"



def calculate_islem_hash(client_code, guid, taksit, islem_tutar, toplam_tutar, siparis_id):
    raw = client_code + guid + taksit + islem_tutar + toplam_tutar + siparis_id
    hashed = hashlib.sha1(raw.encode("ISO-8859-9")).digest()
    return base64.b64encode(hashed).decode("utf-8")



def calculate_3d_hash(client_code, guid, islem_tutar, toplam_tutar, siparis_id, hata_url, basarili_url):
    # 3D işlem için hash formatı farklı olmalı
    raw = client_code + guid + islem_tutar + toplam_tutar + siparis_id + hata_url + basarili_url
    print(f"3D Hash Raw String: {raw}")


    sha1_hash = hashlib.sha1(raw.encode('utf-8')).digest()
    hash_result = base64.b64encode(sha1_hash).decode('utf-8')

    print(f"3D Hash Result: {hash_result}")
    return hash_result


#Kullanıcının girdiği kredi kartı bilgilerini ve ödeme detaylarını alıp,
#TurkPOS (Param POS altyapısı) sistemine bir SOAP isteği (XML formatında) gönderir.
def send_pos_request(client_code, guid, siparis_id, taksit, islem_tutar, toplam_tutar,
                     kk_sahibi, kk_no, kk_sk_ay, kk_sk_yil, kk_cvc):
    islem_hash = calculate_islem_hash(client_code, guid, taksit, islem_tutar, toplam_tutar, siparis_id)

    xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <TP_WMD_UCD xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>{client_code}</CLIENT_CODE>
        <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
        <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
      </G>
      <GUID>{guid}</GUID>
      <KK_Sahibi>{kk_sahibi}</KK_Sahibi>
      <KK_No>{kk_no}</KK_No>
      <KK_SK_Ay>{kk_sk_ay}</KK_SK_Ay>
      <KK_SK_Yil>{kk_sk_yil}</KK_SK_Yil>
      <KK_CVC>{kk_cvc}</KK_CVC>
      <KK_Sahibi_GSM>5551231212</KK_Sahibi_GSM>
      <Hata_URL>https://dev.param.com.tr/en</Hata_URL>
      <Basarili_URL>https://dev.param.com.tr/tr</Basarili_URL>
      <Siparis_ID>{siparis_id}</Siparis_ID>
      <Siparis_Aciklama>a</Siparis_Aciklama>
      <Taksit>{taksit}</Taksit>
      <Islem_Tutar>{islem_tutar}</Islem_Tutar>
      <Toplam_Tutar>{toplam_tutar}</Toplam_Tutar>
      <Islem_Hash>{islem_hash}</Islem_Hash>
      <Islem_Guvenlik_Tip>NS</Islem_Guvenlik_Tip>
      <Islem_ID>654654</Islem_ID>
      <IPAdr>127.0.0.1</IPAdr>
      <Ref_URL>https://dev.param.com.tr/tr</Ref_URL>
      <Data1>a</Data1><Data2>a</Data2><Data3>a</Data3><Data4>a</Data4><Data5>a</Data5>
    </TP_WMD_UCD>
  </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "https://turkpos.com.tr/TP_WMD_UCD"
    }

    url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)
    return response.text, response.status_code


#Daha önce yapılmış bir kredi kartı işlemini iptal etmek ya da iade etmek.
#TurkPOS (ParamPOS) sistemine SOAP formatında XML göndererek bu işlemi başlatıyor.
def send_cancel_or_refund_request(siparis_id, tutar, durum="IADE"):
    xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TP_Islem_Iptal_Iade_Kismi2 xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>{CLIENT_CODE}</CLIENT_CODE>
        <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
        <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
      </G>
      <GUID>{GUID}</GUID>
      <Durum>{durum}</Durum>
      <Siparis_ID>{siparis_id}</Siparis_ID>
      <Tutar>{tutar}</Tutar>
    </TP_Islem_Iptal_Iade_Kismi2>
  </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "https://turkpos.com.tr/TP_Islem_Iptal_Iade_Kismi2"
    }

    url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)
    return response.text, response.status_code


@app.route("/")
def menu():
    return render_template("menu.html")

#@app.route(...), bir web sayfası URL'sini belirli bir Python fonksiyonuna bağlar.
#Bu fonksiyon, kredi kartı ödeme formunu gösterir ve form gönderildikten sonra ödeme işlemini başlatır.
@app.route("/pay", methods=["GET", "POST"])
def pay():
    if request.method == "GET":
        return render_template("Pos_Odeme_Formu.html")

    # Form verileri
    kk_sahibi = request.form.get("kk_sahibi")
    kk_no = request.form.get("kk_no")
    kk_sk_ay = request.form.get("kk_sk_ay")
    kk_sk_yil = request.form.get("kk_sk_yil")
    kk_cvc = request.form.get("kk_cvc")
    taksit = request.form.get("taksit", "1")

    islem_tutar = request.form.get("islem_tutar") or request.form.get("toplam_tutar")
    print("GELEN islem_tutar:", request.form.get("islem_tutar"))

    toplam_tutar = request.form.get("toplam_tutar")
    siparis_id = request.form.get("siparis_id")

    response_text, status_code = send_pos_request(
        CLIENT_CODE, GUID, siparis_id, taksit, islem_tutar, toplam_tutar,
        kk_sahibi, kk_no, kk_sk_ay, kk_sk_yil, kk_cvc
    )

    try:
        root = ET.fromstring(response_text)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'https://turkpos.com.tr/'
        }
        result = root.find(".//ns:TP_WMD_UCDResult", ns)
        sonuc_tag = result.find("ns:Sonuc", ns)
        sonuc = sonuc_tag.text if sonuc_tag is not None else "BULUNAMADI"

        sonuc_str_tag = result.find("ns:Sonuc_Str", ns)
        sonuc_str = sonuc_str_tag.text if sonuc_str_tag is not None else "BULUNAMADI"

        if sonuc == "1":
            return render_template(
                "success.html",
                sonuc_str=sonuc_str,
                islem_id=result.find("ns:Islem_ID", ns).text,
                bank_trans_id=result.find("ns:Bank_Trans_ID", ns).text,
                bank_auth_code=result.find("ns:Bank_AuthCode", ns).text,
                siparis_id=result.find("ns:Siparis_ID", ns).text,
                toplam_tutar=toplam_tutar,
                islem_tutar=islem_tutar,
                ucd_html=result.find("ns:UCD_HTML", ns).text
            )
        else:
            return render_template(
                "error.html",
                sonuc=sonuc,
                sonuc_str=sonuc_str
            )

    except Exception as e:
        return render_template("error.html", sonuc="XML_PARSE_ERROR", sonuc_str=str(e))


@app.route("/iptal-islem", methods=["GET", "POST"])
def iptal_islem():
    if request.method == "GET":
        return render_template("iptal_islem.html")

    siparis_id = request.form.get("siparis_id")
    tutar = request.form.get("tutar")
    durum = request.form.get("durum", "IADE")

    if not siparis_id or not tutar:
        return render_template("iptal_error.html", sonuc="INPUT_ERROR", sonuc_str="Lütfen sipariş ID ve tutar giriniz.")

    response_text, status_code = send_cancel_or_refund_request(siparis_id, tutar, durum)

    try:
        root = ET.fromstring(response_text)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'https://turkpos.com.tr/'
        }
        result = root.find(".//ns:TP_Islem_Iptal_Iade_Kismi2Result", ns)
        sonuc = result.find("ns:Sonuc", ns).text
        sonuc_str = result.find("ns:Sonuc_Str", ns).text
        bank_auth_code = result.find("ns:BankaAuthCode", ns).text if result.find("ns:BankaAuthCode",
                                                                                 ns) is not None else ""
        bank_trans_id = result.find("ns:BankaTransID", ns).text if result.find("ns:BankaTransID",
                                                                               ns) is not None else ""
        bank_host_ref = result.find("ns:HostRefNum", ns).text if result.find("ns:HostRefNum", ns) is not None else ""
        bank_extra = result.find("ns:EkBilgi", ns).text if result.find("ns:EkBilgi", ns) is not None else ""

        if sonuc == "1":
            return render_template(
                "iptal_success.html",
                sonuc=sonuc,
                sonuc_str=sonuc_str,
                bank_auth_code=bank_auth_code,
                bank_trans_id=bank_trans_id,
                bank_host_ref=bank_host_ref,
                bank_extra=bank_extra,
                siparis_id=siparis_id,
                tutar=tutar,
                durum=durum
            )
        else:
            return render_template(
                "iptal_error.html",
                sonuc=sonuc,
                sonuc_str=sonuc_str
            )

    except Exception as e:
        return render_template("iptal_error.html", sonuc="XML_PARSE_ERROR", sonuc_str=str(e))


@app.route("/dekont-gonder", methods=["GET", "POST"])
def dekont_sorgula():
    if request.method == "GET":
        return render_template("dekont_form.html")

    islem_id = request.form.get("islem_id", "").strip()
    e_posta = request.form.get("e_posta", "").strip()

    xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TP_Islem_Dekont_Gonder xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>{CLIENT_CODE}</CLIENT_CODE>
        <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
        <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
      </G>
      <GUID>{GUID}</GUID>
      <Dekont_ID>{islem_id}</Dekont_ID>
      <E_Posta>{e_posta}</E_Posta>
    </TP_Islem_Dekont_Gonder>
  </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "https://turkpos.com.tr/TP_Islem_Dekont_Gonder"
    }

    url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

    try:
        root = ET.fromstring(response.text)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'https://turkpos.com.tr/'
        }

        result = root.find(".//ns:TP_Islem_Dekont_GonderResult", ns)
        sonuc = result.find("ns:Sonuc", ns).text
        sonuc_str = result.find("ns:Sonuc_Str", ns).text

        if sonuc == "1":
            return render_template("dekont_success.html", sonuc_str=sonuc_str)
        else:
            return render_template("dekont_error.html", sonuc=sonuc, sonuc_str=sonuc_str)

    except Exception as e:
        return f"<h3>XML Parse Hatası:</h3><pre>{str(e)}</pre><pre>{response.text}</pre>"


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.message import EmailMessage

from flask import send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@app.route('/dekont-indir', methods=['POST'])
def dekont_indir():
    islem_id = request.form.get('islem_id')
    siparis_id = request.form.get('siparis_id')
    islem_tutar = request.form.get('islem_tutar')
    tarih = datetime.now().strftime("%d.%m.%Y")

    # PDF içeriği
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 100, "Ödeme Dekontu")
    c.drawString(100, height - 130, f"İşlem ID     : {islem_id}")
    c.drawString(100, height - 150, f"Sipariş ID   : {siparis_id}")
    c.drawString(100, height - 170, f"Tutar        : {islem_tutar} TL")
    c.drawString(100, height - 190, f"Tarih        : {tarih}")
    c.drawString(100, height - 210, "Durum        : Başarılı")

    c.save()
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name=f"dekont_{islem_id}.pdf",
                     mimetype='application/pdf')


def send_email_with_pdf(to_email, pdf_path):
    from_email = "aleynaakilic61@gmail.com"
    password = ""

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Ödeme Dekontunuz"

    body = MIMEText("Merhaba,\nÖdemenize ait dekont ektedir.", 'plain')
    msg.attach(body)

    with open(pdf_path, "rb") as f:
        pdf = MIMEApplication(f.read(), _subtype="pdf")
        pdf.add_header('Content-Disposition', 'attachment', filename="dekont.pdf")
        msg.attach(pdf)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()


@app.route('/dekont-success', methods=['POST'])
def dekont_success():
    islem_id = request.form.get('islem_id')
    siparis_id = request.form.get('siparis_id')
    islem_tutar = request.form.get('islem_tutar')
    tarih = datetime.now().strftime("%d.%m.%Y")

    print(f"islem_id: {islem_id}, siparis_id: {siparis_id}, islem_tutar: {islem_tutar}")

    return render_template("dekont_success.html",
                           islem_id=islem_id,
                           siparis_id=siparis_id,
                           islem_tutar=islem_tutar,
                           tarih=tarih)


@app.route("/odeme-3d", methods=["GET", "POST"])
def odeme_3d():
    if request.method == "GET":
        return render_template("Pos_3D_Formu.html")

    kk_sahibi = request.form.get("kk_sahibi")
    kk_no = request.form.get("kk_no")
    kk_sk_ay = request.form.get("kk_sk_ay")
    kk_sk_yil = request.form.get("kk_sk_yil")
    kk_cvc = request.form.get("kk_cvc")
    taksit = request.form.get("taksit", "1")
    islem_tutar = request.form.get("islem_tutar")
    toplam_tutar = request.form.get("toplam_tutar")
    siparis_id = request.form.get("siparis_id")


    basarili_url = request.form.get("Basarili_URL") or "http://localhost:5000/3d-sonuc"
    hata_url = request.form.get("Hata_URL") or "http://localhost:5000/3d-hata"


    islem_hash = calculate_3d_hash(
        CLIENT_CODE,
        GUID,
        islem_tutar,
        toplam_tutar,
        siparis_id,
        hata_url,
        basarili_url
    )

    print("Hesaplanan 3D Hash:", islem_hash)

    xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TP_Islem_Odeme_OnProv_WMD xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>{CLIENT_CODE}</CLIENT_CODE>
        <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
        <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
      </G>
      <GUID>{GUID}</GUID>
      <KK_Sahibi>{kk_sahibi}</KK_Sahibi>
      <KK_No>{kk_no}</KK_No>
      <KK_SK_Ay>{kk_sk_ay}</KK_SK_Ay>
      <KK_SK_Yil>{kk_sk_yil}</KK_SK_Yil>
      <KK_CVC>{kk_cvc}</KK_CVC>
      <KK_Sahibi_GSM>5551231212</KK_Sahibi_GSM>
      <Hata_URL>{hata_url}</Hata_URL>
      <Basarili_URL>{basarili_url}</Basarili_URL>
      <Siparis_ID>{siparis_id}</Siparis_ID>
      <Siparis_Aciklama>3D Test</Siparis_Aciklama>
      <Taksit>{taksit}</Taksit>
      <Islem_Tutar>{islem_tutar}</Islem_Tutar>
      <Toplam_Tutar>{toplam_tutar}</Toplam_Tutar>
      <Islem_Hash>{islem_hash}</Islem_Hash>
      <Islem_Guvenlik_Tip>3D</Islem_Guvenlik_Tip>
      <IPAdr>127.0.0.1</IPAdr>
      <Ref_URL>http://localhost:5000</Ref_URL>
      <Data1>a</Data1><Data2>a</Data2><Data3>a</Data3><Data4>a</Data4><Data5>a</Data5>
    </TP_Islem_Odeme_OnProv_WMD>
  </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "https://turkpos.com.tr/TP_Islem_Odeme_OnProv_WMD"
    }

    url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

    try:
        root = ET.fromstring(response.text)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'https://turkpos.com.tr/'
        }

        result = root.find(".//ns:TP_Islem_Odeme_OnProv_WMDResult", ns)
        sonuc_tag = result.find("ns:Sonuc", ns)
        sonuc = sonuc_tag.text if sonuc_tag is not None else "BULUNAMADI"

        sonuc_str_tag = result.find("ns:Sonuc_Str", ns)
        sonuc_str = sonuc_str_tag.text if sonuc_str_tag is not None else "BULUNAMADI"

        ucd_html_tag = result.find("ns:UCD_HTML", ns)
        ucd_html = ucd_html_tag.text if ucd_html_tag is not None else ""

        if int(sonuc) > 0:
            print("✔️ 3D işlemi başlatılabilir")
            print("UCD HTML:", ucd_html[:100] + "..." if len(ucd_html) > 100 else ucd_html)
            return render_template("3D_success.html", ucd_html=ucd_html)
        else:
            print("❌ İşlem başarısız:", sonuc_str)
            return render_template("error.html", sonuc=sonuc, sonuc_str=sonuc_str)

    except Exception as e:
        return f"<h3>XML Parse Hatası</h3><pre>{str(e)}</pre><pre>{response.text}</pre>"


@app.route("/3d-sonuc", methods=["POST"])
def sonuc_3d():

    md = request.form.get("md", "")
    mdStatus = request.form.get("mdStatus", "")
    orderId = request.form.get("orderId", "")
    islemGUID = request.form.get("islemGUID", "")
    islemHash = request.form.get("islemHash", "")
    transaction_amount = request.form.get("transactionAmount", "")

    islem_tutar = transaction_amount.replace(".", "").replace(",", ".") if transaction_amount else ""
    toplam_tutar = islem_tutar  # Aynı değer olacak
    hata_url = request.form.get("hata_url", "")
    basarili_url = request.form.get("basarili_url", "")

    print("=== 3D Sonuç Parametreleri ===")
    print(f"mdStatus: {mdStatus}")
    print(f"orderId: {orderId}")
    print(f"islemGUID: {islemGUID}")
    print(f"transaction_amount: {transaction_amount}")
    print(f"islem_tutar: {islem_tutar}")
    print(f"md: {md}")
    print(f"Gelen Hash: {islemHash}")
    print(f"Gelen tüm form data: {dict(request.form)}")


    current_guid = GUID

    print(f"3D başlatmada kullanılan GUID: {GUID}")
    print(f"Bankadan gelen GUID: {islemGUID}")
    print(f"Finalize için kullanılacak GUID: {current_guid}")
    print(f"GUID uzunluğu: {len(current_guid)}")


    if mdStatus == "1":
        print("✅ 3D onayı başarılı, ödeme finalize ediliyor...")



        xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TP_WMD_Pay xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>{CLIENT_CODE}</CLIENT_CODE>
        <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
        <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
      </G>
      <GUID>{current_guid}</GUID>
      <UCD_MD>{md}</UCD_MD>
      <Islem_GUID>{current_guid}</Islem_GUID>
      <Siparis_ID>{orderId}</Siparis_ID>
    </TP_WMD_Pay>
  </soap:Body>
</soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "https://turkpos.com.tr/TP_WMD_Pay"
        }

        url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"

        print("Finalize XML:", xml_data)
        response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")


        if not response.text.strip():
            return render_template("error.html",
                                   sonuc="EMPTY_RESPONSE",
                                   sonuc_str="Servisten boş yanıt geldi",
                                   mdStatus=mdStatus)

        try:
            root = ET.fromstring(response.text)
            ns = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'ns': 'https://turkpos.com.tr/'
            }


            result = root.find(".//ns:TP_WMD_PayResult", ns)

            if result is None:
                return f"<h3>Result Tag Bulunamadı</h3><pre>{response.text}</pre>"


            sonuc_tag = result.find("ns:Sonuc", ns)
            sonuc = sonuc_tag.text if sonuc_tag is not None else "0"

            sonuc_str_tag = result.find("ns:Sonuc_Ack", ns)
            sonuc_str = sonuc_str_tag.text if sonuc_str_tag is not None else "Bilinmeyen hata"


            auth_code_tag = result.find("ns:Bank_AuthCode", ns)
            auth_code = auth_code_tag.text if auth_code_tag is not None else "N/A"

            trans_id_tag = result.find("ns:Bank_Trans_ID", ns)
            trans_id = trans_id_tag.text if trans_id_tag is not None else "N/A"

            print(f"Sonuc: {sonuc}, Sonuc_Str: {sonuc_str}")

            if sonuc == "1":
                return render_template("success.html",
                                       sonuc_str=sonuc_str,
                                       bank_auth_code=auth_code,
                                       bank_trans_id=trans_id,
                                       siparis_id=orderId,
                                       islem_tutar=islem_tutar,
                                       toplam_tutar=toplam_tutar)
            else:
                return render_template("error.html",
                                       sonuc="PAYMENT_FAILED",
                                       sonuc_str=sonuc_str,
                                       mdStatus=mdStatus)

        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            return f"<h3>XML Parse Hatası</h3><pre>{str(e)}</pre><pre>{response.text}</pre>"
        except Exception as e:
            print(f"General Error: {e}")
            return f"<h3>İşlem Hatası</h3><pre>{str(e)}</pre><pre>{response.text}</pre>"

    else:
        return render_template("error.html",
                               sonuc="3D_FAILED",
                               sonuc_str=f"3D doğrulama başarısız (mdStatus: {mdStatus})",
                               mdStatus=mdStatus)

@app.route("/3d-hata", methods=["GET", "POST"])
def hata_3d():
    return render_template("error.html", sonuc="3D_RED", sonuc_str="3D işlem başarısız veya kullanıcı iptal etti.")



def calculate_finalize_hash(islem_guid, md, md_status, order_id, store_key):
    """3D işlem finalize için hash hesaplar - Param POS formatına göre"""
    import hashlib
    import base64


    raw = islem_guid + md + md_status + order_id + store_key.lower()
    print(f"Finalize Hash Raw String: {raw}")


    sha1_hash = hashlib.sha1(raw.encode('utf-8')).digest()
    hash_result = base64.b64encode(sha1_hash).decode('utf-8')

    print(f"Finalize Hash Result: {hash_result}")
    return hash_result


@app.route("/provizyon-kapat", methods=["GET", "POST"])
def provizyon_kapat():
    if request.method == "GET":
        return render_template("provizyon_kapat.html")


    prov_id = request.form.get("prov_id", "").strip()
    guid = request.form.get("guid", "").strip()
    tutar = request.form.get("tutar", "").strip().replace(".", ",")  # Noktayı virgüle çevir


    if not guid:
        return render_template("provizyon_error.html", sonuc_str="❌ Hata: GUID alanı boş olamaz!", prov_id=prov_id)

    if not prov_id and not request.form.get("siparis_id", "").strip():
        return render_template("provizyon_error.html",
                               sonuc_str="❌ Hata: Prov_ID veya Siparis_ID alanlarından biri doldurulmalıdır!",
                               prov_id=prov_id)

    siparis_id = request.form.get("siparis_id", "145339").strip()  # Formdan da alınabilir


    xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TP_Islem_Odeme_OnProv_Kapa xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>{CLIENT_CODE}</CLIENT_CODE>
        <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
        <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
      </G>
      <GUID>{guid}</GUID>
      <Prov_ID>{prov_id}</Prov_ID>
      <Prov_Tutar>{tutar}</Prov_Tutar>
      <Siparis_ID>{siparis_id}</Siparis_ID>
    </TP_Islem_Odeme_OnProv_Kapa>
  </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "https://turkpos.com.tr/TP_Islem_Odeme_OnProv_Kapa"
    }

    url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

    try:
        root = ET.fromstring(response.text)
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "ns": "https://turkpos.com.tr/"
        }

        result = root.find(".//ns:TP_Islem_Odeme_OnProv_KapaResult", ns)
        sonuc = result.find("ns:Sonuc", ns).text
        sonuc_str = result.find("ns:Sonuc_Str", ns).text
        dekont_id = result.find("ns:Dekont_ID", ns)
        prov_id_resp = result.find("ns:Prov_ID", ns)

        dekont_id = dekont_id.text if dekont_id is not None else ""
        prov_id_resp = prov_id_resp.text if prov_id_resp is not None else ""

        if sonuc == "1":
            return render_template("provizyon_success.html",
                           sonuc_str=sonuc_str,
                           dekont_id=dekont_id,
                           prov_id=prov_id_resp,
                           siparis_id=siparis_id,
                           tutar=tutar,
                           sonuc=sonuc,
                           bank_auth_code="",
                           bank_trans_id="",
                           bank_host_ref="",
                           bank_extra="")
        else:
            return render_template("provizyon_error.html",
                                   sonuc_str=sonuc_str,
                                   prov_id=prov_id_resp)

    except Exception as e:
        return f"<h3>Hata:</h3><pre>{str(e)}</pre><pre>{response.text}</pre>"









from flask import Flask, render_template, request, flash, redirect, url_for
import requests
import xml.etree.ElementTree as ET
import logging
app.secret_key = "computerengineering"


BASE_URL = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
@app.route('/')
def index():
    return render_template('menu.html')

# Form sayfasını açar
@app.route('/islem-sorgula', methods=['GET'])
def islem_sorgula_form():
    return render_template('islem_sorgulama.html')


import xml.etree.ElementTree as ET
import requests
from flask import request, render_template, flash


@app.route('/islem-sorgula', methods=['POST'])
def islem_sorgula():
    guid = request.form.get('guid', '').strip()
    dekont_id = request.form.get('dekont_id', '').strip()
    siparis_id = request.form.get('siparis_id', '').strip()
    islem_id = request.form.get('islem_id', '').strip()

    if not any([guid, dekont_id, siparis_id, islem_id]):
        flash("En az bir arama kriteri giriniz", "error")
        return render_template('islem_sorgulama.html')

    # XML SOAP isteği
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TP_Islem_Sorgulama4 xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>10738</CLIENT_CODE>
        <CLIENT_USERNAME>Test</CLIENT_USERNAME>
        <CLIENT_PASSWORD>Test</CLIENT_PASSWORD>
      </G>
      <GUID>{guid}</GUID>
      <Dekont_ID>{dekont_id}</Dekont_ID>
      <Siparis_ID>{siparis_id}</Siparis_ID>
      <Islem_ID>{islem_id}</Islem_ID>
    </TP_Islem_Sorgulama4>
  </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "https://turkpos.com.tr/TP_Islem_Sorgulama4"
    }

    try:
        response = requests.post(
            "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx",
            data=xml.encode("utf-8"),
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            flash("SOAP bağlantı hatası", "error")
            return render_template('islem_sorgulama.html')

        # Debug için XML yanıtını logla
        print("SOAP Response:")
        print(response.text)
        print("-" * 50)

        # XML yanıtını parse et
        bilgiler = parse_soap_response(response.text)

        if bilgiler is None:
            flash("XML yanıtı işlenirken hata oluştu", "error")
            return render_template('islem_sorgulama.html')

        return render_template('sonuc.html', bilgiler=bilgiler)

    except Exception as e:
        flash(f"Hata oluştu: {str(e)}", "error")
        return render_template('islem_sorgulama.html')


def parse_soap_response(xml_response):
    """SOAP XML yanıtını parse eder ve bilgileri döndürür"""
    try:
        print("XML Response içeriği:")
        print(xml_response)
        print("-" * 50)

        root = ET.fromstring(xml_response)
        print("XML Root tag:", root.tag)

        # Tüm elementleri listele
        print("Tüm XML elementleri:")
        for elem in root.iter():
            if elem.text and elem.text.strip():
                print(f"Tag: {elem.tag}, Text: {elem.text.strip()}")
        print("-" * 50)

        # SOAP Body içindeki response'u bul
        # Farklı namespace kombinasyonlarını dene
        possible_paths = [
            './/TP_Islem_Sorgulama4Response',
            './/TP_Islem_Sorgulama4Result',
            './/{https://turkpos.com.tr/}TP_Islem_Sorgulama4Response',
            './/{https://turkpos.com.tr/}TP_Islem_Sorgulama4Result',
            './/Response',
            './/Result'
        ]

        response_element = None
        for path in possible_paths:
            response_element = root.find(path)
            if response_element is not None:
                print(f"Response element bulundu: {path}")
                break

        if response_element is None:
            print("Response element bulunamadı!")
            # Body içindeki ilk elementi al
            body = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')
            if body is not None:
                response_element = body[0] if len(body) > 0 else None
                print(
                    f"Body'nin ilk elementi alındı: {response_element.tag if response_element is not None else 'None'}")

        if response_element is None:
            return None

        # Bilgileri çıkar
        bilgiler = {}

        # Response element içindeki tüm child elementleri kontrol et
        print("Response element içindeki elementler:")
        for child in response_element:
            print(f"Child tag: {child.tag}, Text: {child.text}")

        # XML yapısına göre field'ları map et
        field_mapping = {
            'Durum': ['Durum', 'Status', 'Sonuc_Kodu'],
            'Odeme_Sonuc_Aciklama': ['Odeme_Sonuc_Aciklama', 'Aciklama', 'Description', 'Sonuc_Ack'],
            'Tarih': ['Tarih', 'Islem_Tarih', 'Date', 'Transaction_Date'],
            'Dekont_ID': ['Dekont_ID', 'DekonID', 'Dekont_No'],
            'Siparis_ID': ['Siparis_ID', 'SiparisID', 'Order_ID'],
            'Islem_Tipi': ['Islem_Tipi', 'IslemTipi', 'Transaction_Type'],
            'KK_No': ['KK_No', 'Kart_No', 'CardNo', 'Card_Number'],
            'Toplam_Tutar': ['Toplam_Tutar', 'Tutar', 'Amount', 'Total_Amount'],
            'Komisyon_Tutar': ['Komisyon_Tutar', 'Komisyon', 'Commission'],
            'Taksit': ['Taksit', 'TaksitSayisi', 'Installment'],
            'Odeme_Yapan_GSM': ['Odeme_Yapan_GSM', 'GSM', 'Telefon', 'Phone'],
            'Islem_GUID': ['Islem_GUID', 'GUID', 'Transaction_GUID']
        }

        for key, possible_fields in field_mapping.items():
            value = None
            for field in possible_fields:
                # Önce direkt arama
                element = response_element.find(f'.//{field}')
                if element is None:
                    # Büyük/küçük harf duyarsız arama
                    for elem in response_element.iter():
                        if elem.tag.lower().endswith(field.lower()):
                            element = elem
                            break

                if element is not None and element.text:
                    value = element.text.strip()
                    print(f"{key} için {field} bulundu: {value}")
                    break

            bilgiler[key] = value or 'Bilgi bulunamadı'

        return bilgiler

    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return None
    except Exception as e:
        print(f"Parse Error: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.route("/kart-ekle", methods=["GET", "POST"])
def kart_ekle():
    if request.method == "GET":
        return render_template("kart_ekle_form.html")

    # Formdan gelen veriler
    kk_sahibi = request.form.get("kk_sahibi")
    kk_no = request.form.get("kk_no")
    kk_sk_ay = request.form.get("kk_sk_ay")
    kk_sk_yil = request.form.get("kk_sk_yil")
    kk_kart_adi = request.form.get("kk_kart_adi", "")
    kk_islem_id = request.form.get("kk_islem_id", "")

    xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <KS_Kart_Ekle xmlns="https://turkpara.com.tr/">
          <G>
            <CLIENT_CODE>10738</CLIENT_CODE>
            <CLIENT_USERNAME>{CLIENT_USERNAME}</CLIENT_USERNAME>
            <CLIENT_PASSWORD>{CLIENT_PASSWORD}</CLIENT_PASSWORD>
          </G>
          <GUID>{GUID}</GUID>
          <KK_Sahibi>{kk_sahibi}</KK_Sahibi>
          <KK_No>{kk_no}</KK_No>
          <KK_SK_Ay>{kk_sk_ay}</KK_SK_Ay>
          <KK_SK_Yil>{kk_sk_yil}</KK_SK_Yil>
          <KK_Kart_Adi>{kk_kart_adi}</KK_Kart_Adi>
          <KK_Islem_ID>{kk_islem_id}</KK_Islem_ID>
        </KS_Kart_Ekle>
      </soap:Body>
    </soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "https://turkpara.com.tr/KS_Kart_Ekle"
    }

    url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

    try:
        root = ET.fromstring(response.text)
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'ns': 'https://turkpara.com.tr/'
        }

        result = root.find('.//ns:KS_Kart_EkleResult', ns)
        if result is None:
            return f"<h3>Hata: API yanıtında 'KS_Kart_EkleResult' bulunamadı.</h3><pre>{response.text}</pre>"

        sonuc = result.find('ns:Sonuc', ns)
        sonuc_str = result.find('ns:Sonuc_Str', ns)

        if sonuc is None or sonuc_str is None:
            return f"<h3>Hata: API yanıtında 'Sonuc' veya 'Sonuc_Str' bulunamadı.</h3><pre>{response.text}</pre>"

        print(f"API sonucu: {sonuc.text}, Mesaj: {sonuc_str.text}")  # Logla


    except Exception as e:
        return f"<h3>Hata oluştu:</h3><pre>{str(e)}</pre><pre>{response.text}</pre>"

if __name__ == '__main__':
    app.run(debug=True)













