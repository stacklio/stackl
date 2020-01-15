---
title: "Introduction"
kind: basic
weight: 1
---

**STACKL is an open-source software platform that enables users to flexibly model, describe, and automate their application orchestration.**
Writing good application code is difficult enough. 
But then succesfully and continuously deploying your darling app in your IT infrastructure opens up a whole other can of worms.
What other services do you need for your app? Where do you deploy them and how do you choose? Which IT resources can you use to test your development app? Which to run your production app?
Even more: how do you deploy your application? What orchestration tools do you use? Does it have the authorisation to access your resources? How do you manage the app after deployment?
You started of with the honest desire to just write some good code and now reality hits you with all kinds of concerns you want nothing to do with. That is where **STACKL** comes into play.

STACKL supports the autonomous configuration, coordination, and management of applications and IT infrastructure by:

* Forming the Single Source of Truth (SSOT) configuration data lookup store for your IT environment including infrastructure resources, application definitions, and their characteristics and services.
* Decoupling configuration data, automation strategy, and deployment targets thereby simplifying the automated infrastructure management for code and configuration tooling.
* Providing pluggable modules for backend systems, such as processing and data storage, to support different scalability and performance requirements and enable users to choose their prefered tools.

In essence, it allows to ***Model***, ***Describe***, and ***Automate*** your application orchestration workflow. Users are saved from  manual work each time they want to deploy their projects by automating and simplifying IT infrastructure selection, application specification, and choosing suitable orchestration tools. Users now simply model their available infrastructure, describe their desired applications, and specify the desired orchestration tools once. STACKL then transparantly and autonomously uses this information to correctly and efficiently orchestrate and automate applications in the available IT environment across their lifetime and managing dynamic changes.

See [STACKL slides](https://drive.google.com/open?id=10ZmqGU3pOc6EJyZpED4fMgav5pD01RztLkfSn3Jl9EA) for a short presentation about STACKL.

# Contributing

Contributions, issues, and feature requests are always more than welcome! Feel free to check the  [Github issues page](https://github.com/kefranabg/readme-md-generator/issues) if you want to contribute.

See [CONTRIBUTING](CONTRIBUTING.md) to get started.

Please also read the [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md).


# License

The code in this project is licensed under the [GLPv3](LICENSE) license.

# Acknowledgments

STACKL was initially created for in-house use by a DevOps company, [Nubera](https://www.nubera.eu/), who saw the need for platform to better provide  services to clients. After some time, it became clear that STACKL could be useful to the general DevOps community as well so the decision was made to spin it off as an open source project.
Hence, thanks to Nubera  and @Yannick Struyf who put in much of the hard initial work.
