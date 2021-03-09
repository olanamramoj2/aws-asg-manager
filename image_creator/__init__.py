from datetime import datetime, timedelta
from dateutil import tz
import time
import boto3
import pytz

utc = pytz.UTC

class Ec2ImageCreator(object):
    def __init__(self, config):
        self._config = config
        self.ec2 = boto3.resource('ec2')

    def create_image(self):
        images = list(self._get_all_images())
        if images:
            self._deregister_image_days(images)

        _image = self.ec2.Instance(self._config.INSTANCE_ID).create_image(
            BlockDeviceMappings=[
                {
                    'DeviceName': self._config.BLOCK_DEVICE,
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': int(self._config.INSTANCE_VOLUME_SIZE),
                        'VolumeType': self._config.VOLUME_TYPE,
                        'Encrypted': False
                    }
                }
            ],
            Description='Image Created by CI',
            DryRun=False,
            Name=self._generate_image_name(),
            NoReboot=True
        )

        return _image

    def _deregister_image_days(self, images):
        if len(images) > self._config.BACKUP_RETENTION_IN_DAYS:
            sorted_images = sorted(images, key=lambda image: image.name)

            delete_date_start = datetime.utcnow() - timedelta(days=self._config.BACKUP_RETENTION_IN_DAYS)
            delete_date_start_utc = delete_date_start.replace(tzinfo=tz.tzutc(), microsecond=0)

            for image in sorted_images[:-self._config.BACKUP_RETENTION_IN_DAYS]: #keep number of images based from number in BACKUP_RETENTION_IN_DAYS
                image_create_date = datetime.strptime(image.creation_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                if image_create_date.replace(tzinfo=tz.tzutc()).date() <= delete_date_start_utc.date(): #delete images that are beyond BACKUP_RETENTION_IN_DAYS days old
                    self._deregister_image(image)

    def _deregister_image(self, image):
        try:
            ami_name = image.name
            ami_create_date = image.creation_date
            image.deregister(DryRun=False)
            print(
                'deregistered image: ' 
                'image name: {}, ' 
                'date created (UTC): {}'.format(
                    ami_name, 
                    ami_create_date
                )
            )
        except Exception as e:
            print(e)

    def _generate_image_name(self):
        return self._config.AMI_NAME + "-" + str(time.strftime('%Y%m%d_%H%M%S'))

    def _get_all_images(self):
        return self.ec2.images.filter(
            Filters=[
                {
                    'Name': 'name',
                    'Values': [
                        self._config.AMI_NAME + '-*'
                    ]
                }
            ]
        )
