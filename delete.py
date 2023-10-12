import os
import json
import boto3
import botocore

def getNameFiles(profile):
    dir = os.path.join(os.getcwd(),profile)
    files_and_directories = os.listdir(dir)
    return files_and_directories

def delete(profile):
    session = boto3.Session(profile_name=profile)
    ec2 = session.client("ec2")
    ec2r = session.resource("ec2")

    print(f"\nEliminando securitygroups de {profile}")
    files_and_directories = getNameFiles(profile) 
    print(files_and_directories)
    for filename in files_and_directories:
        with open(os.path.join(os.getcwd(),profile, filename), 'r') as f:
            data = json.load(f)
            groupid = data['GroupId']
            print(f"Eliminando {groupid}")
            try:
                sg = ec2r.SecurityGroup(groupid)
                
                if len(sg.ip_permissions) != 0 :
                    print(f"Eliminando reglas ingress de {groupid}")
                    responseingress = sg.revoke_ingress(IpPermissions=sg.ip_permissions)
                    print(responseingress)
                if len(sg.ip_permissions_egress) != 0:
                    print(f"Eliminando reglas egress de {groupid}") 
                    responseegress = sg.revoke_egress(IpPermissions=sg.ip_permissions_egress)
                    print(responseegress)
                response = ec2.delete_security_group(
                    GroupId=groupid,
                )
                print(response) 
            except botocore.exceptions.ClientError as e:
                print(e)
            


if __name__ == "__main__":
    #profiles = ["prati_develop","prati_staging","prati_prod","default"]
    profiles = ["prati_prod"]
    for x in profiles:
        delete(x)