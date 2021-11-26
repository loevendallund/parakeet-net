import json

ran = 100

r = []
rm = [1]
wp = []
count = 0

for i in range(ran):
    r.append(i + 1)
    if count == 10 and i < ran-5:
        wp.append(i + 1)
        count = 0
    count = count + 1

i = 0
while i < ran-2:
    i = i + 2
    rm.append(i + 1)
    rm.append(i)
rm.append(ran)

print(r)
print(rm)
print(wp)
print(len(wp))

data = {}
data['waypoints'] = wp
data['source'] = 0
data['target'] = ran
data['r'] = r
data['rm'] = rm

filename = "ladder" + str(ran)
with open(f"{filename}.json", "w") as out:
    print(f"{filename}.json")
    json.dump(data, out)
