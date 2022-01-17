import pickle as pkl

# Load TBBT
train = pkl.load(open('all_train.pkl', 'rb'))
dev = pkl.load(open('all_dev.pkl', 'rb'))
test = pkl.load(open('all_test.pkl', 'rb'))


data = []
# Read Data
with open('os_all.txt', 'r', encoding='utf-8') as f:
    temp = []
    for x in f:
        if x == '\n':
            data.append(temp)
            temp = []
        else:
            temp.append(x.strip())

# Sliding windows
final = []
for item in data:
    for i, x in enumerate(item):
        if i < 4:
            continue
        temp = {
            'context': [item[i-3], item[i-2]],
            'target': item[i-1],
            'feedback': item[i],
            'target_emotion': 'neutral',
            'context_emotion_sent': item[i]
        }
        final.append(temp)

for x in final:
    train.append(x)

for x in final[:100]:
    dev.append(x)

print(len(train))
print(len(dev))
print(len(test))

# pkl.dump(train[:15000], open('tbbt_os_train.pkl', 'wb'))
pkl.dump(dev, open('tbbt_os_dev.pkl', 'wb'))
# pkl.dump(test, open('tbbt_os_test.pkl', 'wb'))










