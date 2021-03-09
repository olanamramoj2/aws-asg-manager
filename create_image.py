from autoscale import AutoScalingConfigCreator
from image_creator import Ec2ImageCreator

import config
import util


def main(): 
    if util.is_authorized():
        image_creator = Ec2ImageCreator(config)
        image = image_creator.create_image()
        print ("Done creating new image of {}!".format(config.AMI_NAME))

        autoscale_creator = AutoScalingConfigCreator(image, config)
        autoscale_creator.update_autoscaling()
        print ("Done updating ASG of {}!".format(config.ASG_NAME))
        return 1
    print ("The IP of this server is not the Main Instance! Skipping create image...")
    return 0

if __name__ == '__main__':
    main()
