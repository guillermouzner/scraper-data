from urllib.parse import quote
from modules.validate_memo import formatPixKey, isMail

async def validate_existence_pixKey(pixKey):
    # prepare the payload
    validated_pixkey= formatPixKey(pixKey)

    if validated_pixkey [0] == True:
        if len(pixKey) <= 36 or (len(pixKey) >= 36 and isMail(pixKey)):
            try:
                SPAPI = SmartPayApiAsync(API_USER,API_SECRET,API_URL)
                postdata = {
                "address": validated_pixkey[1] # pixkey
                    }
                res = await SPAPI.sendApi("pix/checkkey", postdata)

                if res['status']=='ok':
                    return({"status_code": status.HTTP_200_OK, "detail": {"msg": "valid pixkey", "reformated_key": validated_pixkey[1], "name": res['data']['name'], "amount": ""}})
                else:
                    return({"status_code": status.HTTP_200_OK, "detail": {"msg": "pix key not found", "reformated_key": None, "name":None}} )

            except:
                return({"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "detail": "an unexpected error ocurred"})
            
        else:
            async with httpx.AsyncClient() as client:
                url_parsed = quote(validated_pixkey[1])
                response = await client.get(f"https://connect.smartpay.com.vc/api/pix/qrdecode?qrcode={url_parsed}")

            if response.status_code == 200:
                return({"status_code": status.HTTP_200_OK, "detail": {"msg": "valid pixkey", "reformated_key": validated_pixkey[1], "name": response.json()['data']['name'], "amount": str(response.json()['data']['amount'])}})
            else:
                return({"status_code": status.HTTP_200_OK, "detail": {"msg": "pix key not found", "reformated_key": None, "name":None}} )
    else:
        return({"status_code": status.HTTP_200_OK, "detail":{"msg": validated_pixkey[1],"reformated_key": None, "name": None}})
