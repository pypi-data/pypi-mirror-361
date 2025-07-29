import requests

apiUrl = "https://api.shipxy.com/apicall/v3";


def getMethod(methodName, params):
    baseUrl = apiUrl + "/" + methodName
    return requests.get(baseUrl, params)


def postMethod(methodName, params):
    baseUrl = apiUrl + "/" + methodName
    return requests.post(baseUrl, params)


def getMethodJson(methodName, params):
    baseUrl = apiUrl + "/" + methodName
    return requests.get(baseUrl, params).json()


def postMethodJson(methodName, params):
    baseUrl = apiUrl + "/" + methodName
    return requests.post(baseUrl, params).json()
