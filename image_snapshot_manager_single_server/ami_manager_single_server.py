#python 2
from boto import ec2
import logging
import os
from datetime import datetime, timedelta
import time
from urllib2 import urlopen
from dateutil import tz

_AWS_connection = ec2.connect_to_region(
        "us-east-1",
        aws_access_key_id=open('/shared/aws_autoscale.key', 'r').readlines()[0].rstrip(),
        aws_secret_access_key=open('/shared/aws_autoscale.key', 'r').readlines()[1].rstrip()
    )
_delete_after_in_days = 2  # days
# _images_to_retain = 5
_dry_run = False
LIVE_HOST_FILE_PATH = '/shared/live_host.txt'
#tags required:
#ImageName and Backup
delete_time = datetime.utcnow() - timedelta(days=_delete_after_in_days)
delete_time_utc = delete_time.replace(tzinfo=tz.tzutc(), microsecond=0)


def get_all_instances_list():
    new_instances = []
    instances_list = _AWS_connection.get_all_instances()

    for reservation in instances_list:
        for instance in reservation.instances:
            if 'Backup' in instance.tags:
                if instance.tags['Backup'] == 'True':
                    new_instances.append(instance)
    return new_instances


def delete_image(instance):
    images = get_all_images(instance.tags['ImageName'])
    print 'Processing AMIs to delete for {0}'.format(instance.id)
    if images:
        if len(images) > _delete_after_in_days:
            sorted_images = sorted(images, key=lambda image: image.name)
            for ami in sorted_images:
                start_time = datetime.strptime(
                    ami.creationDate,
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                if start_time.replace(tzinfo=tz.tzutc()).date() <= delete_time_utc.date():
                    try:
                        ami.deregister(dry_run=_dry_run)
                        print 'Deleted AMI {name}({id}), Create time: {start}'.format(name=ami.name, id=ami.id, start=start_time)
                    except boto.exception.EC2ResponseError as e:
                        print str(e)
    print 'AMIs processed'
    # if len(images) > _images_to_retain:
    #     sorted_images_dict = {}
    #     images_list = []

    #     for image in images:
    #         images_list.append(image.name)
    #         sorted_images_dict[image.name] = image

    #     sorted_images = sorted(images_list)

    #     for x in range(0, len(sorted_images) -_images_to_retain):
    #         try:
    #             sorted_images_dict[sorted_images[x]].deregister(delete_snapshot=True, dry_run=_dry_run)
    #             print 'deleted image of ' + instance.id + ': ' + sorted_images[x]
    #         except Exception, e:
    #             print str(e)


def get_all_images(instance_ami_name):
    image_list = _AWS_connection.get_all_images(filters={'name': instance_ami_name + "-*"})
    return image_list


def delete_instance_snapshots(instance_id):
    deletion_counter = 0
    size_counter = 0
    print 'Processing snapshots to delete for instance {0}'.format(instance_id)
    snapshot_list = get_all_intance_snapshots(instance_id)
    if snapshot_list:
        if len(snapshot_list) > _delete_after_in_days:
            sorted_snapshots = sorted(snapshot_list, key=lambda snapshot: snapshot.start_time)
            # delete_date_start = datetime.utcnow() - timedelta(days=_delete_after_in_days)
            for snapshot in sorted_snapshots:
                start_date = datetime.strptime(
                    snapshot.start_time,
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                # start_date = start_date.strftime('%Y-%m-%d')
                if start_date.replace(tzinfo=tz.tzutc()).date() <= delete_time_utc.date():
                    deletion_counter = deletion_counter + 1
                    size_counter = size_counter + snapshot.volume_size
                    # Just to make sure you're reading!
                    try:
                        snapshot.delete(dry_run=_dry_run)
                        print 'Deleted SNAPSHOT ' + snapshot.id + ' of ' + instance_id + '(snapshot creation date: ' + unicode(
                        snapshot.start_time) + ', delete before: ' + unicode(delete_time_utc) + ')'
                    except boto.exception.EC2ResponseError as e:
                        print str(e)
                    # snapshot.delete(dry_run=_dry_run)
            if deletion_counter > 0:
                print 'Deleted {number} snapshots of {instanceid} totalling to {size} GB'.format(
                    number=deletion_counter,
                    instanceid=instance_id,
                    size=size_counter
                )
    print 'Snapshots processed'


def get_all_intance_snapshots(instance_id):
    print 'Get all snapshots for {0}'.format(instance_id)
    return _AWS_connection.get_all_snapshots(filters={'description':'Created by CreateImage(' + instance_id + ') for '
                                                                                                               'ami-* '
                                                                                                               'from '
                                                                                                               'vol-*'})


def main():
    _date_today = time.strftime("%Y%m%d_%H%M%S")

    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(levelname)s] %(message)s',
                        datefmt = '%b %d %Y %H:%M:%S',
                        filename='instance_create_image.log',
                        filemode='w')
    logger = logging.getLogger(__name__)

    instances = get_all_instances_list()

    for instance in instances:
        print 'Processing {0}'.format(instance)
        try:
            delete_image(instance)
            image_name = instance.tags['ImageName'] + '-' + _date_today
            print 'Creating AMI for {0}'.format(instance.id)
            _image_id = _AWS_connection.create_image(
                instance.id,
                image_name,
                description=image_name,
                no_reboot=True,
                dry_run=_dry_run
            )
            print 'AMI created: {ami_id} for {instance}, ami ID: {ami_name}'.format(ami_id=_image_id, instance=instance.id, ami_name=image_name)
            #logger.info('AMI %s Created base on Instance %s' % (_image_id, instance.id))
            delete_instance_snapshots(instance.id)
        except Exception, e:
            logger.error(str(e))
        print ''
    


def get_instance_public_ip():
    return urlopen('http://ip.42.pl/raw').read()


if __name__ == '__main__':
    if not os.path.isfile(LIVE_HOST_FILE_PATH):
        raise ValueError('Main site public ip address required in ' + LIVE_HOST_FILE_PATH)

    with open(LIVE_HOST_FILE_PATH) as live_host_file:
        main_site_ip_address = live_host_file.readline().strip()

    if get_instance_public_ip() == main_site_ip_address:
        main()