import zerorpc


def run():
    c = zerorpc.Client()
    c.connect("tcp://127.0.0.1:4242")
    print(c.iris_model_predict({"sepal_length":1.1, "sepal_width":1.2, "petal_length":1.4, "petal_width":1.5}))


if __name__ == "__main__":
    run()
