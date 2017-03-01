__author__ = 'peterking'

import random

target = random.randint(0, 50)

i = 0
a = []
while i <= 20:
    a.append(random.randint(0, 50))
    i += 1

i = 0
b = []
while i <= 20:
    b.append(random.randint(0, 50))
    i += 1

c = [(x, y) for x in a for y in b if x + y == target]

print(target)
if len(c) == 0:
    print("List is empty.")
else:
    for item in c:
        print(item)