
package orchestration

### This policy is to ensure that the specified environment, location, and zone will only host one service exclusively
# Parameters: 
#	environment - the environment for which this is appropriate
#	location - the location for which this is appropriate
#	zone - the zone for which this is appropriate
# Note: TODO This is untested

exclusivity(application_placement_solutions){
	some i, j
	service1 = input.policy_input.services[i]
	service2 = input.policy_input.services[j]
	solution = application_placement_solutions[_]
	environment_service1 = split(solution[service1],".")[0]
	location_service1 = split(solution[service1],".")[1]
	zone_service1 = split(solution[service1],".")[2]
	environment_service2 = split(solution[service2],".")[0]
	location_service2 = split(solution[service2],".")[1]
	zone_service2 = split(solution[service2],".")[2]
	environment != environment_service1; environment_service1 != environment_service2
	location != location_service1; location_service1 != location_service2
	zone != zone_service1; zone_service1 != zone_service2
} 