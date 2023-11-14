def translate(someObj):
    if(type(someObj)!=type("")):
        return someObj
    elif(someObj[0]=="\"" or someObj[0]=="'"):
        #print(someObj[1:-1])
        return someObj[1:-1]
    elif(48<=ord(someObj[0])<=57):
        return float(someObj)
    else:
        return {
            "false":False,
            "true":True,
            "False":False,
            "True":True
        }[someObj]
def parse(jsonStr):
    maps = []
    islist = []
    keys = ["TOT"]
    tmpValue = ""
    strlen = len(jsonStr)
    mLen = 0#len of map
    kLen = 1#len of keys
    i = 0
    keyInputing=True
    quoting=[]
    qLen = 0#len of quoting marks
    while(i<strlen):
        #print(jsonStr[i],quoting,keys)
        if(jsonStr[i]=="\"" or jsonStr[i]=="'"):
            # type of quote marks:
            #    "''"
            #    "'"
            if(qLen>0 and quoting[qLen-1]==jsonStr[i]):
                quoting.pop()
                qLen-=1
            elif(qLen>1 and quoting[qLen-2]==jsonStr[i]):
                quoting.pop()
                quoting.pop()
                qLen-=2
            else:
                quoting.append(jsonStr[i])
                qLen+=1
        if(qLen==0):
            if(jsonStr[i]=="{"):
                mLen+=1
                maps.append({})
                islist.append(False)
                tmpValue=""
                keyInputing=True
            elif(jsonStr[i]=="["):
                mLen+=1
                maps.append([])
                islist.append(True)
                tmpValue=""
                keyInputing=True
            elif(jsonStr[i]=="}"):
                if(tmpValue!="" and mLen>0):#store the lastKey when , not appeared
                    #print(keys)
                    maps[mLen-1][keys.pop()]=translate(tmpValue)
                    kLen-=1
                tmpValue=maps.pop()
                islist.pop()
                #kLen-=1
                mLen-=1
            elif(jsonStr[i]=="]"):
                if(tmpValue!="" and mLen>0):#store the lastKey when , not appeared
                    maps[mLen-1].append(translate(tmpValue))
                tmpValue=maps.pop()
                islist.pop()
                #kLen-=1
                mLen-=1
            elif(jsonStr[i]==","):
                if(islist[mLen-1]):
                    maps[mLen-1].append(translate(tmpValue))
                else:
                    maps[mLen-1][keys.pop()] = translate(tmpValue)
                    kLen-=1
                tmpValue=""
                keyInputing=True
            elif(keyInputing and jsonStr[i]==":"):
                    keys.append(translate(tmpValue))
                    kLen+=1
                    keyInputing=False
                    tmpValue=""
            elif(jsonStr[i]!=" " and jsonStr[i]!="\t" and jsonStr[i]!="\n"):
                #print(tmpValue,i)
                tmpValue+=jsonStr[i]
        else:
            tmpValue+=jsonStr[i]
        i+=1
    return tmpValue
def stringify(dict__):
    return str(dict__)