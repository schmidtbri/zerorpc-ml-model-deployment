import zerorpc


def run():
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:4242")
    result = client.get_models()
    print("Result: {}".format(result))


if __name__ == "__main__":
    run()
