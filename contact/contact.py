import JSON
import re
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
        self.searchList = [self.CATEGORYDIR,self.NUMBERDIR,self.EMAILDIR]
        self.searchWords = ["categories","number","email"]
        for people in self.contacts:
            fuzzyStr = people
            people=self.contacts[people]
            for i in range(len(self.searchList)):
                for num in people[self.searchWords[i]]:
                    tmp=self.searchList[i].get(num)
                    if(not tmp):
                        tmp=self.searchList[i][num]={}
                    tmp[people["name"]]=True
                    fuzzyStr+=num+chr(0)
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
    def fuzzySearch(self,search:str):
        search=search.lower()
        for name in self.PEOPLEFUZZY:
            if(search in self.PEOPLEFUZZY[name]):
                self.showOnePeople(name)
    def showOnePeople(self,people:str):
        print("Name:",self.contacts[people]["name"])
        print("Phone Number:",*self.contacts[people]["number"])
        print("Email:",*self.contacts[people]["email"])
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
    def addPerson(self,name:str,mode:str,newDatas:list = []):
        def defaultMode():
            self.contacts[name]={
                "name":name,
                "number":[],
                "email":[],
                "categories":[]
            }
        if(mode=="cover"):
            if name in self.contacts:
                self.removeAllPersonReversedList(name)
            defaultMode()
        elif(mode=="blend"):
            if(not name in self.contacts):
                defaultMode()
        else:
            return
        self.contacts[name]["categories"].append("{{Everyone")
        self.addPersonToType(name,"{{Everyone",self.CATEGORYDIR) #Everyone is everyone
        for i in range(len(self.searchList)):
            for data in newDatas[i]:
                self.contacts[name][self.searchWords[i]].append(data)
                self.addPersonToType(name,data,self.searchList[i])
            self.contacts[name][self.searchWords[i]] = list(set(self.contacts[name][self.searchWords[i]]))#UNIQUE

    def save(self):
        handle = open(self.filePath,"w")
        handle.write(JSON.stringify(self.contacts))
        handle.close()
class Console:
    def __init__(self):
        self.con = Contact("test.contact")
        self.waitForInput()
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
        #   -Y silence cover mode
        #  For F:
        #   -q search words
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
            for t in types:
                if(t[0]=="-p"):
                    create[0] = t[1]
                elif(t[0]=="-e"):
                    create[1] = t[1]
                elif(t[0]=="-c"):
                    create[2] = t[1]
                elif(t[0]=="-y"):
                    silence = True
                elif(t[0]=="-Y"):
                    silence = True
                    cover=True
                elif(t[0]=="-n" and len(t[1])>0):
                    name = t[1][0]
            #check some values
            if(name==None):
                if(not silence):
                    while(name==None or len(name)==0):
                        name = input("Enter Name >>> ")
                else:
                    print("Name Invalid")
                    return
            if(not silence and self.con.contacts.get(name) and not cover):
                print("Already exists, cover? (Y/N)")
                if(self.con.getUserInput()):
                    cover=True
            for i in range(3):
                if(create[i]==None):
                    create[i]=[]
                    if(not silence):
                        while(True):
                            pNumber = input(["Number(s) (Press Enter To End): ","Email(s) (Press Enter To End): ","Categories (Press Enter To End): "][i])
                            if(i==0 and not re.match("[0-9]+",pNumber)):
                                break
                            elif(i==1 and not re.match("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",pNumber)):
                                break
                            elif(i==2 and pNumber==""):
                                break
                            create[i].append(pNumber)

                create[i] = list(set(create[i]))#UNIQUE
            #here is a struture design failure, sort from number email category to category number email
            tmp = create[0]
            create[0]=create[2]
            create[2]=create[1]
            create[1]=tmp
            if(cover):
                cover="cover"
            else:
                cover="blend"
            self.con.addPerson(name,cover,create)
        elif(mode == "F"):
            searchWords = None
            if(len(types)>0 and types[0][0]=="-q"):
                searchWords=types[0][1][0]
            else:
                searchWords = curDataInput
            #print(searchWords)
            self.con.fuzzySearch(searchWords)
        else:
            return False
        return True

                        
                    

con = Console()