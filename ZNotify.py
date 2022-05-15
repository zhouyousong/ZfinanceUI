
import smtplib
from email.mime.text import MIMEText

#构建HTML整体结构
def html_goujian(html_body):
    html_top = '''<html>
    <head>
        <title>HTML Pandas Dataframe with CSS</title>
    </head>
    <link rel="stylesheet" type="text/css" href="df_style.css" />
    <style type="text/css">
        .mystyle {
            font-size: 11pt;
            font-family: Arial;
            border-collapse: collapse;
            border: 1px solid silver;
        }

        .mystyle td,
        th {
            padding: 5px;
        }

        .mystyle tr:nth-child(even) {
            background: #E0E0E0;
        }

        .mystyle tr:hover {
            background: silver;
            cursor: pointer;
        }
    </style>

    <body>'''

    html_tail ='''</body></html>'''
    html = html_top+html_body+html_tail
    return html

#发送邮件
def send_email(SendAddr,SendPwd,RevAddr,subject, html_body):
    html_string=html_goujian(html_body)
    msg_from = SendAddr  # 发送方邮箱
    passwd = SendPwd  # 填入发送方邮箱的授权码

    msg_to = RevAddr
    msg = MIMEText(html_string, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.163.com", 465)  # 邮件服务器及端口号
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        return "Successed"
    except:
        return "Failed"



