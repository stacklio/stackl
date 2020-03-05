# this rego file contains all the policies that are active in stackl by default
package stackl.default_policies

# First policy: there is at least 1 infrastructure targets
are_available_targets = false {
    count(input.infrastructure_capabilities[0]) > 0
}
