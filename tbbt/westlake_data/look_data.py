import pickle as pkl

data = pkl.load(open('tbbt_os_dev.pkl', 'rb'))
print("TBBT")
for x in data[:5]:
    for item in x:
        print(item, x[item])
    print('=='*50)

# print("OS")
# for x in data[-5:]:
#     for item in x:
#         print(item, x[item])
#     print('=='*50)
