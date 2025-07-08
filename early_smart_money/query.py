import sqlite3

def print_common_values(db_path, table1, table2, column):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 使用 INTERSECT 查询两个表共有的值
    query = f"SELECT {column} FROM {table1} INTERSECT SELECT {column} FROM {table2}"
    cursor.execute(query)
    
    # 打印所有共同值
    results = cursor.fetchall()
    for row in results:
        print(row[0])
    
    conn.close()

# TODO 输出序号，加入总数
# 使用示例
print_common_values('../DNF.db', 'GOONC', 'KLED', 'Signer')
