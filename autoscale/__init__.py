import time
import boto3


class AutoScalingConfigCreator(object):
    def __init__(self, image="", config):
        self._config = config
        self._autoscale_client = boto3.client('autoscaling', region_name=self._config.AWS_REGION)
        self._image = image
        self._launch_config_name = self._config.LAUNCH_CONFIG_NAME + '-' + \
            str(time.strftime('%Y%m%d_%H%M%S'))

    def update_autoscaling(self):
        launch_configs = self._get_all_launch_config()

        if len(launch_configs) >= 5:
            sorted_launch_configs = sorted(
                launch_configs,
                key=lambda launch_config: launch_config[
                    'LaunchConfigurationName']
            )

            for launch_config in sorted_launch_configs[:-4]:
                self._delete_launch_config(
                    launch_config['LaunchConfigurationName'])

        sg = self._config.SECURITY_GROUPS
        if self._config.USER_DATA != '':
            user_data_raw_list = self._config.USER_DATA.split('\\n')
            self._config.USER_DATA = '\n'.join(user_data_raw_list)
        self._autoscale_client.create_launch_configuration(
            LaunchConfigurationName=self._launch_config_name,
            ImageId=self._image.id,
            KeyName=self._config.EC2_KEYNAME,
            SecurityGroups=sg.split(),
            InstanceType=self._config.INSTANCE_TYPE,
            SpotPrice=self._config.SPOT_PRICE,
            UserData=self._config.USER_DATA,
            InstanceMonitoring={
                'Enabled': self._config.DETAILED_MONITORING
            },
            IamInstanceProfile=self._config.INSTANCE_PROFILE
        )

        self._autoscale_client.update_auto_scaling_group(
            AutoScalingGroupName=self._config.ASG_NAME,
            LaunchConfigurationName=self._launch_config_name,
            MinSize=int(self._config.MIN_ASG_SIZE),
            MaxSize=int(self._config.MAX_ASG_SIZE)
        )

    def instance_refresh(self):
        response = self._autoscale_client.start_instance_refresh(
            AutoScalingGroupName=self._config.ASG_NAME,
            Strategy='Rolling',
            Preferences={
                'MinHealthyPercentage': 50,
                'InstanceWarmup': 0
            }
        )

    def _get_all_launch_config(self):
        launch_configs = self._autoscale_client.describe_launch_configurations(
            MaxRecords=100)['LaunchConfigurations']

        return [lc for lc in launch_configs
                if lc['LaunchConfigurationName'].startswith(self._config.LAUNCH_CONFIG_NAME)]

    def _delete_launch_config(self, launch_config_name):
        self._autoscale_client.delete_launch_configuration(
            LaunchConfigurationName=launch_config_name
        )
