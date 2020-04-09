#This policy is used for multiple redundancy, through the value parameter
multiple_redundancy {
    value := 1
    count(infrastructure_targets[0]) >= value
}