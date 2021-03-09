from snapshots_handler import SnapshotsHandler

import config
import util

def main():
    if util.is_authorized():
        snapshot_handler = SnapshotsHandler(config)
        snapshot_handler.delete_snapshots()
        print("Done deleting snapshots older than {} days!".format(
            config.BACKUP_RETENTION_IN_DAYS))
        return 1
    print ("The IP of this server is not the Main Instance! Skipping delete snapshots...")
    return 0

if __name__ == '__main__':
    main()
