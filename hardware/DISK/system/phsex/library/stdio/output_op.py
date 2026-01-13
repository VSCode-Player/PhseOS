from PhseXlib.locals import * # type: ignore

Encode_dict = GetEncoding("PhseEncode")
format_list = {"n":"\n"}

def msg(*string):
    for i in string:
        if i[0] == "b":
            print(Encode_dict[i[1:]])
        else:
            for j,k in zip(i[1:-1],range(len(i))):
                if j == "\\":
                    print(format_list[i[k+1]],end="")
                else:
                    print(j, end="")
                # print(i[1:-1])