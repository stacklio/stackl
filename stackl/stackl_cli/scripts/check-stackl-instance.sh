#!/bin/bash
if [ -z "$STACKL_INSTANCE_NAME" ]
then
        echo "Verifying if environment variables have been set..."
        echo "STACKL_INSTANCE_NAME is empty"
        exit 1
fi

function get_stackl_instance_yml(){
  stackl get instance -o yaml "$1"
}

function get_stackl_instance(){
  stackl get instance -o json "$1"
}

function read_service_status(){
  echo "$1" | jq ".services.$2.status[].status"
}

echo "Stackl deployment: "
echo Instance: "$STACKL_INSTANCE_NAME"

stackl_instance="$(get_stackl_instance "$STACKL_INSTANCE_NAME")"
export stackl_instance
services_names="$(echo "$stackl_instance" | jq -r '.services | to_entries[].key')"
export services_names

for service_name in $services_names; do
  echo "Checking Service: $service_name"
  service_status=$(read_service_status "$stackl_instance" "$service_name")
  export service_status
  case $service_status in
    1)
      while [ "$service_status" -eq 1 ]; do
        echo "Stack instance is creating, waiting for service: $service_name ..."
        sleep 5
        stackl_instance=$(get_stackl_instance "$STACKL_INSTANCE_NAME")
        export stackl_instance
        service_status=$(read_service_status "$stackl_instance" "$service_name")
        export service_status
      done
      ;;
    2)
      echo "Stack instance $STACKL_INSTANCE_NAME: service $service_name is ready!"
      ;;
    3)
      get_stackl_instance_yml "$STACKL_INSTANCE_NAME"
      echo '---'
      echo "Stack instance $STACKL_INSTANCE_NAME: service $service_name failed!"
      exit 1
      ;;
  esac
done
