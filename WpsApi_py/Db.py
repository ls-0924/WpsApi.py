from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库配置（请根据实际情况修改）
DB_URI = 'mysql+pymysql://root:LSHL135a%40%2F@127.0.0.1:3306/easylaw?charset=utf8mb4'

# 创建基类
Base = declarative_base()

# 定义用户模型（假设表名为 user）
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    phone = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)

def login(phone: str, password: str) -> bool:
    """
    登录验证函数
    :param username: 用户名
    :param password: 密码（建议使用哈希存储，此处假设为明文）
    :return: 验证结果
    """
    try:
        # 创建数据库引擎
        engine = create_engine(DB_URI)
        Session = sessionmaker(bind=engine)
        session = Session()

        # 查询用户
        user = session.query(User).filter_by(phone=phone).first()

        if user and user.password == password:
            print("登录成功！")
            return True
        else:
            print("用户名或密码错误！")
            return False

    except Exception as e:
        print(f"数据库错误：{e}")
        return False

    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    # 示例：模拟用户输入
    phone = input("请输入手机号：")
    password = input("请输入密码：")

    # 执行登录验证
    login_result = login(phone, password)
    print(f"登录结果：{login_result}")