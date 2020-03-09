###
### This package contains all the default policies for application orchestration on provided input data
###
package orchestration

import data.functions
import input.infrastructure_targets as infrastructure_targets
import input.services as services

### Rule to determine if there are deployable targets
are_available_targets {
    count(infrastructure_targets[0]) > 0
}

### Rule to see if a service has one or more suitable infrastructure targets
services_target_resources_match[service_target_pairs] {
    service := services[_]
    target := infrastructure_targets[_]
     # service.resource_requirements[resource] iterates over keys. 
     # The array contains a true or false for each resource the target satisfies
     # the regex extracts the number from a string and converts it to an int
	satisfied_resource_array := [tgt_res_satisfies_srv | service.resource_requirements[resource]
                                    tgt_res_quantity := to_number(regex.find_n("\\d+", target.resources[resource], -1)[0])
                                    srv_res_quantity := to_number(regex.find_n("\\d+", service.resource_requirements[resource], -1)[0])
    								tgt_res_satisfies_srv := tgt_res_quantity >= srv_res_quantity]
    # checks if all values are true, if not, returns false
    all(satisfied_resource_array) = true
    service_target_pairs := {service.id : target.id}
}

### Rule to see if the service has no suitable infrastructure targets
services_target_resources_mismatch[service.id] {
    service := services[_]
    set_of_targets := [ x | x := functions.has_key(services_target_resources_match[i], service.id)]
    count(set_of_targets) == 0
}
