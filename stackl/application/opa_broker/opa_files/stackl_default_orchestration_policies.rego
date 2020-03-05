###
### This package contains all the default policies for application orchestration on provided input data
###
package stackl.default_orchestration_policies

### Rule to determine if there are deployable targets
are_available_targets = true {
    count(data.infrastructure_targets[0]) > 0
}

### Rule to see if a service has one or more suitable infrastructure targets
service_target_match[service_target_pair] {
    service := data.services[_]
    target := data.infrastructure_targets[_]
     # service.resource_requirements[resource] iterates over keys. 
     # The array contains a true or false for each resource the target satisfies
     # the regex extracts the number from a string and converts it to an int
	satisfied_resource_array := [tgt_res_satisfies_srv | service.resource_requirements[resource]
                                    tgt_res_quantity := to_number(regex.find_n("\\d+", target.resources[resource], -1)[0])
                                    srv_res_quantity := to_number(regex.find_n("\\d+", service.resource_requirements[resource], -1)[0])
    								tgt_res_satisfies_srv := tgt_res_quantity >= srv_res_quantity]
    # checks if all values are true, if not, returns false
    all(satisfied_resource_array) = true
    service_target_pair := {service.id : target.id}
}

### Rule to see if the service has no suitable infrastructure targets
service_without_suitable_target[service.id] {
    service := data.services[_]
    set_of_targets := [ x | x := has_key(service_target_match[i], service.id)]
    count(set_of_targets) == 0
}

### Helper function for checking if a key is present
has_key(x, k) { _ = x[k] }
