from monthly_report import SendMonthlyReport
from daily_report import SendDailyReport
import schedule
import time
from datetime import datetime

# Define the function to send daily report
def send_daily_report():
    SendDailyReport()

# Define the function to send monthly report
def send_monthly_report():
    SendMonthlyReport()

# Check if today is the first day of the month
def check_and_send_monthly_report():
    if datetime.now().day == 1:
        send_monthly_report()

# Schedule the daily report to be sent every day at a specific time
schedule.every().day.at("09:00").do(send_daily_report)  # Adjust the time as needed

# Schedule the check for monthly report every day at a specific time
schedule.every().day.at("09:05").do(check_and_send_monthly_report)  # Adjust the time as needed

# Run the schedule in an infinite loop
while True:
    schedule.run_pending()
    time.sleep(60)
