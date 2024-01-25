import re
from lib import API_USER, API_SECRET, API_URL, SmartPayApiAsync
import asyncio
from urllib.parse import quote
import httpx
from fastapi import status
 
async def qrdecode(qr):
    try:
        url_parsed = quote(qr)
        async with httpx.AsyncClient() as client:
            response = await client.get("https://connect.smartpay.com.vc/api/pix/qrdecode?qrcode=" + url_parsed)
            a = response.json()
            return a['data']['key']
    except Exception:
        raise ValueError("invalidBrcode")
 
async def formatPixKey(pixkey):
    # qrcode
    if len(pixkey) > 36:
        pixkey_response = await qrdecode(pixkey)
        return [True, pixkey_response]
 
    # email
    if "@" in pixkey:
        if not isMail(pixkey):
            return [False, "Invalid Email"]
        return [True, pixkey.lower()]
 
    # phone
    if "+" in pixkey:
        pixkey = "+" + re.sub(r'[^\d]+', '', pixkey)
        if len(pixkey) != 14:
            return [False, "Invalid Phone number"]
        if pixkey[:3] != "+55":
            return [False, "Not Brazilian number"]
        return [True, pixkey]
 
    # key
    if len(pixkey) == 36:
        return [True, pixkey]
 
    # formatted cnpj
    if len(pixkey) == 18:
        print('es formatted cnpj')
        if not re.match(r'^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$', pixkey):
            return [False, "Invalid pixkey"]
        if not isCnpj(pixkey):
            return [False, "Invalid cnpj"]
        pixkey = re.sub(r'[^\d]+', '', pixkey)
        return [True, pixkey]
 
    # fone with missing +
    if len(pixkey) == 13:
        if re.match(r'^\d+$', pixkey):
            if pixkey[:2] != "55":
                return [False, "Invalid pixkey"]
            return [True, "+" + pixkey]
 
    # every other option has at least 11 chars
    if len(pixkey) < 11:
        return [False, "Invalid pixkey"]
 
    # cnpj or formatted cpf
    if len(pixkey) == 14:
        # unformatted cnpj
        if re.match(r'^\d+$', pixkey):
            if not isCnpj(pixkey):
                return [False, "Invalid pixkey"]
            return [True, pixkey]
        # formatted cpf
        if re.match(r'^\d{3}\.\d{3}\.\d{3}\-\d{2}$', pixkey):
            if not isCpf(pixkey):
                return [False, "Invalid cpf"]
            return [True, re.sub(r'[^\d]+', '', pixkey)]
 
    # formatted cpf or phone without country
    if len(pixkey) == 11:
        if not re.match(r'^\d+$', pixkey):
            return [False, "Invalid pixkey"]
        if isCpf(pixkey):
            return [True, re.sub(r'[^\d]+', '', pixkey)]
        if pixkey[0] == "0":
            return [False, "Invalid pixkey"]
        return [True, "+55" + pixkey]
 
    # either wrong formatted cpf or formatted phone number
    pixkey = re.sub(r'[^\d]+', '', pixkey)
    if len(pixkey) == 12:
        if pixkey[0] != "0":
            return [False, "Either wrong formatted cpf or formatted phone number"]
        return [True, "+55" + pixkey[1:]]
 
    if len(pixkey) == 11:
        if isCpf(pixkey):
            return [True, pixkey]
        return [True, "+55" + pixkey]
 
    return [False, "Invalid pixkey"]
 
 
 
async def validate_existence_pixKey(pixKey):
    validated_pixkey= await formatPixKey(pixKey)
 
    if validated_pixkey[0]==True:
        try:
            SPAPI = SmartPayApiAsync(API_USER,API_SECRET,API_URL)
            postdata = {
            "address": validated_pixkey[1] # pixkey
            }
 
            res = await SPAPI.sendApi("pix/checkkey", postdata)
 
            if res['status']=='ok':
                return({"status_code": status.HTTP_200_OK, "detail": {"msg": "valid pixkey", "reformated_key": validated_pixkey[1], "name": res['data']['name']}})
 
            else:
                return({"status_code": status.HTTP_200_OK, "detail": {"msg": "pix key not found", "reformated_key": None, "name":None}} )
 
        except ValueError as e:
            return({'status_code': status.HTTP_401_SERVICE_UNAVAILABLE, "detail": e})
        except:
            return({"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "detail": "an unexpected error ocurred"})
 
    else:
        return({"status_code": status.HTTP_200_OK, "detail":{"msg": validated_pixkey[1],"reformated_key": None, "name": None}})
 
