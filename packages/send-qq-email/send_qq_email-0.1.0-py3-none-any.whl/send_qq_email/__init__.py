# server.py
from mcp.server.fastmcp import FastMCP
import smtplib
from email.message import EmailMessage

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def sum(receiver: str, content: str, title: str) -> str:
    """帮发件人给收件人发送邮件"""
    sender = "3485135655@qq.com"
    receiver = receiver
    smtp_server = "smtp.qq.com"  
    password = "zchqzmkeljjwcijj"  
    smtp_port = 587
    msg = EmailMessage()
    msg["Subject"] = title
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(content)

    # 发送邮件
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # 启用TLS加密（端口587时）
            server.login(sender, password)
            server.send_message(msg)
        return "邮件发送成功！"
    except Exception as e:
        return (f"发送失败: {e}")


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def main() -> None:
    mcp.run(transport="stdio")
