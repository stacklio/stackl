###
### This package contains all the default policies for application orchestration on provided input data
###
package orchestration

all_solutions = services_and_suitable_targets {
    matches := {service: { target | target := solution_set_per_service[_][service] } | 
                solution_set_per_service[_][service]}
    services_and_suitable_targets := object.union(all_services_empty, matches)
}

all_services_empty = res {
    res := { s: [] | input.services[s]}
}

## get suitable infrastructrure targets
solution_set_per_service[solution_sets] {
    service := input.services[svc]
    target := input.infrastructure_targets[tgt]
    satisfies_resources(service, target)
    satisfies_functional_requirement(service, target)
    solution_sets := {svc: tgt}
}

satisfies_resources(service, target) {
     # service.resource_requirements[resource] iterates over keys. 
     # The array contains a true or false for each resource the target satisfies
     # the value is converted to bytes by using the parse_bytes function
	satisfied_resource_array := [tgt_res_satisfies_srv | service.resource_requirements[resource]
                                    tgt_res_quantity := units.parse_bytes(target.resources[resource])
                                    srv_res_quantity := units.parse_bytes(service.resource_requirements[resource])
    								tgt_res_satisfies_srv := tgt_res_quantity >= srv_res_quantity]
    # checks if all values are true, if not, returns false
    all(satisfied_resource_array) = true
}

satisfies_functional_requirement(service, target) {
    # Convert arrays to set
    fr := {x | x := service.functional_requirements[_]}
    cfg := {x | x := target.config[_]}
    # Take the intersection to see if the cfg satisfies all the functional requirements
    fr & cfg == fr
}
