import zerorpc


def run():
    client = zerorpc.Client()
    client.connect("tcp://127.0.0.1:4242")
    result = client.iris_model_predict({"sepal_length": 1.1,
                                        "sepal_width": 1.2,
                                        "petal_length": 1.4,
                                        "petal_width": 1.5})
    print("Result: {}".format(result))


if __name__ == "__main__":
    run()
