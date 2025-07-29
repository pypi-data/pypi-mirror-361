class NPyUtils:

    @staticmethod
    def putin(string, count, sel, front):
        if string == str or string == int:
            if count == int:
                if sel == str or string == int:
                    if front == bool:
                        temp = []
                        string = str(string)
                        sel = str(sel)

                        if front:
                            # front put string
                            for i in range(count):
                                temp.append(string)

                            # next put sel
                            for i in range(len(sel)):
                                temp.append(sel[i])

                            return "".join(temp)
                        else:
                            # front put sel
                            for i in range(len(sel)):
                                temp.append(sel[i])

                            # next put string
                            for i in range(count):
                                temp.append(string)

                            return "".join(temp)
                    else:
                        raise "front is not bool"
                else:
                    raise "sel is not str or int"
            else:
                raise "count is not int"
        else:
            raise "string is not str or int"