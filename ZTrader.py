import requests,json
import urllib.parse
import ZBaseFunc

class TDAAPIs:
    def __init__(self, OAuthUserID, RefreshToken,TdaAccountID):
        self.OAuthUserID = OAuthUserID
        self.RefreshToken = RefreshToken
        self.TdaAccountID = TdaAccountID
        ZBaseFunc.SetDLAPIPara('OAuthUserID', OAuthUserID)
        ZBaseFunc.SetDLAPIPara('RefreshToken', RefreshToken)
        ZBaseFunc.SetDLAPIPara('TdaAccountID', TdaAccountID)

    def GetNewAccessToken(self,OAuthUserID=None, RefreshToken = None,TradeDict=dict()):
        if OAuthUserID !=None:
            self.OAuthUserID = OAuthUserID
        if RefreshToken !=None:
            self.RefreshToken = RefreshToken

        headers = {
        'Content-Type':'application/x-www-form-urlencoded'
            }
        self.RefreshToken = urllib.parse.quote(self.RefreshToken)
        grant_type = "grant_type=refresh_token"
        refresh_token = "refresh_token="+self.RefreshToken
        access_type = "access_type=offline"
        code = "code="
        client_id = "client_id="+self.OAuthUserID
        redirect_uri = "redirect_uri=https%3A%2F%2Flocalhost%3A8080"
        Text = grant_type+"&"+refresh_token+"&"+access_type+"&"+code+"&"+client_id+"&"+redirect_uri

        try:
            response = requests.post("https://api.tdameritrade.com/v1/oauth2/token", headers=headers, data=Text)
            Result = json.loads(response.content.decode())
            self.TdaAPIAccessToken = access_token = Result['access_token']
            self.RefreshToken = refresh_token =Result['refresh_token']
            Status = "Get Token Successed"
            TradeDict["TdaAPIRefreshToken"] = refresh_token
            ZBaseFunc.SaveConfigFile(FileName="DefaultTradePara.ZFtd", DumpDict=TradeDict)
            ZBaseFunc.SetDLAPIPara('AccessToken', Result['access_token'])

        except:
            Status = "Get Token Failed"
            access_token = refresh_token = None

        return (Status ,refresh_token ,access_token)

    def GetAccountInfo(self,TdaAccountID=None, TdaAPIAccessToken = None):
        if TdaAccountID !=None:
            self.TdaAccountID = TdaAccountID
        if TdaAPIAccessToken !=None:
            self.TdaAPIAccessToken = TdaAPIAccessToken
        AccountInfo = dict()
        headers = {
        'Authorization':'Bearer '+self.TdaAPIAccessToken
            }

        url = "https://api.tdameritrade.com/v1/accounts/"+self.TdaAccountID +'?fields=positions'

        try:
            response = requests.get(url=url, headers=headers)
            Result = json.loads(response.content.decode())
            AccountInfo["NetLiq"] = Result['securitiesAccount']['currentBalances']['liquidationValue']
            Status = "Account Successed"

        except:
            pass
            Status = "Account Failed"
        return Status,AccountInfo

import pandas as pd
import numpy as np
import talib
import ZfinanceCfg





