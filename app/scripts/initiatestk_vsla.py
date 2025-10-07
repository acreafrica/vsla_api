# import requests
# import urllib3

# # 🔧 Disable SSL warnings if verify=False
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# # Configurable variables  # replace with correct base URL
# BASE_URL = "http://test.543.cgrate.co.zm:55555"       # replace with actual endpoint
# USERNAME = "1556629637703"                    # replace with actual username
# PASSWORD = "M42X45i1"#LeB6zI2K"                # replace with actual password
#                          # replace with actual password

# url = f"{BASE_URL}/Konik/KonikWs"

# payload = f"""<?xml version="1.0" encoding="UTF-8"?>
# <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
#                   xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
#                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
#                   xmlns:kon="http://konik.cgrate.com">
#     <soapenv:Header>
#         <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" 
#                        soapenv:mustUnderstand="1">
#             <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" 
#                                 wsu:Id="{USERNAME}">
#                 <wsse:Username>{USERNAME}</wsse:Username>
#                 <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{PASSWORD}</wsse:Password>
#             </wsse:UsernameToken>
#         </wsse:Security>
#     </soapenv:Header>
#     <soapenv:Body>
#         <kon:processCustomerPayment>
#             <transactionAmount>5</transactionAmount>
#             <customerMobile>260950261186</customerMobile>
#             <paymentReference>7f08c-1e5-441-8b-c7c8</paymentReference>
#         </kon:processCustomerPayment>
#     </soapenv:Body>
# </soapenv:Envelope>
# """

# headers = {
#     "Content-Type": "application/soap+xml"
# }

# try:
#     response = requests.post(url, headers=headers, data=payload, verify=False)  # ⚠️ verify=False skips SSL check
#     print("Status Code:", response.status_code)
#     print("Response Body:")
#     print(response.text)

# except requests.exceptions.SSLError as ssl_err:
#     print("SSL Error:", ssl_err)
# except Exception as e:
#     print("Error:", e)
import requests
import urllib3

# 🔧 Disable SSL warnings if verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurable variables
BASE_URL = "http://test.543.cgrate.co.zm:55555"   # replace with actual endpoint
USERNAME = "1556629637703"                        # replace with actual username
PASSWORD = "M42X45i1"#LeB6zI2K"                    # ✅ ensure full password is included

url = f"{BASE_URL}/Konik/KonikWs"

# Build SOAP XML payload
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
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{PASSWORD}</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
        <kon:processCustomerPayment>
            <transactionAmount>5</transactionAmount>
            <customerMobile>260950261186</customerMobile>
            <paymentReference>7f5717c-1e5-41-8b-c5c8</paymentReference>
        </kon:processCustomerPayment>
    </soapenv:Body>
</soapenv:Envelope>
"""

headers = {
    "Content-Type": "text/xml; charset=utf-8",
    "SOAPAction": "processCustomerPayment"
}

try:
    print(f"Sending SOAP request to: {url}\n")

    # 🕒 Set timeout to 60 seconds (1 minute)
    response = requests.post(url, headers=headers, data=payload, verify=False, timeout=360)

    print("✅ Status Code:", response.status_code)
    print("📄 Response Body:\n")
    print(response.text)

except requests.exceptions.Timeout:
    print("⏳ Request timed out after 1 minute.")
except requests.exceptions.SSLError as ssl_err:
    print("❌ SSL Error:", ssl_err)
except requests.exceptions.RequestException as req_err:
    print("❌ Request Error:", req_err)
except Exception as e:
    print("⚠️ General Error:", e)
