# stackl_sdk.StackApplicationTemplatesApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_stack_application_template**](StackApplicationTemplatesApi.md#delete_stack_application_template) | **DELETE** /stack_application_templates/{document_name} | Delete Stack Application Template
[**get_stack_application_template_by_name**](StackApplicationTemplatesApi.md#get_stack_application_template_by_name) | **GET** /stack_application_templates/{document_name} | Get Stack Application Template By Name
[**get_stack_application_templates**](StackApplicationTemplatesApi.md#get_stack_application_templates) | **GET** /stack_application_templates | Get Stack Application Templates
[**post_stack_application_template**](StackApplicationTemplatesApi.md#post_stack_application_template) | **POST** /stack_application_templates | Post Stack Application Template
[**put_stack_application_template**](StackApplicationTemplatesApi.md#put_stack_application_template) | **PUT** /stack_application_templates | Put Stack Application Template

# **delete_stack_application_template**
> Object delete_stack_application_template(document_name, type_name)

Delete Stack Application Template

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackApplicationTemplatesApi()
document_name = 'document_name_example' # str | 
type_name = 'type_name_example' # str | 

try:
    # Delete Stack Application Template
    api_response = api_instance.delete_stack_application_template(document_name, type_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackApplicationTemplatesApi->delete_stack_application_template: %s\n" % e)
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

# **get_stack_application_template_by_name**
> StackApplicationTemplate get_stack_application_template_by_name(document_name)

Get Stack Application Template By Name

Returns a functional requirement

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackApplicationTemplatesApi()
document_name = 'document_name_example' # str | 

try:
    # Get Stack Application Template By Name
    api_response = api_instance.get_stack_application_template_by_name(document_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackApplicationTemplatesApi->get_stack_application_template_by_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_name** | **str**|  | 

### Return type

[**StackApplicationTemplate**](StackApplicationTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stack_application_templates**
> list[StackApplicationTemplate] get_stack_application_templates()

Get Stack Application Templates

Returns all functional requirements with a specific type

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackApplicationTemplatesApi()

try:
    # Get Stack Application Templates
    api_response = api_instance.get_stack_application_templates()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackApplicationTemplatesApi->get_stack_application_templates: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[StackApplicationTemplate]**](StackApplicationTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_stack_application_template**
> StackApplicationTemplate post_stack_application_template(body)

Post Stack Application Template

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackApplicationTemplatesApi()
body = stackl_sdk.StackApplicationTemplate() # StackApplicationTemplate | 

try:
    # Post Stack Application Template
    api_response = api_instance.post_stack_application_template(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackApplicationTemplatesApi->post_stack_application_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StackApplicationTemplate**](StackApplicationTemplate.md)|  | 

### Return type

[**StackApplicationTemplate**](StackApplicationTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_stack_application_template**
> StackApplicationTemplate put_stack_application_template(body)

Put Stack Application Template

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.StackApplicationTemplatesApi()
body = stackl_sdk.StackApplicationTemplate() # StackApplicationTemplate | 

try:
    # Put Stack Application Template
    api_response = api_instance.put_stack_application_template(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StackApplicationTemplatesApi->put_stack_application_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StackApplicationTemplate**](StackApplicationTemplate.md)|  | 

### Return type

[**StackApplicationTemplate**](StackApplicationTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

