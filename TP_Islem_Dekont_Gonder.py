import requests

url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"

xml_data ="""<?xml version="1.0" encoding="utf-8"?> <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"> <soap:Body>
<TP_Islem_Dekont_Gonder xmlns="https://turkpos.com.tr/">
<G>
<CLIENT_CODE>10738</CLIENT_CODE>
<CLIENT_USERNAME>Test</CLIENT_USERNAME>
<CLIENT_PASSWORD>Test</CLIENT_PASSWORD>
</G>
<GUID>0c13d406-873b-403b-9c09-a5766840d98c</GUID>
<Dekont_ID>3000159363</Dekont_ID>
<E_Posta></E_Posta>
</TP_Islem_Dekont_Gonder>
</soap:Body>
</soap:Envelope>"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "https://turkpos.com.tr/TP_Islem_Dekont_Gonder"
}
# POST isteği gönder
response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

print("Status Code:", response.status_code)
print("Gelen XML:", response.text)