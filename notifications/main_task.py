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
        latest_notifications = get_all_user_notifications(user.token)
        notifications = dict(((n.id, n) for n in latest_notifications))
        user_notifications = dict(((n.id, n) for n in user.notifications))
        all_notification_ids = sorted(
            set(notifications.keys()) | set(user_notifications.keys()),
            key=lambda n: (
                notifications.get(n) or user_notifications.get(n)
            ).updated_at,
        )
        id_pairs = [
            (notifications.get(_id), user_notifications.get(_id))
            for _id in all_notification_ids
        ]
        for new, old in id_pairs:
            if old is None:
                notify_fn(user, new)
            elif new is None:
                continue
            elif new != old:
                notify_fn(user, new)
        user.notifications = latest_notifications


def notify_all_users_by_slack(data_manager: DataManager):
    users = data_manager.get_users()
    main(users, notify_slack)
    data_manager.save_all(users)


def notify_users_with_30m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is not None and 22.5 <= u.config.frequency
    ]
    main(users, notify_slack)
    data_manager.save_all(users)


def notify_users_with_15m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is None or 12.5 <= u.config.frequency < 22.5
    ]
    main(users, notify_slack)
    data_manager.save_all(users)


def notify_users_with_10m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is not None and 7.5 <= u.config.frequency < 12.5
    ]
    main(users, notify_slack)
    data_manager.save_all(users)


def notify_users_with_5m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is not None and 2.5 <= u.config.frequency < 7.5
    ]
    main(users, notify_slack)
    data_manager.save_all(users)


def notify_users_with_1m_config_by_slack(data_manager: DataManager):
    users = [
        u
        for u in data_manager.get_users()
        if u.config.frequency is not None and 0 < u.config.frequency < 2.5
    ]
    main(users, notify_slack)
    data_manager.save_all(users)


def start_scheduler(data_manager: DataManager):
    scheduler.add_job(
        notify_users_with_1m_config_by_slack,
        "interval",
        args=(data_manager,),
        minutes=1,
    )
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
