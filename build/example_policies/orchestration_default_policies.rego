###
### This package contains all the default policies for application orchestration on provided input data
###
package orchestration

solutions = {"fulfilled": true, "services": result} {
	result := {s: targets |
		service := input.services[s]
		targets := targets_for_service(service)
	}

	empty_services := {tgt | tgt := result[_]; tgt == []}
	count(empty_services) == 0
}

else = {"fulfilled": false, "msg": msg} {
	result := {s: targets |
		service := input.services[s]
		targets := targets_for_service(service)
	}

	services_no_targets := { svc | tgt = result[svc]; tgt == []}

	msg := sprintf("Couldn't find a target for services %v", [services_no_targets])
}

#Rule: get basic suitable infrastructure target for the service
targets_for_service(service) = targets {
	targets := [tgt |
		target := input.infrastructure_targets[tgt]
		satisfies_resources(service, target)
		satisfies_functional_requirement(service, target)
		not satisfies_tags(input.required_tags, target)
	]
}

#Function
satisfies_resources(service, target) {
	# service.resource_requirements[resource] iterates over keys.
	# The array contains a true or false for each resource the target satisfies
	# the value is converted to bytes by using the parse_bytes function
	satisfied_resource_array := [tgt_res_satisfies_srv |
		service.resource_requirements[resource]
		tgt_res_quantity := units.parse_bytes(target.resources[resource])
		srv_res_quantity := units.parse_bytes(service.resource_requirements[resource])
		tgt_res_satisfies_srv := tgt_res_quantity >= srv_res_quantity
	]

	# checks if all values are true, if not, returns false
	all(satisfied_resource_array) = true
}

#Function
satisfies_functional_requirement(service, target) {
	# Convert arrays to set
	fr = {x | service.functional_requirements[x] }
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
