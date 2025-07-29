class LstUtils:

    @staticmethod
    def gop(value):
        if type(value) == list:
            temp = list(value)
            n = 1

            for i in temp:
                n *= i

            return n

        else:
            exit("gop(value) is not list")

    @staticmethod
    def nanu(value):
        if type(value) == list:
            temp = list(value)
            n = 1

            for i in temp:
                n /= i

            return n

        else:
            exit("gop(value) is not list")

    @staticmethod
    def minus(value):
        if type(value) == list:
            temp = list(value)
            n = 0

            for i in temp:
                n -= i

            return n

        else:
            exit("gop(value) is not list")

    @staticmethod
    def plus(value):
        if type(value) == list:
            temp = list(value)
            n = 0

            for i in temp:
                n += i

            return n

        else:
             exit("gop(value) is not list")