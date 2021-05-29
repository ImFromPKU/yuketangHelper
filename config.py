import json


class Config:
    __conf = None
    csrftoken = None
    sessionid = None
    uni_id = None
    ykt_addr = None
    heartrate = None
    heartbeat_pack_size = None

    def __new__(cls):
        if not cls.__conf:
            with open("config.json") as file:
                try:
                    conf_j = json.loads(file.read())
                except:
                    raise Exception("配置读取错误")
                else:
                    cls.csrftoken = conf_j["csrftoken"]
                    cls.sessionid = conf_j["sessionid"]
                    cls.uni_id = conf_j["university-id"]
                    cls.ykt_addr = conf_j["ykt_address"]
                    cls.heartrate = conf_j["heartrate"]
                    cls.heartbeat_pack_size = conf_j["heartbeat_pack_size"]
            cls.__conf = super(Config, cls).__new__(cls)
        return cls.__conf

    def __init__(self) -> None:
        pass
