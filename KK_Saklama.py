import requests

url = "https://testposws.param.com.tr/out.ws/service_ks.asmx?wsdl"

xml_data =""" <?xml version="1.0" encoding="utf-8"?> <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"> <soap:Body>
<KK_Saklama xmlns="https://turkpos.com.tr/KK_Saklama/">
<G>
<CLIENT_CODE>10738</CLIENT_CODE>
<CLIENT_USERNAME>Test</CLIENT_USERNAME>
<CLIENT_PASSWORD>Test</CLIENT_PASSWORD>
</G>
<GUID>0c13d406-873b-403b-9c09-a5766840d98c</GUID>
<KK_Sahibi>albert</KK_Sahibi>
<KK_No>4546711234567894</KK_No>
<KK_SK_Ay>12</KK_SK_Ay>
<KK_SK_Yil>26</KK_SK_Yil>
<KK_Kart_Adi>Albert</KK_Kart_Adi>
<KK_Islem_ID></KK_Islem_ID>
</KK_Saklama>
</soap:Body>
</soap:Envelope>"""


headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "https://turkpos.com.tr/KK_Saklama"
}
# POST isteği gönder
response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

print("Status Code:", response.status_code)
print("Gelen XML:", response.text)