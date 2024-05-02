import thriftpy2

timestamp_thrift = thriftpy2.load("timestamp_service.thrift", module_name="timestamp_thrift")

from thriftpy2.rpc import make_server


class TimestampHandler:
    def getCurrentTimestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def start_server():
    server = make_server(timestamp_thrift.TimestampService, TimestampHandler(), '127.0.0.1', 10000)
    print("Starting the Thrift server...")
    server.serve()


if __name__ == "__main__":
    start_server()
