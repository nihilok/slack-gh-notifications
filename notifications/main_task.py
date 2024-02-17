import logging
from typing import Callable

from apscheduler.triggers.cron import CronTrigger

from data.base import DataManager
from data.json_manager import JsonManager
from data.user import User
from notifications.github_funcs import get_all_user_notifications
from notifications.models import Notification
from notifications.notify_slack import notify_slack
from apscheduler.schedulers.background import BackgroundScheduler


scheduler = BackgroundScheduler()


def main(users: list[User], notify_fn: Callable[[User, Notification], None]):
    for user in users:
        notifications = get_all_user_notifications(user.token)
        for notification in notifications:
            notify_fn(user, notification)


def notify_all_users_by_slack(data_manager: DataManager):
    users = data_manager.get_users()
    main(users, notify_slack)


def notify_users_with_30m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is not None and 22.5 <= u.config.frequency
    ]
    main(users, notify_slack)


def notify_users_with_15m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is None or 12.5 <= u.config.frequency < 22.5
    ]
    main(users, notify_slack)


def notify_users_with_10m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is not None and 7.5 <= u.config.frequency < 12.5
    ]
    main(users, notify_slack)


def notify_users_with_5m_config_by_slack(data_mananger: DataManager):
    logging.info("5 minute task called")
    users = [
        u
        for u in data_mananger.get_users()
        if u.config.frequency is not None and 0 <= u.config.frequency < 7.5
    ]
    main(users, notify_slack)


def start_scheduler(data_manager: DataManager):
    scheduler.add_job(
        notify_users_with_5m_config_by_slack,
        CronTrigger(minute="0,5,10,15,20,25,30,35,40,45,50,55"),
        args=(data_manager,),
    )
    scheduler.add_job(
        notify_users_with_10m_config_by_slack,
        CronTrigger(minute="0,10,20,30,40,50"),
        args=(data_manager,),
    )
    scheduler.add_job(
        notify_users_with_15m_config_by_slack,
        CronTrigger(minute="0,15,30,45"),
        args=(data_manager,),
    )
    scheduler.add_job(
        notify_users_with_30m_config_by_slack,
        CronTrigger(minute="0,30"),
        args=(data_manager,),
    )
    scheduler.start()


if __name__ == "__main__":
    manager = JsonManager("./user_data")
    notify_all_users_by_slack(manager)
