import requests
# https://test.543.cgrate.co.zm:8443/Konik/KonikWs or http://test.543.cgrate.co.zm:55555/Konik/KonikWs
# Configurable variables
BASE_URL = "http://test.543.cgrate.co.zm:55555"       # replace with actual endpoint
USERNAME = "1758019102130"                    # replace with actual username
PASSWORD = "zd9X6N3l"                # replace with actual password

url = f"{BASE_URL}/Konik/KonikWs"

payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                  xmlns:kon="http://konik.cgrate.com">
    <soapenv:Header>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" 
                       soapenv:mustUnderstand="1">
            <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" 
                                wsu:Id="{USERNAME}">
                <wsse:Username>{USERNAME}</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">
                    {PASSWORD}
                </wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <kon:processCashDeposit>
            <transactionAmount>5</transactionAmount>
            <customerAccount>097759676</customerAccount>
            <issuerName>Airtel</issuerName>
            <depositorReference>f098a4f3-392f-44d4-b10a-1f7737091f2d</depositorReference>
        </kon:processCashDeposit>
    </soapenv:Body>
</soapenv:Envelope>
"""

headers = {
    "Content-Type": "application/soap+xml"
}

response = requests.post(url, headers=headers, data=payload)

print("Status Code:", response.status_code)
print("Response Body:")
print(response.text)