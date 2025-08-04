import requests
import uuid

url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"

# GUID oluştur
guid = str(uuid.uuid4())

xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <TP_Islem_Odeme_OnProv_Kapa xmlns="https://turkpos.com.tr/">
            <G>
                <CLIENT_CODE>10738</CLIENT_CODE>
                <CLIENT_USERNAME>Test</CLIENT_USERNAME>
                <CLIENT_PASSWORD>Test</CLIENT_PASSWORD>
            </G>
            <GUID>{guid}</GUID>
            <Prov_ID>f7184b1f-c4c2-4d2e-8428-fc6014a00900</Prov_ID>
            <Prov_Tutar>10,00</Prov_Tutar>
            <Siparis_ID></Siparis_ID>
        </TP_Islem_Odeme_OnProv_Kapa>
    </soap:Body>
</soap:Envelope>"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "https://turkpos.com.tr/TP_Islem_Odeme_OnProv_Kapa"
}

try:
    response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)
    response.raise_for_status()
    print("Status Code:", response.status_code)
    print("Gelen XML:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Hata oluştu: {e}")