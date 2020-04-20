
package orchestration

### This policy is for a service that should be replicated a certain amount
# Parameters: 
#	service - the service that should be replicated
#	amount	- the amount of times the service should be replicated

replicas = x {
	service = input.policy_input.service
	amount = input.policy_input.amount
	count(input.services[service]) >= amount
	x = {service: array.slice(input.services[service], 0, amount)}
} else = x {
   x = {input.policy_input.service: []}
}