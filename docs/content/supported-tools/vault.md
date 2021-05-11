---
title: Vault
kind: supported-tools
weight: 4
date: 2021-05-11 01:00:00 +0100
publishdate: 2021-05-11 00:00:00 +0000
expirydate: 2030-01-01 00:00:00 +0000
draft: false
tags: []
---

Vault is used to pass secrets to automation code, such as Ansible and Terraform. This sections documents how to add secrets to Stackl documents and how to configure Stackl to integrate with Vault.

## Stackl-Vault integration

To integrate Stackl with Vault, configuration must be added to both Stackl and Vault. Vault needs to be configured in such a way that Stackl job pods are allowed to authenticate with Vault and are able to retreive/write secrets in Vault.

Stackl needs to know which configuration is added to Vault in order to use the correct configuration. For example, a Vault role must be created, so this Vault role has to be referenced in the Stackl config.

### Vault configuration

As mentioned above, Stackl pods need to be able to authenticate with Vault. In order to do so, Stackl chose to use Vault's [Kubernetes Auth Method](https://www.vaultproject.io/docs/auth/kubernetes). This method can be used to authenticate with Vault using a Kubernetes Service Account Token, in this case, the service account token of the Stackl-agent service account.

For more information on how to configure Vault to use this authentication method, visit the [Vault documentation](https://www.vaultproject.io/docs/auth/kubernetes).

### Stackl configuration

Once all the Vault configuration is finished, a Stackl agent can be configured to use Vault. A Vault role and Vault mount point, both created in the previous step, need to be added as environment variables to the Stackl agent. The recommended installation for Stackl and its agents is Helm. 

For more information visit the [Stackl configuration](https://www.stackl.io/docs/latest/installation/configuration/#vault-secret-handler) and the [Stackl helm charts](https://github.com/stacklio/stackl-helm).

## References

* [Vault Kubernetes auth method](https://www.vaultproject.io/docs/auth/kubernetes)
* [Stackl configuration](https://www.stackl.io/docs/latest/installation/configuration/#vault-secret-handler)
* [Stackl helm charts](https://github.com/stacklio/stackl-helm)
