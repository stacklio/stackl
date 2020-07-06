package replicas
solutions = {"fulfilled": true, "services": result} {

  not input.parameters.exclusive
  result = {service_key: service_targets |
          amount := input.parameters.services[service_key]
          targets := input.services[service_key]
          count(targets) >= amount
          service_targets := array.slice(targets, 0, amount)
  }
  # Check if each service has targets
  count(input.services) == count(result)
}
else = {"fulfilled": false, "msg": msg} {
  msg := sprintf("Not enough targets for services %v", [input.services])
}
