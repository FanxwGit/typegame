import pandas as pd

# 读取Excel文件
data = pd.read_excel('/home/fxw/workspace/typegame/words.xlsx', header=None)

# 过滤第二列大于10的数据
filtered_data = data[data.iloc[:, 1] > 1]

# print(filtered_data[:10])

file = open("test.txt", "w")
for index, row in filtered_data.iterrows():
    file.write(f"{row[0]}\t{''.join(row[2].strip().split("\n"))}\n")