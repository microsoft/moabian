# A single global App dictionary to hold the command line parameters


class App:
    __hidden = {"debug": False, "port": 3306}

    def print():
        print(App.__hidden)

    @staticmethod
    def config(debug, port):
        App.__hidden["debug"] = debug
        App.__hidden["port"] = port

    @staticmethod
    def get(name):
        return App.__hidden[name]

    @staticmethod
    def debug():
        return App.__hidden["debug"]


if __name__ == "__main__":
    # from app import App

    print(App.debug())
    print(App.get["debug"])
