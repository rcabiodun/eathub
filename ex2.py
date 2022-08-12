class Human:
    def say(self):
        print("How are you")
    
    def do(self):
        print("I'm fine")
        self.say()
    
    population = 0
    def __init__(self,name):
        self.name = name
        ++Human.population
        Human.incpopulation()
    @classmethod
    def incpopulation(cls):
        cls.population += 1

class mammal:
    def say(self):
        print("How are you")
    
    def do(self):
        print("I'm fine")
        self.say()
    
    population = 0
    def __init__(self,my_type):
        self.type = my_type
        ++Human.population
        Human.incpopulation()
    @classmethod
    def incpopulation(cls):
        cls.population += 1


class Man(Human,mammal):
    def __init__(self, name,height,my_type):
        self.height=height
        mammal.__init__(self,my_type)
        Human.__init__(self,name)


m = Man("Hassan","2'2","mammal")

print(m.type)



