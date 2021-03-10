from datetime import datetime, timedelta
from dateutil import tz
import boto3
import botocore
import pytz

utc = pytz.UTC

class SnapshotsHandler(object):
    def __init__(self, config):
        self._config = config
        self.ec2 = boto3.resource('ec2')

    def _get_all_snapshots(self):
        return self.ec2.snapshots.filter(
            Filters=[
                {
                    'Name': 'description',
                    'Values': [
                        'Created by CreateImage(' +
                        self._config.INSTANCE_ID + ') for ami-*'
                    ]
                }
            ]
        )

    def delete_snapshots(self):
        snapshots = list(self._get_all_snapshots())
        if snapshots:
            self._delete_snapshot_days(snapshots)

    def _delete_snapshot_days(self, snapshots):
        if len(snapshots) > self._config.BACKUP_RETENTION_IN_DAYS:
            sorted_snapshots = sorted(snapshots, key=lambda snapshot: snapshot.start_time)

            delete_date_start = datetime.utcnow() - timedelta(days=self._config.BACKUP_RETENTION_IN_DAYS)
            #delete_date_start = utc.localize(delete_date_start)
            delete_date_start_utc = delete_date_start.replace(tzinfo=tz.tzutc(), microsecond=0)
            
            for snapshot in sorted_snapshots[:-self._config.BACKUP_RETENTION_IN_DAYS]: #keep number of snapshots based from number in BACKUP_RETENTION_IN_DAYS
                snapshot_copy = snapshot
                if snapshot_copy.start_time.replace(microsecond=0).date() <= delete_date_start_utc.date(): #delete snapshots that are beyond BACKUP_RETENTION_IN_DAYS days old
                    self._delete_snapshot(snapshot)

    def _delete_snapshot(self, snapshot):
        try: 
            snapshot_id = snapshot.id
            snapshot_start_time = snapshot.start_time
            snapshot.delete(DryRun=False)
            print(
                'deleted a snapshot: ' 
                'id: {}, ' 
                'date created (UTC): {}'.format(
                    snapshot_id, 
                    snapshot_start_time
                )
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidSnapshot.InUse':
                print (str(e))
            else:
                raise e
