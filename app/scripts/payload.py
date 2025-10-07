payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                  xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                  xmlns:kon="http://konik.cgrate.com">
    <soapenv:Header>
        <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" 
                       soapenv:mustUnderstand="1">
            <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" 
                                wsu:Id="1758019102130">
                <wsse:Username>LeB6zI2K</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{PASSWORD}</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <kon:processCustomerPayment>
            <transactionAmount>5</transactionAmount>
            <customerMobile>260950261186</customerMobile>
            <paymentReference>7f0d97ec-1eb5-48341-8b1tg-c76c12</paymentReference>
        </kon:processCustomerPayment>
    </soapenv:Body>
</soapenv:Envelope>
"""

USERNAME = "1758019102130"                    # replace with actual username
PASSWORD = "LeB6zI2K"  