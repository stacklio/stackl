---
title: Usage
kind: basic
weight: 5
date: 2020-02-10 01:00:00 +0100
publishdate: 2020-02-01 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---
# Deploying a webserver on a virtual machine with STACKL (Terraform + Ansible)

This tutorial will help you understand how STACKL works by setting up a virtual machine with Terraform, and deploying Nginx on this machine with Ansible.

## Prerequisites

* Stackl
* Docker (or another way to build images)

## 1. Writing the Terraform and Ansible code for use by Stackl

STACKL can execute Terraform and Ansible code by running it in containers. This means we have to write our code, get the
variables from STACKL and bake it into a Docker image. We will start by making our Terraform image.

### Terraform

In this example we will create a virtual machine on vSphere, but we could deploy a virtual machine anywhere as long as
we can access it from where STACKL is running and we defined an output variable "hosts" (More about this later). If you
are unfamiliar with Terraform it is recommended you follow the [getting started guide](https://learn.hashicorp.com/terraform/getting-started/install).

First we'll write the code:

```hcl
provider "aws" {
  region = "var.aws_region"
  access_key = "var.aws_access_key"
  secret_key = "var.aws_secret_key"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["var.ami_name_value"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "web" {
  ami           = "${data.aws_ami.ubuntu.id}"
  instance_type = "var.instance_type"

  tags = {
    Name = "var.machine_name"
  }
}
```

Put this file in a directory (name it main.tf) and create a new file called `Dockerfile`, and add following content to this file:

```Dockerfile
FROM hashicorp/terraform:light

COPY main.tf main.tf

ENTRYPOINT []
```

Now build the terraform image with the following command (assuming you use Docker):

```sh
docker build -t stacklio/terraform-vm .
```

Now that the Terraform image is ready we can start with creating the Ansible one.

### Ansible

For this example we want to install Nginx on our machines by using the official Nginx role:

https://github.com/nginxinc/ansible-role-nginx

Make a new directory, and in this directory create a `roles` directory and clone the repository in this roles directory (name it nginx). Create a `Dockerfile`. You should now have the following structure.

```sh
.
├── Dockerfile
└── roles
    └── nginx
```

This will install Nginx by using the role we cloned earlier. It will expose it on the port provided within STACKL.

Next use this Dockerfile to build the image:

```Dockerfile
FROM quay.io/operator-framework/ansible-operator:v0.14.1

COPY roles /opt/ansible/
```

Build the image:

```sh
docker build -t stacklio/ansible-nginx .
```

## 2. Create the STACKL documents

Now that we have our automation code in place, we need to model both our infrastructure and our application in STACKL, we start by modelling our infrastructure.

### Infrastructure

To model our infrastructure we make use of three types of documents:

* Environment
* Location
* Zone

For this example we create a `production` environment which will look like this and contains mostly information about our VMware environment:

```yaml
---
category: configs
description: production environment
name: production
params: {}
packages:
- linux
- nginx
secrets:
  aws_access_key: YWNjZXNzX2tleQ==
  aws_secret_key: c2VjcmV0X2tleQ==
type: environment
tags:
  environment: production
```

We define a `location`, in this case it is where our datacenter is located:

```yaml
---
description: Ireland AWS
type: location
name: ireland
category: configs
params:
  aws_region: eu-west-1
```

Finally we define a zone, for our example we choose a cluster. We also add which configs are possible in this zone:

```yaml
---
description: eu-west-1-a
type: zone
name: eu-west-1-a
category: configs
params: {}
```

For these documents use the /documents endpoint and upload them. (Or put them in the right directory if you make use of the LocalFileSystem option)

Combine these documents in a stack infrastructure template, this way you can define all the possible targets in your organization.

POST the following payload to the /stack_infrastructure_template endpoint:

```yaml
---
category: configs
description: ''
infrastructure_capabilities: {}
infrastructure_targets:
- environment: production
  location: ireland
  zone: eu-west-1-a
name: stackl
type: stack_infrastructure_template
```

### Application

Now that we have defined our infrastructure we need to model our application. An application in Stackl can be an actual application, but it can also be something that can be provisioned E.G. A virtual machine. For our webserver we need two components. A virtual machine, with linux installed and our webserver software, in this case Nginx. We model these two as functional requirements.

#### Functional Requirements

Functional requirements in STACKL define what will be executed to create something, see the following example:

```yaml
---
category: configs
description: type functional_requirement with name linux
invocation:
  description: Deploys a Linux VM
  image: stacklio/terraform-vm
  tool: terraform
name: linux
params:
  ami_name_value: ubuntu/images/hvm-ssd/ubuntu-trusty-14.04-amd64-server-*
  instance_type: "t2.micro"
type: functional_requirement
```

Just like environments, locations and zones, functional requirements also have params. In our case it defines the lookup value for an AMI and the instance type.

Every FR (Functional Requirement) has an invocation part. This consists out of a description, the image that will be used (the ones we build earlier) and the tool that will be used (Terraform and Ansible)

Beside the linux FR we also want an NGINX one:

```yaml
---
category: configs
description: type functional_requirement with name nginx
invocation:
  description: Deploys Nginx on a linux vm
  image: stacklio/ansible-nginx
  tool: ansible
name: nginx
params:
  nginx_http_template_enable: true
  nginx_http_template:
    default:
      template_file: http/default.conf.j2
      conf_file_name: default.conf
      conf_file_location: /etc/nginx/conf.d/
      servers:
        server1:
          listen:
            listen_localhost:
              # ip: 0.0.0.0
              port: "8080"
          server_name: localhost
          error_page: /usr/share/nginx/html
          autoindex: false
          web_server:
            locations:
              default:
                location: /
                html_file_location: /usr/share/nginx/html
                html_file_name: index.html
                autoindex: false
            http_demo_conf: false
type: functional_requirement
```

This one is similar to the linux one, except that we use Ansible and define the parameters we need to execute the role.

Use these two documents as payload and POST them to the /functional_requirements endpoint.

#### Service

Services can be used to tell STACKL to combine functional requirements and apply one on top of the other. We create a service, which will make sure there is a Linux VM and Nginx deployed on it:

```yaml
---
name: webserver
type: service
category: items
functional_requirements:
- linux
- nginx
params: {}
```

Note that the order of the functional requirements is important, obviously we first need a virtual machine before we can deploy NGINX.

#### Stack Application Template

Finally we create a stack application template, this can combine different services. For this example we will only use one service, but we could also add more services if needed:

```yaml
---
name: web
type: stack_application_template
category: configs
services:
- webserver
policies: {}
```

## 3. Create the instance

Now that we have everything in place we can create our webserver, use the following command:

```json
stackl create instance --stack-application-template web --stack-infrastructure-template stackl -p '{"machine_name": "test", "instance_type": "t2.micro"}' demo_instance
```

This will initiate the creation of our stack instance, which is the result of combining a SAT (Stack Application Template) and a SIT (Stack Infrastructure Template). When we we want to create a Stack Instance, STACKL will first evaluate all the possible infrastructure targets where the application can be deployed. After finding a possible target, all the params are combined and added to the stack instance so they can be used in our automation code.

Here is the order of precedence for variables from least to greatest (the last listed variables winning prioritization):

```sh
Environment -> Location -> Zone -> Service -> Functional Requirement -> Supplied Params
```

Stackl will now use these variables in its invocations to create our instance. After a while we can see the status of our stack instance by using the GET /stack_instance/demo_instance, we should see the following:

```json
{
  "name": "demo_instance",
  "deleted": false,
  "instance_params": {
    "machine_name": "test",
    "instance_type": "t2.micro"
  },
  "instance_secrets": {},
  "services": {
    "webserver": [
      {
        "infrastructure_target": "production.ireland.eu-west-1-a",
        "provisioning_parameters": {
          "aws_region": "eu-west-1",
          "ami_name_value": "ubuntu/images/hvm-ssd/ubuntu-trusty-14.04-amd64-server-*",
          "nginx_http_template_enable": true,
          "nginx_http_template": {
            "default": {
              "template_file": "http/default.conf.j2",
              "conf_file_name": "default.conf",
              "conf_file_location": "/etc/nginx/conf.d/",
              "servers": {
                "server1": {
                  "listen": {
                    "listen_localhost": {
                      "port": "8080"
                    }
                  },
                  "server_name": "localhost",
                  "error_page": "/usr/share/nginx/html",
                  "autoindex": false,
                  "web_server": {
                    "locations": {
                      "default": {
                        "location": "/",
                        "html_file_location": "/usr/share/nginx/html",
                        "html_file_name": "index.html",
                        "autoindex": false
                      }
                    },
                    "http_demo_conf": false
                  }
                }
              }
            }
          },
          "machine_name": "test",
          "instance_type": "t2.micro"
        },
        "secrets": {
          "aws_access_key": "YWNjZXNzX2tleQ==",
          "aws_secret_key": "c2VjcmV0X2tleQ=="
        }
      }
    ]
  },
  "stack_infrastructure_template": "stackl",
  "stack_application_template": "web",
  "status": [
    {
      "functional_requirement": "linux",
      "infrastructure_target": "production.ireland.eu-west-1-a",
      "service": "webserver",
      "status": 0,
      "error_message": ""
    },
    {
      "functional_requirement": "nginx",
      "infrastructure_target": "production.ireland.eu-west-1-a",
      "service": "webserver",
      "status": 0,
      "error_message": ""
    }
  ],
  "type": "stack_instance",
  "category": "items"
}
```

Our Stack Instance is now ready, we should now be able to go to the VM and see the default NGINX welcome message.
