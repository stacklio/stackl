###
### This package contains all the default policies for application orchestration on provided input data
###
package orchestration

import data.functions
import input.infrastructure_targets as infrastructure_targets
import input.services as services

### Rule to create a solution set for each service
solution_set_per_service = solutions {
    matched_services := services_targets_resources_match[_]
    unmatched_services := services_target_resources_no_match[_]
    solutions := functions.merge_objects(matched_services, {services_target_resources_no_match[service]:[]})
} else = solutions{
    solutions := services_targets_resources_match[_]
}

### Rule to see determine infrastructure targets for all services
## Object Comprehension { <key>: <term> | <body> } with a nested set comprehension { <term> | <body> }
services_targets_resources_match[services_and_suitable_targets] {
    services_and_suitable_targets := {service: { target | target := services_targets_resources_match_helper[_][service] } | 
  services_targets_resources_match_helper[_][service]}
}

### Rule to see if the service has no suitable infrastructure targets
services_target_resources_no_match[service.id] {
    service := services[_]
    services_targets_resources_match[services_and_suitable_targets]
    not functions.has_key(services_and_suitable_targets, service.id)
}

## Help Rule to see if a service has one or more suitable infrastructure targets
services_targets_resources_match_helper[service_target_pairs] {
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