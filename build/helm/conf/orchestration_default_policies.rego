###
### This package contains all the default policies for application orchestration on provided input data
###
package orchestration

advanced_application_placement_solutions = solutions {
    unfiltered_application_placement_solutions = basic_application_placement_solution_sets
    part_filtered_application_placement_solutions = satisfies_additional_sat_policies(unfiltered_application_placement_solutions)
    filtered_application_placement_solutions = satisfies_additional_sit_policies(part_filtered_application_placement_solutions)
    solutions := filtered_application_placement_solutions
}

basic_application_placement_solution_sets = basic_application_placement {
    matches := {service: { target | target := targets_for_service[_][service] } | 
                targets_for_service[_][service]}
    basic_application_placement := object.union(all_services_empty, matches)
}

all_services_empty = res {
    res := { s: [] | input.services[s]}
}

#Rule: get basic suitable infrastructure target for the service
targets_for_service[set_of_suited_targets] {
    service := input.services[svc]
    target := input.infrastructure_targets[tgt]
    satisfies_resources(service, target)
    satisfies_functional_requirement(service, target)
    not satisfies_tags(input.required_tags, target)

    set_of_suited_targets := {svc: tgt}
}

#Function
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

#Function
satisfies_functional_requirement(service, target) {
    # Convert arrays to set
    fr := {x | x := service.functional_requirements[_]}
    cfg := {x | x := target.packages[_]}
    # Take the intersection to see if the cfg satisfies all the functional requirements
    fr & cfg == fr
}

#Function
satisfies_tags(required_tags, target) {
    some t
    required_tags[t] != target.tags[t]
    required_tags[t] != "all"
}

satisfies_additional_sat_policies(application_placement_solutions){
    true
}

satisfies_additional_sit_policies(application_placement_solutions){
    true
}
