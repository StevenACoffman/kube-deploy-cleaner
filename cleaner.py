#!/usr/bin/env python3

import argparse
import datetime
import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging
import sys

LOGGER_NAME = None


def log():
    return logging.getLogger(LOGGER_NAME)


def config_logger():
    logger = log()
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(funcName)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def parse_time(s: str):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)


def td_format(td_object):
    if td_object is None:
        return "None"
    seconds = int(td_object.total_seconds())
    periods = [
        ('year',        60*60*24*365),
        ('month',       60*60*24*30),
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
        ('second',      1)
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


def deployment_expired(deployment):
    now = datetime.datetime.now(datetime.timezone.utc)
    grace_period = 0

    annotations = deployment.metadata.annotations
    deployment_expiration = annotations.get('deploymentExpirationTime', None)
    if deployment_expiration:
        deployment_expiration = parse_time(deployment_expiration)
        seconds_since_expiration = now - deployment_expiration
        if seconds_since_expiration > datetime.timedelta(grace_period):
            return '{} old'.format(td_format(seconds_since_expiration))


def delete_if_expired(dry_run, deployment, reason, api_instance):
    if reason:
        log().info("Deleting namespace {} deployment {} ({})".format(deployment.metadata.namespace, deployment.metadata.name, reason))
        if dry_run:
            log().info('** DRY RUN **')
        else:
            api_response = api_instance.delete_namespaced_deployment(
                name=deployment.metadata.name,
                namespace=deployment.metadata.namespace,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                    grace_period_seconds=5))
            log().info("Deployment deleted.")


def main():
    config_logger()
    log().info('Starting kube-job-cleaner')
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    args = parser.parse_args()

    if os.getenv('IN_CLUSTER', 'true') in ("yes", "true"):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    log().info('Looking for expired "Deployment" objects')
    # create an instance of the API class
    api_instance = client.AppsV1beta2Api()
    # label_selector = 'label_selector_example'

    try: 
        api_response = api_instance.list_deployment_for_all_namespaces(watch=False)
        for deployment in api_response.items:
            log().info("Checking namespace {} deployment {} for expiration".format(deployment.metadata.namespace, deployment.metadata.name))
            delete_if_expired(args.dry_run, deployment, deployment_expired(deployment), api_instance)
    except ApiException as e:
        log().error("Exception when calling AppsV1beta2Api->list_deployment_for_all_namespaces: {}\n".format(e))


if __name__ == "__main__":
    main()
