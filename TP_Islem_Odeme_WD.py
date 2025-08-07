import requests
url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
xml_data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TP_Islem_Odeme_WD xmlns="https://turkpos.com.tr/">
      <G>
        <CLIENT_CODE>10738</CLIENT_CODE>
        <CLIENT_USERNAME>Test</CLIENT_USERNAME>
        <CLIENT_PASSWORD>Test</CLIENT_PASSWORD>
      </G>
      <Doviz_Kodu>1001</Doviz_Kodu>
      <GUID>0c13d406-873b-403b-9c09-a5766840d98c</GUID>
      <KK_Sahibi>test</KK_Sahibi>
      <KK_No>4546711234567894</KK_No>
      <KK_SK_Ay>12</KK_SK_Ay>
      <KK_SK_Yil>26</KK_SK_Yil>
      <KK_CVC>000</KK_CVC>
      <KK_Sahibi_GSM>5551231212</KK_Sahibi_GSM>
      <Hata_URL>https://dev.param.com.tr/tr</Hata_URL>
      <Basarili_URL>https://dev.param.com.tr/tr</Basarili_URL>
      <Siparis_ID>1</Siparis_ID>
      <Siparis_Aciklama>string</Siparis_Aciklama>
      <Islem_Tutar>100</Islem_Tutar>
      <Toplam_Tutar>100</Toplam_Tutar>
      <Islem_Hash>jTbpMjgcvRKaCZiJsypnKCg8pYo=</Islem_Hash>
      <Islem_Guvenlik_Tip>3</Islem_Guvenlik_Tip>
      <Islem_ID>125</Islem_ID>
      <IPAdr>127.0.0.1</IPAdr>
    </TP_Islem_Odeme_WD>
  </soap:Body>
</soap:Envelope>"""

url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "https://turkpos.com.tr/TP_Islem_Odeme_WD"
}

response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

print("Status Code:", response.status_code)
print("Gelen XML:", response.text)