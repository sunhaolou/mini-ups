import smtplib
import threading

seqnum = 1
seq_mutex = threading.Lock()
acks_world = []
acks_amazon = []


def get_curr_seqnum():
    seq_mutex.acquire()
    global seqnum
    seq = seqnum
    seqnum += 1
    seq_mutex.release()
    return seq

def ack_handler_amazon(acks_from_amazon):
    global acks_amazon
    for ack in acks_from_amazon:
        acks_amazon.append(ack)


def ack_handler(acks_from_world):
    global acks_world
    for ack in acks_from_world:
        acks_world.append(ack)


def check_ack(seq):
    global acks_world
    return seq in acks_world


def send_email(user_email, content):
    host = "smtp.gmail.com"
    port = 587
    From = "haolouproject@gmail.com"
    pwd = "ywnhgjqlrfkmkvjd"
    s = smtplib.SMTP(host, port)
    s.starttls()
    s.login(From, pwd)
    SUBJECT = "UPS Notification!"
    message = 'Subject: {}\n\n{}'.format(SUBJECT, content)
    s.sendmail(From, user_email, message)
    s.quit()
