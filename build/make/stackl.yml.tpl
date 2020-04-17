http:
  port: 8080

datastore:
  type: LFS
  # Change this to the absolute path where your Stackl config and items are located
  lfs_volume: /example_database/

task_broker:
  type: Custom

message_channel:
  type: Redis

agent_broker:
  type: Local
  host: stackl-agent:50051

opa:
  # Change this to the absolute path where your OPA files are located ##TODO: make this a fixed spot somewhere
  opa_files_location: /build/example_policies