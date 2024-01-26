from urllib.parse import quote
from modules.validate_memo import formatPixKey, isMail

async def validate_existence_pixKey(pixKey):
    # prepare the payload
    validated_pixkey= formatPixKey(pixKey)

    if validated_pixkey [0] == True:
        try:
          if len(pixKey) <= 36 or (len(pixKey) >= 36 and isMail(pixKey)):
            SPAPI = SmartPayApiAsync(API_USER,API_SECRET,API_URL)
            postdata = {
              "address": validated_pixkey[1] # pixkey
            }
            data = await SPAPI.sendApi("pix/checkkey", postdata)

            if data.get('status') == 'ok':
                return {
                    "status_code": status.HTTP_200_OK, 
                    "detail": {
                        "msg": "valid pixkey", 
                        "reformated_key": validated_pixkey[1], 
                        "name": data['data']['name'], 
                        "amount": ""
                    }
                }

            else:
                return {
                    "status_code": status.HTTP_400_BAD_REQUEST, 
                    "detail": {
                        "msg": "pix key not found",
                        "reformated_key": None, 
                        "name": None
                    }
                  }

          if len(pixKey) > 36:
            async with httpx.AsyncClient() as client:
              url_parsed = quote(validated_pixkey[1])
              response = await client.get(f"https://connect.smartpay.com.vc/api/pix/qrdecode?qrcode={url_parsed}")

              if response.status_code != 200:
                raise Exception()

              data = response.json()

              if data.get('status') == 'ok':
                return {
                  "status_code": status.HTTP_200_OK, 
                  "detail": {
                      "msg": "valid pixkey", 
                      "reformated_key": validated_pixkey[1], 
                      "name": response.json()['data']['name'], 
                      "amount": str(response.json()['data']['amount'])
                  }
                }

              if data.get('status') == 'failed':
                return {
                    "status_code": status.HTTP_400_BAD_REQUEST, 
                    "detail": {
                        "msg": "Expired or Invalid QR code"
                    }
                  }
        except Exception:
          return {
            "status_code": status.HTTP_500_BAD_REQUEST, 
            "detail": {
                "msg": "an unexpected error ocurred"
            }
          }
    else:
        return({"status_code": status.HTTP_200_OK, "detail":{"msg": validated_pixkey[1],"reformated_key": None, "name": None}})
