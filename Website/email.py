# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart      


def sendMail(msg,to_list):
	#
    sender = 'm18630585565_1@163.com'
    subject = '最低点差追踪'

    # 创建邮箱
    em = MIMEMultipart()
    em['subject'] = subject
    em['From'] = sender
    em['To'] = ",".join(to_list)

    # 邮件的内容
    content = MIMEText(msg)
    em.attach(content)

    # 发送邮件
    # 1、连接服务器
    print("开始连接服务器")

    #21端口已经被云服务器商关闭了，所以只能用465端口了
    smtp=smtplib.SMTP_SSL('smtp.163.com',465)

    print("连接服务器成功")
    # 2、登录
    print("开始登录服务器")
    smtp.login(sender, 'UAJSWJOOKEVIVYYX')
    print("登录服务器成功")
    # 3、发邮件
    print("开始发送邮件")
    smtp.send_message(em)
    print("发送邮件成功")
    # 4、关闭连接
    smtp.close()
    
if __name__ == '__main__':
    sendMail('11','1979450016@qq.com')
    
    
    import sqlite3

    with sqlite3.connect("db/users.db") as conn:
        cur = conn.cursor()
        cur.execute("""
            select * from users;
            """)
    
        users = cur.fetchall()
        emails = list(set([user[2] for user in users]))
    
