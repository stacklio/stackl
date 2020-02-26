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

This tutorial will help you understand how STACKL works by setting up a virtual machine with Terraform, and deploying 
Nginx on this machine with Ansible.

## Prerequisites

* Stackl
* Docker (or another way to build images)

## 1. Writing the Terraform and Ansible code for use by Stackl

STACKL can execute Terraform and Ansible code by running it in containers. This means we have to write our code, get the
variables from STACKL and bake it into a Docker image. We will start by making our Terraform image.

### Terraform

In this example we will create a virtual machine on vSphere, but we could deploy a virtual machine anywhere as long as
we can access it from where stackl is running and we defined an output variable "hosts" (More about this later). If you
are unfamiliar with Terraform it is recommended you follow the (getting started guide)[https://learn.hashicorp.com/terraform/getting-started/install]

First we'll write the code:

```hcl
terraform {
  backend "http" {
  }
}

variable "stackl_host" {
  type = string
}

variable "stackl_stack_instance" {
    type = string
}

variable "stackl_service" {
    type = string
}

data "http" "example" {
  url = "http://${var.stackl_host}/stack_instances/${var.stackl_stack_instance}"
  request_headers = {
    "Accept" = "application/json"
  }
}

locals {
  service_values = jsondecode(data.http.example.body)["services"][var.stackl_service]
}

provider "vsphere" {
  user           = local.service_values.provisioning_parameters.username
  password       = local.service_values.provisioning_parameters.password
  vsphere_server = local.service_values.provisioning_parameters.hostname

  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name = local.service_values.provisioning_parameters.datacenter
}

data "vsphere_datastore" "datastore" {
  name          = local.service_values.provisioning_parameters.datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = local.service_values.provisioning_parameters.cluster
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name          = local.service_values.provisioning_parameters.network
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_virtual_machine" "template" {
  name          = local.service_values.provisioning_parameters.vmw_image
  datacenter_id = data.vsphere_datacenter.dc.id
}

resource "vsphere_virtual_machine" "vm" {
  count =  local.service_values.provisioning_parameters.replicas
  name = format("%s-%s", local.service_values.provisioning_parameters.vm_name, count.index)
  folder = local.service_values.provisioning_parameters.folder
  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id
  num_cpus = 2
  memory   = 2048
  guest_id = data.vsphere_virtual_machine.template.guest_id

  firmware = data.vsphere_virtual_machine.template.firmware

  network_interface {
    network_id = data.vsphere_network.network.id
    adapter_type = data.vsphere_virtual_machine.template.network_interface_types[0]
  }

  disk {
    label            = "disk0"
    size             = "30"
    eagerly_scrub    = data.vsphere_virtual_machine.template.disks.0.eagerly_scrub
    thin_provisioned = data.vsphere_virtual_machine.template.disks.0.thin_provisioned
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.template.id
    customize {
      linux_options {
        domain = "vsphere.local"
        host_name = format("%s-%s", local.service_values.provisioning_parameters.vm_name, count.index)
      }
      network_interface {}
    }
  }
}

output "hosts" {
  value = vsphere_virtual_machine.vm.*.default_ip_address
}
```

Pay attention to the following:

1) The remote backend is set to http because we will save the Terraform statefile there.
2) We have 3 variables: stackl_host, stackl_stack_instance and stackl_service. These will be passed to the container that is running Terraform as environment variables.
3) The data resource data.http.example gets the stack-instance data from stackl, so we can use it's key-value pairs.

put this file in a directory (name it main.tf) and create a new file called `Dockerfile`, and add following content to this file:

```Dockerfile
FROM hashicorp/terraform:light

COPY main.tf main.tf

ENTRYPOINT []
CMD terraform init -backend-config="address=http://${TF_VAR_stackl_host}/terraform/${TF_VAR_stackl_stack_instance}" \
    && terraform apply --auto-approve
```

Now build the terraform image with the following command (assuming you use Docker):
```sh
docker build -t stacklio/terraform-vm .
```

Now that the Terraform ansible image is ready we can start with creating the Ansible one.

### Ansible

For this example we want to install Nginx on our machines by using the official nginx role:

https://github.com/nginxinc/ansible-role-nginx

Make a new directory, and in this directory create a `roles` directory and clone the repository in this roles directory (name it nginx). Besides that create a `main.yml` file and a `Dockerfile`. You should now have the following structure.

```sh
.
├── Dockerfile
├── main.yml
└── roles
    └── nginx
```

Add the following to the main.yml file:

```yml
---
- hosts: "{{ stackl_service }}"
  become: true
  roles:
    - role: nginx
  vars:
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
                port: "{{ provisioning_parameters['port'] }}"
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
```

This will install Nginx by using the role we cloned earlier. It will expose it on the port provided withing Stackl.

Next use this Dockerfile to build the image:

```Dockerfile
FROM stacklio/ansible-base

COPY roles .
COPY main.yml .
```

We start from an ansible-base image already provided by STACKL, this already has ansible and provides the STACKL ansible inventory so we can easily connect to our hosts and get variables from STACKL for use within our playbook.

Build the image:

```sh
docker build -t stacklio/ansible-nginx
```

## 2. Create the STACKL documents

Now that we have our automation code in place, we need to model both our infrastructure and our application in STACKL, we start by modelling our infrastructure.

### Infrastructure

To model our infrastructure we make use of three types of documents:

* Environment
* Location
* Zone

For this example we create a `production` environment which will look like this and contains mostly information about our VMware environment:

```json
{
    "category": "configs",
    "description": "production environment",
    "name": "production",
    "params": {
        "datastore": "vsanDatastore",
        "hostname": "vsphere.local",
        "password": "password",
        "username": "administrator@vsphere.local"
    },
    "type": "environment"
}
```

We define a location, in this case it is where our datacenter is located:

```json
{
    "description": "Brussels DC",
    "type": "location",
    "name": "brussels",
    "category": "configs",
    "params": {
        "datacenter": "DC01"
    }
}
```

Finally we define a zone, for our example we choose a cluster. We also add which configs are possible in this zone:

```json
{
  "description": "Our First Cluster",
  "type": "zone",
  "name": "cluster1",
  "category": "configs",
  "params": {
    "cluster": "CL01",
    "CPU": "4GHz",
    "RAM": "4GB",
    "config": [
      "linux",
      "nginx"
    ],
    "network": "VMXnetwork"
  }
}
```

For these documents use the /documents endpoint and upload them. (Or put them in the right directory if you make use of the LocalFileSystem option)

Combine these documents in a stack infrastructure template, this way you can define all the possible targets in your organization.

POST the following payload to the /stack_infrastructure_template endpoint:

```json
{
    "category": "configs",
    "description": "",
    "infrastructure_capabilities": {},
    "infrastructure_targets": [
        {
            "environment": "production",
            "location": "brussels",
            "zone": "cluster1"
        }
    ],
    "name": "stackl",
    "type": "stack_infrastructure_template"
}
```

### Application

Now that we have defined our infrastructure we need to model our "application". An application in Stackl can be an actual application, but it can also be something that can be provisioned E.G. A virtual machine. For our webserver we need two components. A virtual machine, with linux installed and our webserver software, in this case Nginx. We model these two as functional requirements.

#### Functional Requirements

Functional requirements in STACKL define what will be executed to create something, see the following example:

```json
{
    "category": "configs",
    "description": "type functional_requirement with name linux",
    "invocation": {
        "description": "Deploys a Linux VM",
        "image": "stacklio/terraform-vm",
        "tool": "terraform"
    },
    "name": "linux",
    "params": {
        "aws_ami": "ami-12345",
        "vmw_image": "ubuntu1804_template_vmw"
    },
    "type": "functional_requirement"
}
```

Just like Environments, Locations and Zones, Functional Requirements also have params, in our case it defines the name of our ubuntu template in vSphere, but if we made changes to our Terraform configuration, we could also support for example AWS EC2 and add the ami that should be used. 

Every FR (Functional Requirement) has an invocation part. This consists out of a description, the image that will be used (The ones we build earlier) and the tool that will be used (Terraform and Ansible)

Beside the linux FR we also want an NGINX one:

```json
{
    "category": "configs",
    "description": "type functional_requirement with name nginx",
    "invocation": {
        "description": "Deploys nginx on a linux vm",
        "image": "stacklio/ansible-nginx",
        "tool": "ansible"
    },
    "name": "nginx",
    "params": {
        "port": "8080"
    },
    "type": "functional_requirement"
}
```

This one is similar to the linux one, except that we use ansible and define the default port that we want to expose our webserver on.

Use these two documents as payload and POST them to the /functional_requirements endpoint.

#### Service

Services can be used to tell STACKL to combine functional requirements and apply one on top of the other. We create a service, which will make sure there is a linux VM and nginx deployed on it:

```json
{
    "name": "webserver",
    "type": "service",
    "category": "items",
    "functional_requirements": ["linux", "nginx"],
    "non_functional_requirements": {
        "CPU": "1GHz",
        "RAM": "2GB"
    },
    "params": {
        "webserver": "nginx"
    }
}
```

Note that the order of the functional requirements is important, obviously we first need a virtual machine before we can deploy NGINX.

The non functional requirements define what is needed for this service. We expect to have at least 1GHZ of compute and 2GB of RAM. This is why we defined in our zone that we can have at most 4GHZ and 4GB.

#### Stack Application Template

Finally we create a stack application template, this can combine different services, for this example we will only use one service, but we could also add more services if needed (a good example would be a database):

```json
{
    "name": "web",
    "type": "stack_application_template",
    "category": "configs",
    "services": ["webserver"],
    "extra_functional_requirements": {}
}
```

## 3. Create the instance

Now that we have everything in place we can create our webserver, use the following payload:

```json
{
  "params": {
    "vm_name": "example",
    "replicas": "1",
    "folder": "vsphere_folder"
  },
  "connection_credentials": {
    "username": "ubuntu",
    "password": "ubuntu"
  },
  "stack_infrastructure_template": "stackl",
  "stack_application_template": "web",
  "stack_instance_name": "demo_instance"
}
```

and POST it to /stack_instances, this will initiate the creation of our Stack Instance. Which is the result of combining a SAT (Stack Application Template) and a SIT (Stack Infrastructure Template). When we we want to create a Stack Instance, STACKL will first evaluate all the possible infrastructure targets where the application can be deployed. After finding a possible targets, all the params will be combined and added to the stack instance so they can be used in our automation code. Repeating keys will be overwritten in the following order:

```sh
Environment -> Location -> Zone -> Service -> Functional Requirement -> Supplied Params
```

Which means that if we define the same variable in Environment and in Service, the one from Service will be used.

The connection credentials will be used to ssh onto our server.

Stackl will now use these variables in its invocations to create our instance. After a while we can see the status of our stack instance by using the GET /stack_instance/demo_instance, we should see the following:

```json
{
    "category": "items",
    "deleted": false,
    "name": "demo_instance",
    "services": {
        "webserver": {
            "connection_credentials": {
                "password": "ubuntu",
                "username": "ubuntu"
            },
            "hosts": [
                "10.10.8.156"
            ],
            "infrastructure_target": "production.brussels.cluster1",
            "provisioning_parameters": {
                "CPU": "4GHz",
                "RAM": "4GB",
                "aws_ami": "ami-12345",
                "cluster": "CL01",
                "config": [
                    "linux",
                    "nginx"
                ],
                "datacenter": "DC01",
                "datastore": "vsanDatastore",
                "folder": "vsphere_folder",
                "hostname": "vsphere.local",
                "network": "VMXnetwork",
                "password": "password",
                "port": "8080",
                "replicas": "1",
                "username": "administrator@vsphere.local",
                "vm_name": "example",
                "vmw_image": "ubuntu1804_template_vmw",
                "webserver": "nginx"
            },
            "status": [
                {
                    "error_message": "",
                    "functional_requirement": "nginx",
                    "status": 2
                }
            ]
        }
    },
    "type": "stack_instance"
}
```

Our Stack Instance is now ready, we should now be able to go to

```sh
curl 10.10.8.156:8080
```

and see the default NGINX welcome message.

