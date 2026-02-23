import smtplib
from email.message import EmailMessage
from utils import resource_path
import mysql.connector
from config import get_db_connection
import os
import asyncio
from telegram import Bot
from telegram.request import HTTPXRequest
from telegram.error import TelegramError
import json

class LowAttendanceNotifier:
    def __init__(self):
        self.threshold = 75.0 # Percentage
        self.bot_token = self._load_bot_token()

    def _load_bot_token(self):
        # Try .env first
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token: return token
        
        # Try json file
        try:
            with open(resource_path("telegram_bot_credentials.json"), 'r') as f:
                data = json.load(f)
                return data.get('bot_token', '')
        except:
            return ""

    async def _send_telegram_async(self, chat_id, message):
        if not self.bot_token: return False
        try:
            request = HTTPXRequest(connect_timeout=60, read_timeout=60)
            bot = Bot(token=self.bot_token, request=request)
            async with bot:
                await bot.send_message(chat_id=chat_id, text=message)
            return True
        except Exception as e:
            print(f"Telegram Async Error: {e}")
            return False

    def send_telegram_alert(self, chat_id, name, pct):
        if not chat_id: return False
        
        msg = f"⚠️ Low Attendance Alert ⚠️\n\nDear {name},\n\nYour attendance is {pct:.1f}%, which is below the {self.threshold}% threshold.\nPlease meet the coordinator.\n\nRegards,\nAdmin"
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._send_telegram_async(chat_id, msg))
            finally:
                loop.close()
        except Exception as e:
             print(f"Telegram Sync Error: {e}")
             return False

    def check_and_notify(self):
        """Check all students for low attendance and send alerts"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Fetch TelegramID as well
            # Note: Checking if column exists first might be safer, but assuming it exists based on user code
            try:
                cursor.execute("SELECT Student_id, Student_name, Email, TelegramID FROM student")
            except:
                 # Fallback if TelegramID logic fails (e.g. column missing), though user has it
                 cursor.execute("SELECT Student_id, Student_name, Email, '' as TelegramID FROM student")
                 
            students = cursor.fetchall()
            
            alerts_sent = 0
            
            # Get total working days (estimate)
            cursor.execute("SELECT COUNT(DISTINCT Date) FROM attendance")
            total_days = cursor.fetchone()[0]
            
            for student in students:
                sid, name, email, telegram_id = student
                
                # Calculate attendance
                cursor.execute("SELECT COUNT(*) FROM attendance WHERE Student_id=%s", (sid,))
                present_days = cursor.fetchone()[0]
                
                if total_days == 0:
                    continue
                    
                attendance_pct = (present_days / total_days) * 100
                
                if attendance_pct < self.threshold:
                    email_sent = self.send_alert_email(name, email, attendance_pct, present_days, total_days)
                    
                    telegram_sent = False
                    if telegram_id:
                        telegram_sent = self.send_telegram_alert(telegram_id, name, attendance_pct)
                    
                    if email_sent or telegram_sent:
                        alerts_sent += 1
                        
            conn.close()
            return f"Checked {len(students)} students. Sent {alerts_sent} alerts."
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: {e}"

    def send_alert_email(self, name, email, pct, present, total):
        try:
            if not email or "@" not in email:
                return False
                
            user = os.getenv("SMTP_USER")
            password = os.getenv("SMTP_PASSWORD")
            
            if not user or not password:
                if os.path.exists(resource_path("credentials.txt")):
                    with open(resource_path("credentials.txt"), "r") as f:
                        line = f.readline().strip().split(',')
                        if len(line) >= 2:
                            user, password = line[0], line[1]
            
            if not user or not password:
                return False

            msg = EmailMessage()
            msg.set_content(f"""
            Dear {name},
            
            This is an alert regarding your low attendance.
            Current Attendance: {pct:.1f}% ({present}/{total} days)
            Minimum Required: {self.threshold}%
            
            Please meet your coordinator immediately.
            
            Regards,
            Admin
            """)
            
            msg['Subject'] = 'Low Attendance Alert'
            msg['From'] = user
            msg['To'] = email
            
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
            server.quit()
            return True
            
        except Exception as e:
            print(f"Failed to send to {name}: {e}")
            return False

    def _notify_thread(self, callback):
        result = self.check_and_notify()
        if callback:
            callback(result)

    def check_and_notify_threaded(self, callback=None):
        import threading
        t = threading.Thread(target=self._notify_thread, args=(callback,))
        t.start()
