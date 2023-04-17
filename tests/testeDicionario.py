from collections import OrderedDict


class Xuxu():
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "xuxuuu" + self.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, id):
        return self.id == id

    # Semelhante ao __str__, é usado para retornar uma representação em string do objeto
    # O metodo str em um print(Xuxu()) sobrescreverá o __repr__
    def __repr__(self) -> str: 
        return f"id:{self.id}"


d = OrderedDict()
d[Xuxu('1')] = 'A'
d[Xuxu('2')] = 'B'
print('1' in d)
print(2 in d)  # no metodo eq é verificado se existe o casamento entre valores hash, ou seja, se seu valor e seu tipo são iguais!
print(3 in d)

print('\n')
print(d['1'])
print(d['2'])
print('\n')

# --------------------
print(d)
print(Xuxu('5'))
print(d.keys())
print(d.items())
print(d.get('A'))
print(str(Xuxu('1')))


listTeste = [1,2,3,6,5,8,9]
print(listTeste[-1])
