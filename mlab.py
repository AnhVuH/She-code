import mongoengine

#mongodb://<dbuser>:<dbpassword>@ds263380.mlab.com:63380/she-code

host = "ds263380.mlab.com"
port = 63380
db_name = "she-code"
user_name = "admin123"
password = "admin123"


def connect():
    mongoengine.connect(db_name, host=host, port=port, username=user_name, password=password)

def list2json(l):
    import json
    return [json.loads(item.to_json()) for item in l]


def item2json(item):
    import json
    return json.loads(item.to_json())
