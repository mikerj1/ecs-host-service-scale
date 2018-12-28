#!/usr/bin/env python
"""
A Lambda Function to set the desired count of running tasks
in a service based upon environment variables

"""
from __future__ import print_function

import os

import boto3


def ecs_client():
    return boto3.client("ecs")


def adjust_service_desired_count(ecs_client, cluster, service, desiredCount):
    running_service = ecs_client.describe_services(cluster=cluster, services=[service])

    if not running_service["services"]:
        print("SKIP: Service not found in cluster {}".format(cluster))
        return

    desired_task_count = running_service["services"][0]["desiredCount"]

    clusters = ecs_client.describe_clusters(clusters=[cluster])
    registered_instances = clusters["clusters"][0]["registeredContainerInstancesCount"]

    if desired_task_count != desiredCount:
        print("Adjusting cluster '{}' to run {} tasks of service '{}'".format(
            cluster, desiredCount, service
        ))
        response = ecs_client.update_service(
            cluster=cluster,
            service=service,
            desiredCount=desiredCount,
        )

        print(response)
        return response

    # Do nothing otherwise
    print("SKIP: Cluster {} has {} desired tasks for {} registered instances.".format(
        cluster, desired_task_count, registered_instances
    ))
    return


def lambda_handler(event, context):
    if not event:
        raise ValueError("No event provided.")

    service = os.getenv('ECS_SERVICE_ARN')
    if not service:
        raise ValueError("Need to set `ECS_SERVICE_ARN` env var to serviceArn(s).")
        
    cluster = os.getenv('ECS_CLUSTER_ARN')
    if not cluster:
        raise ValueError("Need to set `ECS_CLUSTER_ARN` env var to clusterArn.")
        
    desired_count = int(os.getenv('DESIRED_COUNT'))
    #if not desired_count:
      #  raise ValueError("Need to set `DESIRED_COUNT` to the desired number of tasks.")
    print (desired_count)
    serviceItems = service.split(',')
    
    for item in serviceItems[:]:
      adjust_service_desired_count(ecs_client(), cluster, item, desired_count)
    print("DONE")
