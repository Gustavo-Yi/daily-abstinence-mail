# daily-abstinence-mail

每天北京时间 10:00 通过 GitHub Actions 发送一封“中国传统优良文化”戒色知识邮件。

## Secrets

仓库需要配置这些 GitHub Actions Secrets：

- `QQ_MAIL_USER`：发件 QQ 邮箱
- `QQ_MAIL_AUTH_CODE`：QQ 邮箱 SMTP 授权码
- `QQ_MAIL_TO`：收件邮箱

授权码不要写进代码、提交记录或 README。
