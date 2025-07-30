import os
from dotenv import load_dotenv
from lingua_sql import LinguaSQL

# 加载环境变量
load_dotenv()

try:
    # 初始化 lingua_sql，使用持久化存储
    nl = LinguaSQL(config={
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "deepseek-chat",
        "client": "persistent"
    })

    # 从数据库导入所有表的 DDL
    print("正在从数据库导入表结构...")
    if nl.import_database_schema():
        print("数据库表结构导入成功！")
    else:
        print("数据库表结构导入失败！")
        exit(1)

    # # 训练示例问题和 SQL
    # nl.train(
    #     question="学号为2023213203的学生的姓名为多少？",
    #     sql="SELECT xm FROM t_aixl_bksjbxx WHERE xh = '2023213203';"
    # )

    print("训练完成！")

    # 测试查询
    question = "统一认证码为1688438的学生的性别为多少？"
    print(f"\n问题: {question}")
    results = nl.ask(question)
    
    if results:
        print("\n查询结果:")
        for row in results:
            print(row)
    else:
        print("\n未找到结果")

except Exception as e:
    print(f"发生错误: {e}") 