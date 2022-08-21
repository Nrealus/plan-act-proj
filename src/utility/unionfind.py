import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

############################################

class UnionFind2:

    def __init__(self):
        self.parent_node = {}
        self.rank = {}
        # custom : to easily store and access connected component of an element,
        # without iterating on all elements and using find on them
        self.adjacency_storage = {}

    def make_set(self, u):

        for i in u:
            if i in self.adjacency_storage:
                self.adjacency_storage[self.find(i)].discard(i)
                self.adjacency_storage[i].clear()
                self.adjacency_storage[i].add(i)
            else:
                self.adjacency_storage[i] = set([i])
            self.parent_node[i] = i
            self.rank[i] = 0

    def contains(self, u):

        r = True
        for i in u:
            #r = r and (u in self.parent_node)
            if not i in self.parent_node:
                return False
        #return r
        return True

    def find(self, k):

        if self.parent_node[k] != k:
            self.parent_node[k] = self.find(self.parent_node[k])
        return self.parent_node[k]

    def union(self, a, b):

        x = self.find(a)
        y = self.find(b)

        if x == y:
            return
        if self.rank[x] > self.rank[y]:
            self.parent_node[y] = x
            self.adjacency_storage[x].update(self.adjacency_storage[y])
        elif self.rank[x] < self.rank[y]:
            self.parent_node[x] = y
            self.adjacency_storage[y].update(self.adjacency_storage[x])
        else:
            self.parent_node[x] = y
            self.adjacency_storage[y].update(self.adjacency_storage[x])
            self.rank[y] = self.rank[y] + 1

    def add_and_union(self, a, b):

        if not self.contains([a]):
            self.make_set([a])
        if not self.contains([b]):
            self.make_set([b])
        self.union(a,b)

    def connected_component(self, a):

        r = self.find(a)
        return self.adjacency_storage[r]

    #def display(self.u):
    #    print([self.find(i) for i in u])

############################################

class UnionFind1:

    def __init__(self):
        self.parent_node = {}
        self.rank = {}
        self.elements = set()

    def make_set(self, u):

        for i in u:
            self.parent_node[i] = i
            self.rank[i] = 0
            self.elements.add(i)

    def find(self, k):
        
        if self.parent_node[k] != k:
            self.parent_node[k] = self.find(self.parent_node[k])
        return self.parent_node[k]

    def union(self, a, b):
        x = self.find(a)
        y = self.find(b)

        if x == y:
            return
        if self.rank[x] > self.rank[y]:
            self.parent_node[y] = x
        elif self.rank[x] < self.rank[y]:
            self.parent_node[x] = y
        else:
            self.parent_node[x] = y
            self.rank[y] = self.rank[y] + 1

    def connected_component(self, a):
        r = self.find(a)
        res = set()
        for i in self.elements:
            if self.find(i) == r:
                res.add(i)
        return res
