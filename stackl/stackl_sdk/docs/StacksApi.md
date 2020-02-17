# stackl_sdk.StacksApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_stack_instance**](StacksApi.md#get_stack_instance) | **GET** /stacks/instances/{stack_instance_name} | Get Stack Instance
[**get_stack_instances**](StacksApi.md#get_stack_instances) | **GET** /stacks/instances | Get Stack Instances
[**post_stack_instance**](StacksApi.md#post_stack_instance) | **POST** /stacks/instances | Post Stack Instance
[**put_stack_instance**](StacksApi.md#put_stack_instance) | **PUT** /stacks/instances | Put Stack Instance

# **get_stack_instance**
> StackInstance get_stack_instance(stack_instance_name)

Get Stack Instance

Returns a stack instance with a specific name

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StacksApi()
stack_instance_name = 'stack_instance_name_example' # str | 

try:
    # Get Stack Instance
    api_response = api_instance.get_stack_instance(stack_instance_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StacksApi->get_stack_instance: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stack_instance_name** | **str**|  | 

### Return type

[**StackInstance**](StackInstance.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stack_instances**
> list[StackInstance] get_stack_instances()

Get Stack Instances

Returns all stack instances

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StacksApi()

try:
    # Get Stack Instances
    api_response = api_instance.get_stack_instances()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StacksApi->get_stack_instances: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[StackInstance]**](StackInstance.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_stack_instance**
> Object post_stack_instance(body)

Post Stack Instance

Creates a stack instance with a specific name

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StacksApi()
body = stackl_sdk.StackInstanceInvocation() # StackInstanceInvocation | 

try:
    # Post Stack Instance
    api_response = api_instance.post_stack_instance(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StacksApi->post_stack_instance: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StackInstanceInvocation**](StackInstanceInvocation.md)|  | 

### Return type

[**Object**](Object.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_stack_instance**
> Object put_stack_instance(body)

Put Stack Instance

Update a stack instance with the given name from a stack application template and stack infrastructure template, creating a new one if it does not yet exist

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StacksApi()
body = stackl_sdk.StackInstanceInvocation() # StackInstanceInvocation | 

try:
    # Put Stack Instance
    api_response = api_instance.put_stack_instance(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StacksApi->put_stack_instance: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StackInstanceInvocation**](StackInstanceInvocation.md)|  | 

### Return type

[**Object**](Object.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

