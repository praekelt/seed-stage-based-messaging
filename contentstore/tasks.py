import os
import requests
import paramiko

from celery.task import Task
from django.conf import settings
from django.utils._os import abspathu
from sftpclone import sftpclone

from subscriptions.models import Subscription
from subscriptions.tasks import make_absolute_url, send_next_message
from .models import BinaryContent


class SyncAudioMessages(Task):

    def _get_existing_files(self, root, host, username, password, port):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, port=port)
        ftp = ssh.open_sftp()
        existing_files = ftp.listdir(root)
        return existing_files

    def run(self, **kwargs):
        if settings.AUDIO_FTP_HOST:
            src = abspathu(settings.MEDIA_ROOT)
            if not src.endswith('/'):
                src += '/'

            root = settings.AUDIO_FTP_ROOT
            host = settings.AUDIO_FTP_HOST
            username = settings.AUDIO_FTP_USER
            password = settings.AUDIO_FTP_PASS
            port = int(settings.AUDIO_FTP_PORT)

            existing_files = self._get_existing_files(
                root, host, username, password, port)

            delete_files = []

            files = BinaryContent.objects.all()
            for item in files.iterator():

                if item.content.name not in existing_files:
                    r = requests.get(make_absolute_url(item.content.url))

                    local_path = '{}{}'.format(src, item.content.name)
                    with open(local_path, "wb") as f:
                        f.write(r.content)

                    delete_files.append(local_path)

            cloner = sftpclone.SFTPClone(
                src,
                "{}:{}@{}:{}".format(username, password, host, root),
                port=port,
                delete=False
            )

            cloner.run()

            for item in delete_files:
                os.remove(item)


sync_audio_messages = SyncAudioMessages()


class QueueSubscriptionSend(Task):
    """
    Queues the send next message task for all of the subscriptions tied to
    the schedule.
    """
    name = "contentstore.tasks.queue_subscription_send"

    def run(self, schedule_id, **kwargs):
        """
        Arguments:
            schedule_id {int} -- The schedule to send messages for
        """
        subscriptions = Subscription.objects.filter(
            schedule_id=schedule_id,
            active=True,
            completed=False,
            process_status=0,
        ).values('id')
        for subscription in subscriptions.iterator():
            send_next_message.delay(str(subscription['id']))

queue_subscription_send = QueueSubscriptionSend()
