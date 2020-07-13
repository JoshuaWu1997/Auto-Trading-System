"""
@File   :utils.py
@Author :JohsuaWu1997
@Date   :13/07/2020
"""
import datetime


def is_today(time_tick, n_time=None):
    if n_time is None:
        return time_tick.date() == datetime.datetime.now().date()
    else:
        return time_tick.date() == n_time.date()


def print_transactions(ids, price, amount):
    for i in range(len(ids)):
        println = 'buy  ' if amount[i] > 0 else 'sell '
        print(println + ids[i] + ' for ' + str(abs(amount[i])) + ' on ' + str(price[i]))


def is_trade():
    date = str(datetime.datetime.now().date())
    n_time = datetime.datetime.now()
    m_start = datetime.datetime.strptime(date + '09:30', '%Y-%m-%d%H:%M')
    m_end = datetime.datetime.strptime(date + '11:30', '%Y-%m-%d%H:%M')
    n_start = datetime.datetime.strptime(date + '13:00', '%Y-%m-%d%H:%M')
    n_end = datetime.datetime.strptime(date + '15:00', '%Y-%m-%d%H:%M')
    return (m_start < n_time < m_end) or (n_start < n_time < n_end)
