import  re

x1=re.compile('[0-9]*.txt')

t1='23.txt'
t2='hello.txt'
print(bool(re.match(x1,t1)))
print(bool(re.match(x1,t2)))