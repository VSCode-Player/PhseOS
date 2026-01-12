from PhseXlib.locals import * # type: ignore

Encode_dict = GetEncoding("PhseEncode")

def msg(*string):
    for i in string:
        if i[0] == "b":
            print(Encode_dict[i[1:]])
        else:
            print(i[1:-1])