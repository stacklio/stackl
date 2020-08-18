#!/bin/bash
if [ -z "$STACKL_INSTANCE" ]
then
        echo "Verifying if environment variables have been set..."
        echo "STACKL_INSTANCE is empty"
        exit 1
fi

function get_stackl_instance_yml(){
  stackl get instance -o yaml "$1"
}

function get_stackl_instance(){
  stackl get instance -o json "$1"
}

function read_service_status(){
  echo "$1" | jq ".status[] | select(.service==\"$2\").status"
}

echo "Stackl deployment: "
echo Instance: "$STACKL_INSTANCE"

stackl_instance="$(get_stackl_instance "$STACKL_INSTANCE")"
export stackl_instance
services_names="$(echo "$stackl_instance" | jq -r '.services | to_entries[].key')"
export services_names

for service_name in $services_names; do
  echo "Checking Service: $service_name"
  service_status=$(read_service_status "$stackl_instance" "$service_name")
  export service_status
  case $service_status in
    0)
      echo "Stack instance $STACKL_INSTANCE: service $service_name is ready!"
      ;;
    1)
      get_stackl_instance_yml "$STACKL_INSTANCE"
      echo '---'
      echo "Stack instance $STACKL_INSTANCE: service $service_name failed!"
      exit 1
      ;;
    2)
      while [ "$service_status" -eq 2 ]; do
        echo "Stack instance is creating, waiting for service: $service_name ..."
        sleep 5
        stackl_instance=$(get_stackl_instance "$STACKL_INSTANCE")
        export stackl_instance
        service_status=$(read_service_status "$stackl_instance" "$service_name")
        export service_status
      done
      ;;
  esac
done
