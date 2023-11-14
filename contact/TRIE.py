from queue import Queue
class TrieNode(object):
    def __init__(self,value=None,isEnded=False):
        self.childNodes={}
        self.value = value
        self.isEnded=isEnded
        self.failPointer=None
        self.key=''
    def child(self,value):
        return self.childNodes.get(value,None)
def buildTrie(root_:TrieNode,words:list):
    tmp=None
    def addWord(word:str):
        root = root_
        for i in word:
            tmp = root.child(i)
            if not tmp:
                tmp = TrieNode(i)
                root.childNodes[i]=tmp
            root = tmp
        root.key=word
        root.isEnded=True
    for word in words:
        addWord(word)
    return root_
def buildFailPointers(root:TrieNode):
    #bfs build pointer
    q = Queue()
    q.put(root)
    while(not q.empty()):
        node:TrieNode = q.get()
        child=None
        for key in node.childNodes:
            child=node.childNodes[key]
            failParent:TrieNode = node.failPointer
            failChild=None
            if(failParent!=None):
                failChild = failParent.child(key)#find the child with same key as my child
                # not root
            while(failParent!=None and not failChild):
                failParent = failParent.failPointer
                if failParent==None:
                    break
                failChild = failParent.child(key)
            #failure trace back to root node
            if(failParent==None):
                child.failPointer=root
            else:
                child.failPointer = failChild
            q.put(child)
    return root
                    
def search(search, root):#check user fuzzy multi-word search
    node:TrieNode  = root
    for i,c in enumerate(search):
        while node and not node.child(c):
            node = node.failPointer
        if not node:
            node = root
            continue
        node = node.child(c)
        out = node
        while out:
            if out.isEnded:
                return True
            out = out.failPointer
    return False