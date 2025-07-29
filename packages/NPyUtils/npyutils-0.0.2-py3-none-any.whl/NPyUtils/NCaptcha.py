import random
import string

class NCaptcha:

    @staticmethod
    def captcha_b1(way):
        match way:
            case "number":
                random_num = random.sample(range(1, 9), 6)

                return "".join(map(str, random_num))
            case "string":
                random_str = random.choices(string.ascii_letters, k=6)

                return "".join(random_str)
            case "all":
                chars = string.ascii_letters + string.digits
                random_str = "".join(random.choices(chars, k=6))

                return "".join(random_str)
            case _:
                raise "Invalid arg"