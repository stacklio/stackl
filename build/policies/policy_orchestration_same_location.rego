
package orchestration

### This policy is to ensure that the given services are in the same location
# Parameters: 
#	services - a list of services that should be in the same location
# Note: TODO This is untested

same_zone(application_placement_solutions){
	some i, j
	service1 = input.policy_input.services[i]
	service2 = input.policy_input.service[j]
	solution = basic_application_placement_solution_sets[_]
	location_service1 = split(solution[service1],".")[1]
	location_service2 = split(solution[service2],".")[1]
	location_service1 == location_service2
} 