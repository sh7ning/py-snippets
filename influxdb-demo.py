from influxdb import InfluxDBClient
import random
import datetime


class InfluxDB(object):
    def __init__(self, host='localhost', port=8086, username='', password=''):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.client = InfluxDBClient(host, port, username, password)

    def select_db(self, db_name):
        db_list = self.client.get_list_database()
        not_exists = True
        for db in db_list:
            if db['name'] == db_name:
                not_exists = False
                break
        if not_exists:
            self.client.create_database(db_name)
            # 设置默认保留策略
            self.client.create_retention_policy("30d_rp", "30d", "1", db_name, True, "4w")

        self.client.switch_database(db_name)

        return self


json_body = list()

now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:")+"00Z"
t = (datetime.datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ") - datetime.timedelta(minutes=60*24*7))

for i in range(1, 60*24*7):     # 60*24*7
    t = t + datetime.timedelta(minutes=1)

    json_body.append({
        "measurement": "rate_history",  # 表名
        "tags": {   # 用于查询的tag
            "type": "rate",
        },
        "fields": {     # 数据
            "value": random.randint(160, 400) / 100
        },
        # "time": int(t.timestamp())     # 这个针对 time_precision=s
        "time": int(t.timestamp() / 60)  # 建议用这个，这个针对 time_precision=m
        # "time": t   # 这个用法要小心，主要是时区问题，比如只写入当前时间一条记录，然后查询不到，时区问题。。。
    })

host = '192.168.31.76'
influx = InfluxDB(host, 8086, '', '')

influx_db_name = "demo"

influx.client.drop_database(influx_db_name)     # TODO
influx.select_db(influx_db_name)

# print(influx.client.get_list_retention_policies())
influx.client.write_points(json_body, time_precision='m')   # 这里的 s 调整会影响具体数据，不过只对 time 为 datetime 类型生效， time 为 int 的时候应该为 s

sql = 'SELECT distinct("value") FROM "30d_rp"."rate_history" WHERE time >= now() - 1h GROUP BY time(1m) fill(null);'
result = influx.client.query(sql)

print(f"Result: {result}")

