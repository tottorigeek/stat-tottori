import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """メール送信サービスクラス"""
    
    def __init__(self):
        self.smtp_server = settings.MAIL_SERVER
        self.smtp_port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.use_tls = settings.MAIL_USE_TLS
        self.from_email = settings.MAIL_FROM
    
    def _create_smtp_connection(self):
        """SMTP接続作成"""
        if not self.smtp_server:
            raise ValueError("メールサーバーが設定されていません")
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            if self.username and self.password:
                server.login(self.username, self.password)
            
            return server
            
        except Exception as e:
            logger.error(f"SMTP接続エラー: {e}")
            raise
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """メール送信"""
        
        if not self.smtp_server:
            logger.warning("メールサーバーが設定されていないため、メール送信をスキップします")
            return False
        
        try:
            # メッセージ作成
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # テキスト部分
            if text_content:
                text_part = MimeText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # HTML部分
            html_part = MimeText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # メール送信
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"メール送信成功: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"メール送信エラー ({to_email}): {e}")
            return False

# EmailServiceインスタンス
email_service = EmailService()

def send_verification_email(email: str, token: str, username: str) -> bool:
    """メール認証用メール送信"""
    
    subject = "【すたっととっとり】メール認証のお願い"
    
    # 認証URL生成（実際の環境では適切なURLに変更）
    verification_url = f"http://localhost:3000/verify-email?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>メール認証</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="color: #2563eb; margin: 0;">🏔️ すたっととっとり</h1>
            <p style="color: #6b7280; margin: 5px 0 0 0;">鳥取県統計分析プラットフォーム</p>
        </div>
        
        <h2 style="color: #1f2937;">メール認証のお願い</h2>
        
        <p>{username}様</p>
        
        <p>この度は「すたっととっとり」にご登録いただき、ありがとうございます。</p>
        
        <p>アカウントを有効化するため、下記のボタンをクリックしてメール認証を完了してください。</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="background-color: #2563eb; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 6px; display: inline-block;
                      font-weight: bold;">
                メール認証を完了する
            </a>
        </div>
        
        <p style="color: #6b7280; font-size: 14px;">
            ボタンをクリックできない場合は、下記URLをコピーしてブラウザのアドレスバーに貼り付けてください：<br>
            <a href="{verification_url}" style="color: #2563eb;">{verification_url}</a>
        </p>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        
        <p style="color: #6b7280; font-size: 12px;">
            このメールに心当たりがない場合は、このメールを無視してください。<br>
            お困りの際は、システム管理者までお問い合わせください。
        </p>
    </body>
    </html>
    """
    
    text_content = f"""
    【すたっととっとり】メール認証のお願い
    
    {username}様
    
    この度は「すたっととっとり」にご登録いただき、ありがとうございます。
    
    アカウントを有効化するため、下記のURLにアクセスしてメール認証を完了してください。
    
    {verification_url}
    
    このメールに心当たりがない場合は、このメールを無視してください。
    お困りの際は、システム管理者までお問い合わせください。
    """
    
    return email_service.send_email(email, subject, html_content, text_content)

def send_password_reset_email(email: str, token: str, username: str) -> bool:
    """パスワードリセット用メール送信"""
    
    subject = "【すたっととっとり】パスワードリセットのご案内"
    
    # パスワードリセットURL生成
    reset_url = f"http://localhost:3000/reset-password?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>パスワードリセット</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="color: #2563eb; margin: 0;">🏔️ すたっととっとり</h1>
            <p style="color: #6b7280; margin: 5px 0 0 0;">鳥取県統計分析プラットフォーム</p>
        </div>
        
        <h2 style="color: #1f2937;">パスワードリセットのご案内</h2>
        
        <p>{username}様</p>
        
        <p>パスワードリセットのご依頼を受け付けました。</p>
        
        <p>新しいパスワードを設定するため、下記のボタンをクリックしてください。</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" 
               style="background-color: #dc2626; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 6px; display: inline-block;
                      font-weight: bold;">
                パスワードをリセットする
            </a>
        </div>
        
        <p style="color: #6b7280; font-size: 14px;">
            ボタンをクリックできない場合は、下記URLをコピーしてブラウザのアドレスバーに貼り付けてください：<br>
            <a href="{reset_url}" style="color: #dc2626;">{reset_url}</a>
        </p>
        
        <p style="color: #dc2626; font-weight: bold; font-size: 14px;">
            ⚠️ このリンクは1時間後に無効になります。
        </p>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        
        <p style="color: #6b7280; font-size: 12px;">
            パスワードリセットを依頼していない場合は、このメールを無視してください。<br>
            セキュリティ上の懸念がある場合は、システム管理者までお問い合わせください。
        </p>
    </body>
    </html>
    """
    
    text_content = f"""
    【すたっととっとり】パスワードリセットのご案内
    
    {username}様
    
    パスワードリセットのご依頼を受け付けました。
    
    新しいパスワードを設定するため、下記のURLにアクセスしてください。
    
    {reset_url}
    
    ⚠️ このリンクは1時間後に無効になります。
    
    パスワードリセットを依頼していない場合は、このメールを無視してください。
    セキュリティ上の懸念がある場合は、システム管理者までお問い合わせください。
    """
    
    return email_service.send_email(email, subject, html_content, text_content)

def send_welcome_email(email: str, username: str) -> bool:
    """ウェルカムメール送信"""
    
    subject = "【すたっととっとり】ご登録ありがとうございます"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>ウェルカムメール</title>
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="color: #2563eb; margin: 0;">🏔️ すたっととっとり</h1>
            <p style="color: #6b7280; margin: 5px 0 0 0;">鳥取県統計分析プラットフォーム</p>
        </div>
        
        <h2 style="color: #1f2937;">ようこそ！</h2>
        
        <p>{username}様</p>
        
        <p>この度は「すたっととっとり」にご登録いただき、ありがとうございました。</p>
        
        <p>このプラットフォームでは、以下の機能をご利用いただけます：</p>
        
        <ul style="color: #374151; line-height: 1.6;">
            <li>📊 人口動態・住みやすさ指標の詳細分析</li>
            <li>🤖 AI による政策効果予測</li>
            <li>🗺️ インタラクティブな地図表示</li>
            <li>📈 高度なデータ可視化（D3.js）</li>
            <li>💾 分析履歴の保存・共有</li>
        </ul>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://localhost:3000/" 
               style="background-color: #2563eb; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 6px; display: inline-block;
                      font-weight: bold;">
                プラットフォームを開始する
            </a>
        </div>
        
        <p>ご不明な点がございましたら、お気軽にお問い合わせください。</p>
        
        <p>今後ともよろしくお願いいたします。</p>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        
        <p style="color: #6b7280; font-size: 12px;">
            すたっととっとり運営チーム
        </p>
    </body>
    </html>
    """
    
    text_content = f"""
    【すたっととっとり】ご登録ありがとうございます
    
    {username}様
    
    この度は「すたっととっとり」にご登録いただき、ありがとうございました。
    
    このプラットフォームでは、以下の機能をご利用いただけます：
    
    - 人口動態・住みやすさ指標の詳細分析
    - AI による政策効果予測
    - インタラクティブな地図表示
    - 高度なデータ可視化
    - 分析履歴の保存・共有
    
    プラットフォーム: http://localhost:3000/
    
    ご不明な点がございましたら、お気軽にお問い合わせください。
    今後ともよろしくお願いいたします。
    
    すたっととっとり運営チーム
    """
    
    return email_service.send_email(email, subject, html_content, text_content)