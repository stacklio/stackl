# stackl_sdk.StackInfrastructureTemplatesApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_stack_infrastructure_template**](StackInfrastructureTemplatesApi.md#delete_stack_infrastructure_template) | **DELETE** /stack_infrastructure_templates/{document_name} | Delete Stack Infrastructure Template
[**get_stack_infrastructure_template_by_name**](StackInfrastructureTemplatesApi.md#get_stack_infrastructure_template_by_name) | **GET** /stack_infrastructure_templates/{document_name} | Get Stack Infrastructure Template By Name
[**get_stack_infrastructure_templates**](StackInfrastructureTemplatesApi.md#get_stack_infrastructure_templates) | **GET** /stack_infrastructure_templates | Get Stack Infrastructure Templates
[**post_stack_infrastructure_template**](StackInfrastructureTemplatesApi.md#post_stack_infrastructure_template) | **POST** /stack_infrastructure_templates | Post Stack Infrastructure Template
[**put_stack_infrastructure_template**](StackInfrastructureTemplatesApi.md#put_stack_infrastructure_template) | **PUT** /stack_infrastructure_templates | Put Stack Infrastructure Template

# **delete_stack_infrastructure_template**
> Object delete_stack_infrastructure_template(document_name, type_name)

Delete Stack Infrastructure Template

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackInfrastructureTemplatesApi()
document_name = 'document_name_example' # str | 
type_name = 'type_name_example' # str | 

try:
    # Delete Stack Infrastructure Template
    api_response = api_instance.delete_stack_infrastructure_template(document_name, type_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackInfrastructureTemplatesApi->delete_stack_infrastructure_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_name** | **str**|  | 
 **type_name** | **str**|  | 

### Return type

[**Object**](Object.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stack_infrastructure_template_by_name**
> StackInfrastructureTemplate get_stack_infrastructure_template_by_name(document_name)

Get Stack Infrastructure Template By Name

Returns a functional requirement

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackInfrastructureTemplatesApi()
document_name = 'document_name_example' # str | 

try:
    # Get Stack Infrastructure Template By Name
    api_response = api_instance.get_stack_infrastructure_template_by_name(document_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackInfrastructureTemplatesApi->get_stack_infrastructure_template_by_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_name** | **str**|  | 

### Return type

[**StackInfrastructureTemplate**](StackInfrastructureTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stack_infrastructure_templates**
> list[StackInfrastructureTemplate] get_stack_infrastructure_templates()

Get Stack Infrastructure Templates

Returns all functional requirements with a specific type

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackInfrastructureTemplatesApi()

try:
    # Get Stack Infrastructure Templates
    api_response = api_instance.get_stack_infrastructure_templates()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackInfrastructureTemplatesApi->get_stack_infrastructure_templates: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[StackInfrastructureTemplate]**](StackInfrastructureTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_stack_infrastructure_template**
> StackInfrastructureTemplate post_stack_infrastructure_template(body)

Post Stack Infrastructure Template

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackInfrastructureTemplatesApi()
body = stackl_sdk.StackInfrastructureTemplate() # StackInfrastructureTemplate | 

try:
    # Post Stack Infrastructure Template
    api_response = api_instance.post_stack_infrastructure_template(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackInfrastructureTemplatesApi->post_stack_infrastructure_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StackInfrastructureTemplate**](StackInfrastructureTemplate.md)|  | 

### Return type

[**StackInfrastructureTemplate**](StackInfrastructureTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_stack_infrastructure_template**
> StackInfrastructureTemplate put_stack_infrastructure_template(body)

Put Stack Infrastructure Template

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackInfrastructureTemplatesApi()
body = stackl_sdk.StackInfrastructureTemplate() # StackInfrastructureTemplate | 

try:
    # Put Stack Infrastructure Template
    api_response = api_instance.put_stack_infrastructure_template(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackInfrastructureTemplatesApi->put_stack_infrastructure_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StackInfrastructureTemplate**](StackInfrastructureTemplate.md)|  | 

### Return type

[**StackInfrastructureTemplate**](StackInfrastructureTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

