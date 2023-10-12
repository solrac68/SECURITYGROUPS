import boto3
import os
import json

def saveFile(str,file, dir):
    ruta = os.path.join(os.getcwd(),dir)
    if not(os.path.exists(ruta)):
        os.mkdir(dir)
    rutaTotal = os.path.join(os.getcwd(),dir,file)
    text_file = open(rutaTotal, "w")
    text_file.write(str)
    text_file.close()

def printservicios(profile):
    session = boto3.Session(profile_name=profile)
    lista = session.get_available_services()
    for l in lista:
        print(l)

def find(profile):
    session = boto3.Session(profile_name=profile)

    ec2 = session.client("ec2")
    #ec2r = session.resource("ec2")
    elb = session.client("elb")
    elbv2 = session.client("elbv2")
    rds = session.client("rds")
    #apig = session.client('apigateway')

    used_SG = set()

    # response = apig.get_vpc_links()
    # print(response)

    # Find NetworkInterfaces security group in use.
    response = ec2.describe_network_interfaces()
    for l in response['NetworkInterfaces']:
        for g in  l['Groups']:
            groupid = g['GroupId']
            print(f"NetworkInterfaces SecurityGroup ID: {groupid}")
            used_SG.add(groupid)

    # Find EC2 instances security group in use.
    response = ec2.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            for sg in instance["SecurityGroups"]:
                groupid = sg["GroupId"]
                print(f"ec2 SecurityGroup ID: {groupid}")
                used_SG.add(groupid)

    # Find Classic load balancer security group in use
    response = elb.describe_load_balancers()
    for lb in response["LoadBalancerDescriptions"]:
        for sg in lb["SecurityGroups"]:
            print(f"elb SecurityGroup ID: {sg}")
            used_SG.add(sg)

    # Find Application load balancer security group in use
    response = elbv2.describe_load_balancers()
    for lb in response["LoadBalancers"]:
        for sg in lb["SecurityGroups"]:
            print(f"elbv2 SecurityGroup ID: {sg}")
            used_SG.add(sg)

    # Find RDS db security group in use
    response = rds.describe_db_instances()
    for instance in response["DBInstances"]:
        for sg in instance["VpcSecurityGroups"]:
            vpcrdssg = sg["VpcSecurityGroupId"]
            #print(f"rds SecurityGroup ID: {vpcrdssg}")
            used_SG.add(vpcrdssg)

    response = ec2.describe_security_groups()
    total_SG = [sg["GroupId"] for sg in response["SecurityGroups"]]
    unused_SG = set(total_SG) - used_SG

    print(f"Numero total de grupos de seguridad {profile}: {len(total_SG)}")
    print(f"Grupos de seguridad usados profile {profile}: {len(used_SG)}\n")
    print(f"Grupos de seguridad sin usar profile {profile}: {len(unused_SG)}")
    print(f"{list(unused_SG)}")

    # for l in list(unused_SG):
    #     security_group = ec2r.SecurityGroup(l)
    #     descripcion = security_group.description
    #     print(descripcion)

    response = ec2.describe_security_groups(GroupIds=list(unused_SG))

    #print(type(response))
    #print(type(response["SecurityGroups"]))


    for x in response["SecurityGroups"]:
        file = x['GroupId'] + ".json"
        print(x['GroupId'])
        app_json = json.dumps(x, indent=4)
        saveFile(app_json,file, profile)
        #print(app_json)
        #print("------------------------------------------------------------------------")


if __name__ == "__main__":
    profiles = ["prati_develop","prati_staging","prati_prod","default"]
    #profiles = ["prati_prod"]
    for x in profiles:
        find(x)

