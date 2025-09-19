import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import (BaseModel,
                      AnyHttpUrl ,
                      HttpUrl, 
                        validator,
                          EmailStr, 
   
    SecretStr
                      )

from pydantic_settings  import (
   
    BaseSettings, 
  
)


from dotenv import load_dotenv

from urllib.parse import urlencode

from dataclasses import dataclass,InitVar
import urllib


load_dotenv()
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DigiBima\\SQLEXPRESS;"
    "DATABASE=vsla;"
    "UID=sa;"
    "PWD=RiftValley@2022;"
    "MARS_Connection=Yes;"
    )

class Settings(BaseSettings):
    DEBUG: bool=True
    #API_V1_STR: str
    SECRET_KEY: SecretStr=""
    PROJECT_NAME: str="Digibima API"
    PROJECT_VERSION: str="0.1.0"
    PROJECT_DESCRIPTION: str="Digibima API is a RESTful API for managing insurance policies"
    PROJECT_DOMAIN: str ="https://digibima.com"   
    REDIS_URL: str="redis://localhost:6379/0"
    #tokens
    WHATSAPP_API_TOKEN:str=""
    SESSION_COOKIE_EXPIRE_MINUTES: int = 60

    ADMIN_SESSION_COOKIE_EXPIRE_MINUTES: int = 60

    PORTAL_SESSION_COOKIE_EXPIRE_MINUTES: int = 600


    #tokens
    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    #EMAIL_ACTIVATION_TOKEN_EXPIRE_MINUTES: int = 60
    ACCOUNT_VERIFICATION_CODE_EXPIRE_MINUTES: int = 3600

    #SMTP_HOST = 'smtp.gmail.com'
    SMTP_EMAIL_SENDER: str=" "
    SMTP_EMAIL_PASSWORD: str=""
    EMAILS_ENABLED:bool=True
    SMTP_PORT :int =465
    #SMTP_USER=SMTP_EMAIL_SENDER
    #SMTP_PASSWORD=SMTP_EMAIL_PASSWORD
    SMTP_TLS:bool=False
    EMAILS_FROM_NAME: str="Digibima"

    DIGITAL_OCEAN_SPACES_KEY: str=""
    DIGITAL_OCEAN_SPACES_SECRET: str=""
    DIGITAL_OCEAN_SPACES_ENDPOINT_DOMAIN: str="digitaloceanspaces.com"
    DIGITAL_OCEAN_SPACES_CDN_DOMAIN: str="digibima.nyc3.cdn.digitaloceanspaces.com"

    #the bucket hosts things like logos e.t.c
    DIGITAL_OCEAN_SPACES_PUBLIC_BUCKET_NAME: str="digibima-public"

    ALLOWED_ORIGINS: List[str]= [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001"]
    # ASYNC_DATABASE_URL:str = f"mssql+aioodbc:///?odbc_connect={params}"
    ASYNC_DATABASE_URL: str= "mssql+aioodbc://sa:admin123@localhost,1433/vsla?driver=ODBC+Driver+17+for+SQL+Server&MARS_Connection=Yes"

    EMAIL_TEMPLATES_DIR: str=""
    ACCOUNT_ACTIVATION_URL: str=""
    TEST_EMAIL: EmailStr="vkoech@acreafrica.com"

    


    class Config:
        case_sensitive = True


settings = Settings()