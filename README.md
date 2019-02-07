# dojotest
This has been created for Dojo test
Task 1:
=======

Please find the files under this repository and run the file docker-compose file as below:

#docker-compose up -d

For your information: My current output is displaying under http://ec2-18-221-29-48.us-east-2.compute.amazonaws.com/. Please refresh the browser every 20 seconds and it will changes the output message.

Task 2:
=======

                               Running DOJO madness application in AWS Cloud Environment

ECS is the AWS Docker container service that handles the orchestration and provisioning of Docker containers. 
The Container Instances are part of a logical group called an ECS Cluster
Steps involved:
•	Create ECR repository for storing the images
•	Push custom image from development system to amazon ECR
•	Create ECS Cluster with 2 Container Instance
•	Create a Task Definition
•	Create an ELB and Target Group to later associate with the ECS Service
•	Create a Service that runs the Task Definition
•	Confirm everything is Working
Create ECR repository for storing the images:
1.	Open the Amazon ECR console at https://console.aws.amazon.com/ecr/repositories.
2.	From the navigation bar, choose the region to create repository.
3.	In the navigation pane, choose Repositories.
4.	On the Repositories page, choose Create repository.
5.	For Repository configuration, enter a unique name for our repository and choose Create repository.
6.	Select the repository we created and choose View push commands to view the steps to push an image to our new repository.
Push custom image from development system to amazon ECR
1.	Retrieve the docker login command that can use to authenticate Docker client to our registry by pasting the aws ecr get-login command from the console into a terminal window.
2.	Run the command from Docker client: aws ecr get-login --region region --no-include-email
$ docker login -u AWS -p password https://aws_account_id.dkr.ecr.us-east-1.amazonaws.com
3.	Genearte the image from Dockerfile  and tag it as dojo:latest
4.	Push the dojo:latest image to our ECR repository by pasting the docker push command into a terminal window.
Create ECS Cluster with 2 Container Instance: 
1.	Before creating a cluster, we need to create a security group called dojo-ecs-sg that we’ll use.
$ aws ec2 create-security-group --group-name dojo-ecs-sg --description dojo-ecs-sg
2.	Now create an ECS Cluster called dojo-cluster and the ec2 instances that belongs to the ECS Cluster. Use the dojo-ecs-sg security group that was created. We can get the id of the security group from the EC2 Console / Network & Security / Security Groups. It is important to select a Key pair so we can ssh into the instance later to verify things are working.
3.	For the Networking VPC settings, we can use custom VPC and all the Subnets associated with the account. For the IAM Role use ecsInstanceRole. If ecsInstanceRole does not yet exist, create it. We will need to change the settings according to our own account, VPC and Subnets
Create a task definition
1.	This is describes how a docker container should launch. It contains settings like exposed port, docker image, cpu shares, memory requirement, command to run and environmental variables.
2.	We could use this template for creating the task definition.
3.	Register task definition using aws cli : 
$aws ecs register-task-definition --cli-input-json file://task-definition.json
4.	In our ECS task definitions, make sure that we are using the full registry/repository:tag naming for our ECR images. For example, aws_account_id.dkr.ecr.region.amazonaws.com/dojo:latest. So, both dojo and nginx containers should be created as part of task-definition.json
5.	Confirm that the task definition successfully registered with the ECS Console.
Create an ELB and Target Group to later associate with the ECS Service
1.	Now create an ELB and a target group with it. ELB used to load balance requests across multiple containers and also want to expose the html ouput page to the internet for testing. The easiest way to create an ELB is with the EC2 Console.
2.	Go the EC2 Console / Load Balancing / Load Balancers, click “Create Load Balancer” and select Application Load Balancer.Create Configure Load Balancer.
3.	Name it like dojo-elb and select internet-facing.
4.	Use the default Listener with a HTTP protocol and Port 80.
5.	Under Availability Zone, choose our VPC and choose the all subnets. It is very important to choose the same subnets that was chosen when create the cluster. If the subnets are not the same the ELB health check can fail and the containers will keep getting destroyed and recreated in an infinite loop if the instance is launched in an AZ that the ELB is not configured to see.
6.	Configure Security Groups for elb like dojo-elb-sg and open up port 80 and source 0.0.0.0/0 so anything from the outside world can access the ELB port 80.
7.	Configure Routing to Create a new target group name dojo-target-group with port 80. 
8.	Register Targets for select instances and create
9.	Now only port 80 on the ELB is exposed to the outside world and any traffic from the ELB going to a container instance with the dojo-ecs-sg group is allowed like executing below command:
$ aws ec2 authorize-security-group-ingress --group-name dojo-ecs-sg --protocol tcp --port 1-65535 --source-group dojo-elb-sg
Create a Service that runs the Task Definition
1.	The command to create the ECS service takes a few parameters so it is easier to use a json file as it’s input. Hence, create a ecs-service.json file with the following:
{
    "cluster": "dojo-cluster",
    "serviceName": "dojo-service",
    "taskDefinition": "dojo-app",
    "loadBalancers": [
        {
            "targetGroupArn": "FILL-IN-ELB-TARGET-GROUP-ARN",
            "containerName": "web",
            "containerPort": 80
        }
    ],
    "desiredCount": 1,
    "role": "ecsServiceRole"
}

2.	To find the targetGroupArn, we can go to the EC2 Console / Load Balancing / Target Groups and click on the dojo-target-group
3.	Now create the ECS service: my-service
$ aws ecs create-service --cli-input-json file://ecs-service.json
Confirm everything is Working
1.	Confirm that the service is running properly. Check that dojo-target-group is showing and maintaining healthy targets. Under Load Balancing / Target Groups, click on dojo-target-group and check the Targets tab. We should see a Target that is reporting healthy
2.	Let also ssh into the instance and see the running docker process is returning a good response. Under Clusters / ECS Instances, click on the Container Instance and grab the public dns record so we can ssh into the instance.
3.	Lastly, let’s also verify by hitting the external DNS address of the ELB. We can find the DNS address in the EC2 Console under Load Balancing / Load Balancers and clicking on dojo-elb.
4.	Verify the ELB publicly available DNS endpoint with curl:
$ curl dojo-elb-1693572386.us-east-1.elb.amazonaws.com
