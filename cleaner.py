#!/usr/bin/env python3

import argparse
import datetime
import os
import pykube


def parse_time(s: str):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc).timestamp()


def deployment_expired(deployment):
    now = datetime.datetime.now()
    grace_period = 0

    annotations = deployment.obj['metadata'].get('annotations', {})
    deployment_expiration = annotations.get('deploymentExpirationTime', None)
    if deployment_expiration:
        deployment_expiration = parse_time(deployment_expiration)
        seconds_since_expiration = now - deployment_expiration
        if seconds_since_expiration > grace_period:
            return '{:.0f}s old'.format(seconds_since_expiration)


def delete_if_expired(dry_run, entity, reason):
    if reason:
        print("Deleting {} {} ({})".format(entity.kind, entity.name, reason))
        if dry_run:
            print('** DRY RUN **')
        else:
            entity.delete()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    args = parser.parse_args()

    try:
        config = pykube.KubeConfig.from_service_account()
    except FileNotFoundError:
        # local testing
        config = pykube.KubeConfig.from_file(os.path.expanduser('~/.kube/config'))
    api = pykube.HTTPClient(config)

    for deployment in pykube.Deployment.objects(api, namespace=pykube.all):
        delete_if_expired(args.dry_run, deployment, deployment_expired(deployment))


if __name__ == "__main__":
    main()
