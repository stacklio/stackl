# stackl_sdk.FunctionalRequirementsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_functional_requirement**](FunctionalRequirementsApi.md#delete_functional_requirement) | **DELETE** /functional_requirements/{document_name} | Delete Functional Requirement
[**get_functional_requirement_by_name**](FunctionalRequirementsApi.md#get_functional_requirement_by_name) | **GET** /functional_requirements/{document_name} | Get Functional Requirement By Name
[**get_functional_requirements**](FunctionalRequirementsApi.md#get_functional_requirements) | **GET** /functional_requirements | Get Functional Requirements
[**post_functional_requirement**](FunctionalRequirementsApi.md#post_functional_requirement) | **POST** /functional_requirements | Post Functional Requirement
[**put_functional_requirement**](FunctionalRequirementsApi.md#put_functional_requirement) | **PUT** /functional_requirements | Put Functional Requirement

# **delete_functional_requirement**
> Object delete_functional_requirement(document_name, type_name)

Delete Functional Requirement

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.FunctionalRequirementsApi()
document_name = 'document_name_example' # str | 
type_name = 'type_name_example' # str | 

try:
    # Delete Functional Requirement
    api_response = api_instance.delete_functional_requirement(document_name, type_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FunctionalRequirementsApi->delete_functional_requirement: %s\n" % e)
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

# **get_functional_requirement_by_name**
> FunctionalRequirement get_functional_requirement_by_name(document_name)

Get Functional Requirement By Name

Returns a functional requirement

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.FunctionalRequirementsApi()
document_name = 'document_name_example' # str | 

try:
    # Get Functional Requirement By Name
    api_response = api_instance.get_functional_requirement_by_name(document_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FunctionalRequirementsApi->get_functional_requirement_by_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_name** | **str**|  | 

### Return type

[**FunctionalRequirement**](FunctionalRequirement.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_functional_requirements**
> list[FunctionalRequirement] get_functional_requirements()

Get Functional Requirements

Returns all functional requirements with a specific type

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.FunctionalRequirementsApi()

try:
    # Get Functional Requirements
    api_response = api_instance.get_functional_requirements()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FunctionalRequirementsApi->get_functional_requirements: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[FunctionalRequirement]**](FunctionalRequirement.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_functional_requirement**
> FunctionalRequirement post_functional_requirement(body)

Post Functional Requirement

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.FunctionalRequirementsApi()
body = stackl_sdk.FunctionalRequirement() # FunctionalRequirement | 

try:
    # Post Functional Requirement
    api_response = api_instance.post_functional_requirement(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FunctionalRequirementsApi->post_functional_requirement: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FunctionalRequirement**](FunctionalRequirement.md)|  | 

### Return type

[**FunctionalRequirement**](FunctionalRequirement.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_functional_requirement**
> FunctionalRequirement put_functional_requirement(body)

Put Functional Requirement

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.FunctionalRequirementsApi()
body = stackl_sdk.FunctionalRequirement() # FunctionalRequirement | 

try:
    # Put Functional Requirement
    api_response = api_instance.put_functional_requirement(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FunctionalRequirementsApi->put_functional_requirement: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FunctionalRequirement**](FunctionalRequirement.md)|  | 

### Return type

[**FunctionalRequirement**](FunctionalRequirement.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

