
package orchestration

### This policy is to ensure that two services are not on the same target
# Parameters: 
#	services - a list of services that should not be on the same target
# Note: TODO This is untested

same_zone(application_placement_solutions){
	some i, j
	service1 = input.policy_input.services[i]
	service2 = input.policy_input.service[j]
	solution[service1] == solution[service2]
} 