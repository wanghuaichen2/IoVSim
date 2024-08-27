import pandas as pd

# 读取 CSV 文件
file_path = 'CallGraph_480.csv'
df = pd.read_csv(file_path)

# 筛选 service 为 'S_156482560' 的记录
filtered_df = df
# filtered_df = df[df['service'] == 'S_156482560']

# 删除除了 timestamp 外每列元素值都相同的重复记录
filtered_df = filtered_df.drop_duplicates(subset=filtered_df.columns.difference(['timestamp']))

# 按 traceid 分组
grouped = filtered_df.groupby('traceid')

# 定义函数以过滤重复的 um 和 dm 对
def filter_duplicates(group):
    return group.drop_duplicates(subset=['um', 'dm'])

# 对每个分组应用该函数
filtered_groups = grouped.apply(filter_duplicates).reset_index(drop=True)

# 统计每个分组的出现次数
group_counts = filtered_groups['traceid'].value_counts()

# 查找重复的组
unique_groups = []
duplicate_groups = []

for traceid, group in grouped:
    group_key = tuple(group[['um', 'dm']].sort_values(by=['um', 'dm']).itertuples(index=False, name=None))
    if group_key in unique_groups:
        duplicate_groups.append(traceid)
    else:
        unique_groups.append(group_key)

# 统计并打印重复组的数量
print(f"Number of duplicate groups: {len(duplicate_groups)}")

# 删除重复的组
final_df = filtered_groups[~filtered_groups['traceid'].isin(duplicate_groups)]

# 保存结果到新的 CSV 文件
output_path = 'filtered_call_graph.csv'
final_df.to_csv(output_path, index=False)

print(f"Filtered data has been saved to {output_path}")
