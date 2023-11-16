import JSON
import re
import TRIE
def flatten(deepDict):
    flattened = []
    for key,val in enumerate(deepDict):
        if(type(val)==list or type(val)==dict):
            flattened+=flatten(val)
        elif type(deepDict)==dict:
            flattened.append(deepDict[val])
        else:
            flattened.append(val)
    return flattened
def deep_copy(deepDict):
    dictType = type(deepDict)==dict
    newDict = None
    if(dictType):
        newDict = {}
    else:
        newDict = []
    for sth in deepDict:
        if(dictType):
            if(type(deepDict[sth]) == list or type(deepDict[sth]) == dict):
                newDict[sth]=deep_copy(deepDict[sth])
            else:
                newDict[sth]=deepDict[sth]
        else:
            if(type(sth) == list or type(sth) == dict):
                newDict.append(deep_copy(sth))
            else:
                newDict.append(sth)
    return newDict
class Contact:
    def __init__(self,path:str):
        self.CATEGORYDIR = {}
        self.NUMBERDIR = {}
        self.EMAILDIR = {}
        self.PEOPLEFUZZY = {}
        try:
            handle = open(path,"r")
            self.contacts=JSON.parse(handle.read())
            handle.close()
        except FileNotFoundError:
            self.contacts = {}
        self.filePath = path
        tmp = None
        self.searchList = [self.NUMBERDIR,self.EMAILDIR]
        self.searchWords = ["number","email"]
        #create reversed dictionary, initialize fuzzyStr and link referenceKey
        for people in self.contacts:
            fuzzyStr = people
            people=self.contacts[people]
            for i in range(len(self.searchList)):
                for num in people[self.searchWords[i]]:
                    tmp=self.searchList[i].get(num)
                    if(not tmp):
                        tmp=self.searchList[i][num]={}
                    tmp[people["name"]]=True
                    fuzzyStr+=chr(0)+num
            
            for key in people["tags"]:
                for num in people["tags"][key]:
                    tmp=self.CATEGORYDIR.get(num)
                    if(not tmp):
                        tmp=self.CATEGORYDIR[num]={}
                    tmp[people["name"]]=True
                    fuzzyStr+=chr(0)+num

            self.PEOPLEFUZZY[people["name"]]=fuzzyStr.lower()
    def getUserInput(self):
        inputN = 0
        while(inputN<3):
            sth=input("Y/N >>> ")
            if(sth=="y" or sth=="Y"):
                return True
            elif(sth=="n" or sth=="N"):
                return False
        return False
    def listAllContact(self):
        print(self.contacts)
        print(self.searchList)
        print(self.PEOPLEFUZZY)
    def fuzzySearch(self,search:str|list):
        def doingSomethingWhenSearched(name):
            self.showOnePeople(name)
        if (type(search)==type([])):
            root = TRIE.TrieNode()
            TRIE.buildTrie(root,search)
            TRIE.buildFailPointers(root)
            for name in self.PEOPLEFUZZY:
                if(TRIE.search(self.PEOPLEFUZZY[name],root)):
                    doingSomethingWhenSearched(name)
        else:
            search=search.lower()
            for name in self.PEOPLEFUZZY:
                if(search in self.PEOPLEFUZZY[name]):
                    doingSomethingWhenSearched(name)
    def showOnePeople(self,people:str):
        print("Name:",self.contacts[people]["name"])
        print("Phone Number:",*self.contacts[people]["number"])
        print("Email:",*self.contacts[people]["email"])
        for key in self.contacts[people]["tags"]:
            if(key[:2]=="{{"):
                continue
            print(key+":",*self.contacts[people]["tags"][key])
        print()
    def showContacts(self,filter:dict,exclude:bool=False):
        willShow = set()
        for cate in self.CATEGORYDIR:
            if(not (exclude^(not not filter.get(cate)))):
                continue
            for people in self.CATEGORYDIR[cate]:
                willShow.add(people)
        for people in willShow:
            self.showOnePeople(people)
        return
    def addInformationType(self,t_type:str,dictionary:dict):
        if(dictionary.get(t_type)):
            return
        dictionary[t_type]={}
    def addPersonToType(self,name:str,t_type:str,dictionary:dict):
        self.addInformationType(t_type,dictionary)
        dictionary[t_type][name]=True
        return
    def removeAllPersonReversedList(self,name:str):
        for i in range(len(self.searchList)):
            for cate in self.contacts[name][self.searchWords[i]]:
                del self.searchList[i][cate][name]
                if(len(self.searchList[i][cate])==0):
                    del self.searchList[i][cate]
            self.contacts[name][self.searchWords[i]]=[]
        for tag in self.contacts[name]["tags"]:
            for cate in self.contacts[name]["tags"][tag]:
                del self.CATEGORYDIR[cate][name]
                if(len(self.CATEGORYDIR[cate])==0):
                    del self.CATEGORYDIR[cate]
            self.contacts[name]["tags"][tag]=[]
    def deletePerson(self,name:str):
        tmp = self.contacts.get(name)
        if(not tmp):
            return
        self.removeAllPersonReversedList(name)
        del self.contacts[name]#here we cant use tmp because tmp is going to return
        return tmp
    def addPerson(self,name:str,mode:str,newDatas:list = []):
        def defaultMode():
            self.contacts[name]={
                "name":name,
                "number":[],
                "email":[],
                "tags":{}
            }
        if(mode=="cover" or mode=="update"):
            if(mode == "update"):
                words = self.searchWords+["tags"]
                for i in range(len(newDatas)):
                    if(newDatas[i]==None or len(newDatas[i])==0):
                        newDatas[i]=self.contacts[name][words[i]]
            if name in self.contacts:
                self.removeAllPersonReversedList(name)
            defaultMode()
        elif(mode=="blend"):
            if(not name in self.contacts):
                defaultMode()
        else:
            return True
        self.contacts[name]["tags"]["{{systemDefault"] = self.contacts[name]["tags"].get("{{systemDefault",[]);
        self.contacts[name]["tags"]["{{systemDefault"].append("{{Everyone")
        self.addPersonToType(name,"{{Everyone",self.CATEGORYDIR) #Everyone is everyone
        fuzzyStr = name
        if self.PEOPLEFUZZY.get(name) and (mode == "blend"):
            fuzzyStr=""
        else:
            self.PEOPLEFUZZY[name]=""
        for i in range(len(self.searchList)):
            for data in newDatas[i]:
                self.contacts[name][self.searchWords[i]].append(data)
                self.addPersonToType(name,data,self.searchList[i])
                fuzzyStr+=chr(0)+str(data)
            self.contacts[name][self.searchWords[i]] = list(set(self.contacts[name][self.searchWords[i]]))#UNIQUE
        if(type(newDatas[2])==dict):
            tags = self.contacts[name]["tags"]
            for key in newDatas[2]:
                if(not tags.get(key)):
                    tags[key]=[]
                for data in newDatas[2][key]:
                    tags[key].append(data)
                    self.addPersonToType(name,data,self.CATEGORYDIR)
                    fuzzyStr+=chr(0)+str(data)
                tags[key] = list(set(tags[key]))
        #add full fuzzyStr to oriFUZZYSTR
        self.PEOPLEFUZZY[name]+=fuzzyStr.lower()

    def save(self):
        handle = open(self.filePath,"w")
        handle.write(JSON.stringify(self.contacts))
        handle.close()
class Console:
    def __init__(self,path:str):
        self.con = Contact(path)
    def waitForInput(self):
        res=True
        try:
            while(res):
                command = input("CONTACT >>> ")
                res=self.exec(command)
        except KeyboardInterrupt:
            print("\n\nSAVING&QUITTING...")
            self.con.save()
        else:
            print("\n\nSAVING&QUITTING...")
            self.con.save()
    def exec(self,command:str):
        if(command[-1]!=" "):
            command+=" "
        strLen = len(command)
        if(strLen==0):
            return
        quoting=[]#space in quote doesnt split
        qLen = 0
        #modes:
        #   L: List
        #   A: Add
        mode = command[0]
        types = []
        curDataInput = ""
        #commands:
        #  For L:
        #   -f only-filter-category   example:-f category,category...
        #   -fe exclude-filtered-category
        #  For A:
        #   -n name
        #   -p numbers,numbers,...
        #   -c category,category...
        #   -e emails,emails
        #   -y silence mode
        #   -mode b/c/u (blend/cover/update)
        #  For F:
        #   -q search words
        #  For M
        #   -<n/p/e/c> data -o modify
        #  For D
        tmpValue = ""
        ind = 1
        while(ind<strLen):
            if(command[ind]=="\"" or command[ind]=="'"):
                # type of quote marks:
                #    "''"
                #    "'"
                if(qLen>0 and quoting[qLen-1]==command[ind]):
                    quoting.pop()
                    qLen-=1
                elif(qLen>1 and quoting[qLen-2]==command[ind]):
                    quoting.pop()
                    quoting.pop()
                    qLen-=2
                else:
                    quoting.append(command[ind])
                    qLen+=1
                if(qLen==0 and len(tmpValue)>0 and (tmpValue[0]=="\"" or tmpValue[0]=="'")):
                    tmpValue = tmpValue[1:-1]
            if(qLen==0):
                if(command[ind]==" " or command[ind]==","):
                    if(len(tmpValue)>0):
                        if(tmpValue[0]=="-"):
                            types.append([tmpValue,[]])
                        else:
                            if(len(types)>0):
                                types[-1][1].append(tmpValue)
                            else:
                                curDataInput = tmpValue
                        tmpValue=""
                else:
                    tmpValue+=command[ind]
            else:
                tmpValue+=command[ind]
            ind+=1
        if(mode=="L"):
            lst={}
            if(len(types)>0):
                for t in types[0][1]:
                    lst[t]=True
                self.con.showContacts(lst,types[0][0]=="-fe")
            else:
                self.con.showContacts(lst,True)
        elif(mode=="A"):
            name = None
            create = [None,None,None]
            silence = False
            cover = False
            update = False
            for t in types:
                if(t[0]=="-p"):
                    create[0] = t[1]
                elif(t[0]=="-e"):
                    create[1] = t[1]
                elif(t[0]=="-c"):
                    create[2] = {"{{systemDefault":t[1]}
                elif(t[0]=="-y"):
                    silence = True
                elif(t[0]=="-n" and len(t[1])>0):
                    name = t[1][0]
                elif(t[0]=="-mode" and len(t[1])>0):
                    if(t[1][0]!="b"):
                        cover=True
                    if(t[1][0]=="u"):
                        update=True
            #check some values
            if(name==None):
                if(not silence):
                    while(name==None or len(name)==0):
                        name = input("Enter Name >>> ")
                else:
                    print("Name Invalid")
                    return True
            if(not self.con.contacts.get(name) and update):
                print("User does not exists.")
                return True
            if(not silence and self.con.contacts.get(name) and not cover):
                print("Already exists, cover? (Y/N)")
                if(self.con.getUserInput()):
                    cover=True
            #enter phoneNumber and others
            for i in range(0,2):
                if(create[i]==None):
                    create[i]=[]
                    if(not silence):
                        while(True):
                            pNumber = input(["Number(s) (Press Enter To End): ","Email(s) (Press Enter To End): "][i])
                            if(i==0 and not re.match("^[0-9]*$",pNumber)):
                                break
                            elif(i==1 and not re.match("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",pNumber)):
                                break
                            create[i].append(pNumber)

                create[i] = list(set(create[i]))#UNIQUE
            #enter Custom Fields & Categories
            if(create[2]==None):
                create[2]={}
                if(not silence):
                    while(True):
                        pField = input("Custom Field (Press Enter To End): ")
                        pVal = input("Categories (Press Enter To End): ")
                        if(len(pVal)==0):
                            break
                        if(pField[:2]=="{{"):
                            pField=pField[2:]
                        if(len(pField)==0):
                            pField="{{systemDefault"
                        create[2][pField] = create[2].get(pField,[])
                        create[2][pField].append(pVal)
            if(cover):
                if(update):
                    cover="update"
                else:
                    cover="cover"
            else:
                cover="blend"
            self.con.addPerson(name,cover,create)
        elif(mode == "F"):
            searchWords = None
            if(len(types)>0 and types[0][0]=="-q"):
                searchWords=types[0][1]
                ind_tmp = len(searchWords)-1
                while(ind_tmp>=0):
                    searchWords[ind_tmp] = searchWords[ind_tmp].lower()
                    ind_tmp-=1
            else:
                searchWords = curDataInput
            #print(searchWords)
            self.con.fuzzySearch(searchWords)
        elif(mode == "M"):
            moded = {}
            lastCommand = "-n"
            name = ""
            phone = None#modify only one phone number
            email = None#modify only one email number
            oriInformation:dict = None
            modTag = None
            modTagOnce = None#mod a tag's which category
            for t in types:
                if(t[0]=="-o" and len(t[1])>0):
                    moded[lastCommand] = t[1]
                elif(t[0]=="-n" and len(t[1])>0):
                    lastCommand=t[0]
                    name = t[1][0]
                elif((t[0]=="-p" or t[0]=="-e")):
                    lastCommand=t[0]
                    if(len(t[1])>0):
                        if(t[0]=="-p"):
                            phone=t[1][0]
                        else:
                            email=t[1][0]
                elif(t[0]=="-c" and len(t[1])>0):
                    lastCommand=t[0]
                    modTag = t[1][0]
                    if(len(t[1])>1):
                        modTagOnce = t[1][1]
            if(len(name)==0 or not self.con.contacts.get(name)):
                return True
            else:
                def basicIndex(lst,val):
                    l = len(lst)
                    i_ = 0
                    while(i_<l):
                        if lst[i_] == val:
                            return i_
                        i_+=1
                    return None
                #create a copy to avoid change to originalData
                oriInformation = deep_copy(self.con.contacts.get(name))
                if(moded.get("-n")):
                    name=moded["-n"][0]
                if(moded.get("-p")):
                    if(phone):
                        pos = basicIndex(oriInformation["number"],phone)
                        if(pos):
                            oriInformation["number"][pos]=moded["-p"][0]
                    else:
                        oriInformation["number"]=moded["-p"]
                if(moded.get("-e")):
                    if(email):
                        pos = basicIndex(oriInformation["email"],email)
                        if(pos):
                            oriInformation["email"][pos]=moded["-e"][0]
                    else:
                        oriInformation["email"]=moded["-e"]
                if(moded.get("-c")):
                    if(modTagOnce):
                        pos = basicIndex(oriInformation["tags"][modTag],modTagOnce)
                        if(pos):
                            oriInformation["tags"][modTag][pos]=moded["-c"][0]
                    else:
                        oriInformation["tags"][modTag] = moded["-c"]
                for number in oriInformation["number"]:
                    if(not re.match("^[0-9]*$",number)):
                        print("Invalid phone number modification")
                        return True
                for email in oriInformation["email"]:
                    if(not re.match("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",email)):
                        print("Invalid email modification")
                        return True
                self.con.deletePerson(oriInformation["name"])
                self.con.addPerson(name,"cover",[oriInformation["number"],oriInformation["email"],oriInformation["tags"]])
        elif(mode=="D"):
            if(len(curDataInput)==0):
                return True
            self.con.deletePerson(curDataInput)
        else:
            return False
        return True

con = Console("test.contact")
con.waitForInput()