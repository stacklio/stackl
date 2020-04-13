#This policy is used for multiple redundancy, through the value parameter
package orchestration
​
​
multiple_targets = x {
	service = input.policy_input.service
	amount = input.policy_input.amount
	count(input.services[service]) >= amount
	x = {service: array.slice(input.services[service], 0, amount)}
} else = x {
   x = {input.policy_input.service: []}
}
