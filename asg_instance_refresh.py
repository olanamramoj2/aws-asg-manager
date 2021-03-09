from autoscale import AutoScalingConfigCreator

import config
import util


def main(): 
    if util.is_authorized():
        autoscale_creator = AutoScalingConfigCreator(config)
        autoscale_creator.instance_refresh()
        print ("Done executing instance refresh for ASG {}!".format(config.ASG_NAME))
        return 1
    print ("The IP of this server is not the Main Instance! Skipping instance refresh...")
    return 0

if __name__ == '__main__':
    main()
