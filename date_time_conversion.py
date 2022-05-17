import datetime

from datetime import datetime

now = datetime.now()
a = '12:00:00'
b = '23:59:00'
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

if b > current_time > a:
    print('yes a')
else:
    # if b > current_time:
    print('yes b')
