from shipxy import Shipxy

from key import key
# key = "请从 API控制台 申请";

if __name__ == '__main__':
    # response = Shipxy.SearchShip(key, "coco")
    response = Shipxy.GetSingleShip(key, 413961925)
    # response = Shipxy.GetManyShip(key, "413961925,477232800,477172700")
    # response = Shipxy.GetFleetShip(key, "6db8d8ec-858d-4417-86c0-666d61e340bf")
    # response = Shipxy.GetSurRoundingShip(key, 413961925)
    # response = Shipxy.GetAreaShip(key, "121.289063,35.424868-122.783203,35.281501-122.167969,33.979809")
    # response = Shipxy.GetShipRegistry(key, 413961925)
    # response = Shipxy.SearchShipParticular(key, 477172700, None, None, None)

    # response = Shipxy.SearchPort(key, "qingdao")
    # response = Shipxy.GetBerthShips(key, "CNSHG")
    # response = Shipxy.GetAnchorShips(key, "CNSHG")
    # response = Shipxy.GetETAShips(key, "CNSHG", 1746612218, 1747044218)

    # response = Shipxy.GetShipTrack(key, 477172700, 1746612218, 1747044218)
    # response = Shipxy.SearchshipApproach(key, 477172700, 1746612218, 1747044218)

    # response = Shipxy.GetPortofCallByShip(key, 477172700, None, None, None, 1751007589, 1751440378)
    # response = Shipxy.GetPortofCallByShipPort(key, 477172700, None, None, None, 'CNSHG', 1751007589, 1751440378)
    # response = Shipxy.GetShipStatus(key, 477172700, None, None, None)
    # response = Shipxy.GetPortofCallByPort(key, 'CNSHG', 1751407589, 1751440378)

    # response = Shipxy.PlanRouteByPoint(key, '113.571144,22.844316', "121.58414,31.37979")
    # response = Shipxy.PlanRouteByPort(key, 'CNGZG', "CNSHG")
    # response = Shipxy.GetSingleETAPrecise(key,  477172700,  "CNSHG", 20)

    # response = Shipxy.GetWeatherByPoint(key, 123.58414, 27.37979)
    # response = Shipxy.GetWeather(key, 1)
    # response = Shipxy.GetAllTyphoon(key)
    # response = Shipxy.GetSingleTyphoon(key, 2477927)
    # response = Shipxy.GetTides(key)
    # response = Shipxy.GetTideData(key, 8000005, '2025-03-01', '2025-03-05')

    # response = Shipxy.GetNavWarning(key, '2024-07-21 20:00', '2024-09-21 20:00')

    # response = Shipxy.AddFleet(key, "测试船队1", "477985700,412751691", 1);
    # response = Shipxy.UpdateFleet(key, 'c02def78-a57d-4311-bee3-1c89a018cddf', "测试船队", "477985700", 1)
    # response = Shipxy.GetFleet(key, 'c02def78-a57d-4311-bee3-1c89a018cddf')
    # response = Shipxy.DeleteFleet(key, '8bef754a-b117-4050-8878-65c979185130')
    # response = Shipxy.AddFleetShip(key, 'c02def78-a57d-4311-bee3-1c89a018cddf',  "477985700,412751690")
    # response = Shipxy.UpdateFleetShip(key, 'c02def78-a57d-4311-bee3-1c89a018cddf', "477985700")
    # response = Shipxy.DeleteFleetShip(key, 'c02def78-a57d-4311-bee3-1c89a018cddf', "477985700")
    # response = Shipxy.AddArea(key, "119.846180,32.345143-119.814280,32.311867-119.4661,32.291067-119.375887,32.213847",
    #                           "浙江沿海区域1", "http://192.186.1.1:8000/Shipxy/testdemo",
    #                           3, 59,"1,2,3", "c02def78-a57d-4311-bee3-1c89a018cddf");

    # response = Shipxy.UpdateArea(key, "1d0a807c-5c39-492f-8c99-8a1135da6667",
    #                              "119.846180,32.345143-119.814280,32.311867-119.4661,32.291067-119.375887,32.213847",
    #                              "浙江沿海区域", "http://192.186.1.1:8000/Shipxy/testdemo",
    #                              3, 59, "1,2,3", "c02def78-a57d-4311-bee3-1c89a018cddf");
    # response = Shipxy.GetArea(key, '1d0a807c-5c39-492f-8c99-8a1135da6667')
    # response = Shipxy.DeleteArea(key, '1d0a807c-5c39-492f-8c99-8a1135da6667')

    print(response)
    # print("test")