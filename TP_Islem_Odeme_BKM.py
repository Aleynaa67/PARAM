import requests
url = "https://testposws.param.com.tr/turkpos.ws/service_turkpos_prod.asmx"
xml_data ="""<?xml version="1.0" encoding="utf-8"?> <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"> <soap:Body>
<TP_Islem_Odeme_BKM xmlns="https://turkpos.com.tr/">
<G>
<CLIENT_CODE>10738</CLIENT_CODE>
<CLIENT_USERNAME>Test</CLIENT_USERNAME>
<CLIENT_PASSWORD>Test</CLIENT_PASSWORD>
</G>
<GUID>;0c13d406-873b-403b-9c09-a5766840d98c</GUID>
<Customer_Info></Customer_Info>
<Customer_GSM>5551231212</Customer_GSM>
<Error_URL>http://localhost:62361/turkpos.api/Sonuc.aspx</Error_URL>
<Success_URL>http://localhost:62361/turkpos.api/Sonuc.aspx</Success_URL>
<Order_ID>sipariş1</Order_ID>
<Order_Description></Order_Description>
<Amount>100,00</Amount>
<Payment_Hash>4HaFjeEYpcVMQYgq94lxuYWHAV8=</Payment_Hash>
<Transaction_ID></Transaction_ID>
<IPAddress>127.0.0.1</IPAddress>
<Referrer_URL>https://dev.param.com.tr/tr</Referrer_URL>
</TP_Islem_Odeme_BKM>
</soap:Body>
</soap:Envelope>"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "https://turkpos.com.tr/TP_Islem_Odeme_BKM"
}
response = requests.post(url, data=xml_data.encode("utf-8"), headers=headers)

print("Status Code:", response.status_code)
print("Gelen XML:", response.text)