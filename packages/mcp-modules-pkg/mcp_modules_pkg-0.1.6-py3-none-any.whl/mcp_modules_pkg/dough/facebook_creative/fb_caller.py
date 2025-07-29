"""Request를 도와주는 모듈
    requests하면서 json 오브젝트로 바꿔야하는 경우가 많은데 그때마다
    예외처리 하는 코드 넣기 싫어서 만들어봄
    팀에서 공통으로 이런 Method를 만들어서 사용하면 좋을것 같음
"""
import json
import requests

class ApiCaller:
    """Masterapi쓰면 되는데 graphapi-video를 써야해서 만든 모듈
    """

    GRAPH_API_VERSION = 'v20.0'
    def __init__(self) -> None:
        """초기화하면서 facebook access_token을 받아옵니다.
        """
        response = ApiCaller.fetch_data(
            "https://masterapi.datawave.co.kr/api/raw/facebook/auth?account=puzzle1studio")
        self.access_token = response['access_token']
    def get_access_token(self) -> str:
        """페이스북 API호출에 필요한 AccessToken을 반환해주는 함수
            ApiCaller가 선언이 될 때 받아온다.
        """
        return self.access_token
    @staticmethod
    def fetch_data(url, method='GET', payload=None, file=None) -> any:
        """requests를 쓰면서 생기는 예외처리를 해놓은 함수입니다.

        Args:
            url (_type_): requests할 url
            method (str, optional): method default는 GET
            payload (_type_, optional): payload
            file (_type_, optional): file

        Raises:
            ValueError: method를 잘못 썼을 경우

        Returns:
            Json Object : requests에 대한 응답을 json object로 반환
        """
        response = None
        print(method)
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, files= file, data= payload)
                print(response.text)
            else:
                raise ValueError
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f"Error fetching data: {error}")
            return None
        except ValueError as error:
            print(error)
            print("unsupported method")

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as error:
            print(f"Error parsing JSON data: {error}")
            return None

        return data
    def graphapi_get(self,path, querystring):
        """facebook graph api get호출 도우미

        Args:
            path (_type_): url path
            querystring (_type_): url querystring
            #sample : https://masterapi.datawave.co.kr/api/raw/facebook/graph/v16.0/me/adaccounts
                ?account=bitmango&fields=id,name&limit=5000
            sample 과 같은 형태의 api url 주소를 만들어주기 위한 caller
            path 와 queryString을 받아서 하나의 Url 주소를 만들어준다.
            Path를 입력할때는 꼭 /를 포함해줘야 한다.
        """
        url = (
            f"https://masterapi.datawave.co.kr/api/raw/facebook/graph/"
            f"{self.GRAPH_API_VERSION}{path}?{querystring}"
        )
        print(url)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print(f"Error fetching data: {error}")
            return None
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as error:
            print(f"Error parsing JSON data: {error}")
            return None

        return data

    def graphapi_post(self, path, querystring, payload=None):
        """graphapi post호출 도우미

        Args:
            path (_type_): api path
            querystring (_type_): api querystring
            payload (_type_, optional): payload default None

        Returns:
            json : post호출을 하고 나서 돌아온 Response의 json
        """
        """
        url = (
            f"https://masterapi.datawave.co.kr/api/raw/facebook/graph/"
            f"{self.GRAPH_API_VERSION}{path}?{querystring}"
        )
        """
        headers = {
            'Content-Type': 'application/json',
        }
        url = (
            f"https://graph.facebook.com/{self.GRAPH_API_VERSION}{path}?access_token={self.access_token}"
        )
        data = None
        response = requests.post(url,data=payload,headers=headers)
        if response.status_code == 200:
            try:
                print(response.text)
                data = json.loads(response.text)
            except json.JSONDecodeError as error:
                print(f"Error parsing JSON data: {error}")
                return None
        else:
            print(f"Failed: {response.status_code}, {response.text}")
            return None

        return data
