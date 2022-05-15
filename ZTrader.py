import requests,json
import urllib.parse
import ZBaseFunc
def GetNewAccessToken(OAuthUserID="", RefreshToken = "",TradeDict=[]):
    headers = {
    'Content-Type':'application/x-www-form-urlencoded'
        }
    RefreshToken = urllib.parse.quote(RefreshToken)
    grant_type = "grant_type=refresh_token"
    refresh_token = "refresh_token="+RefreshToken
    access_type = "access_type=offline"
    code = "code="
    client_id = "client_id="+OAuthUserID
    redirect_uri = "redirect_uri=https%3A%2F%2Flocalhost%3A8080"
    Text = grant_type+"&"+refresh_token+"&"+access_type+"&"+code+"&"+client_id+"&"+redirect_uri

    response = requests.post("https://api.tdameritrade.com/v1/oauth2/token", headers=headers, data=Text)
    try:
        Result = json.loads(response.content.decode())
        access_token = Result['access_token']
        refresh_token =Result['refresh_token']
        Status = "Get Token Successed"
        TradeDict["TdaAPIRefreshToken"] = refresh_token
        ZBaseFunc.SaveConfigFile(FileName="DefaultTradePara.ZFtd", DumpDict=TradeDict)

    except:
        Status = "Get Token Failed"
        access_token = refresh_token = None

    return (Status ,refresh_token ,access_token)

