# stackl_sdk.ServicesApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_service**](ServicesApi.md#delete_service) | **DELETE** /services/{document_name} | Delete Service
[**get_service_by_name**](ServicesApi.md#get_service_by_name) | **GET** /services/{document_name} | Get Service By Name
[**get_services**](ServicesApi.md#get_services) | **GET** /services | Get Services
[**post_service**](ServicesApi.md#post_service) | **POST** /services | Post Service
[**put_service**](ServicesApi.md#put_service) | **PUT** /services | Put Service

# **delete_service**
> Object delete_service(document_name, type_name)

Delete Service

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.ServicesApi()
document_name = 'document_name_example' # str | 
type_name = 'type_name_example' # str | 

try:
    # Delete Service
    api_response = api_instance.delete_service(document_name, type_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ServicesApi->delete_service: %s\n" % e)
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

# **get_service_by_name**
> Service get_service_by_name(document_name)

Get Service By Name

Returns a functional requirement

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.ServicesApi()
document_name = 'document_name_example' # str | 

try:
    # Get Service By Name
    api_response = api_instance.get_service_by_name(document_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ServicesApi->get_service_by_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_name** | **str**|  | 

### Return type

[**Service**](Service.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_services**
> list[Service] get_services()

Get Services

Returns all functional requirements with a specific type

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.ServicesApi()

try:
    # Get Services
    api_response = api_instance.get_services()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ServicesApi->get_services: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Service]**](Service.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_service**
> Service post_service(body)

Post Service

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.ServicesApi()
body = stackl_sdk.Service() # Service | 

try:
    # Post Service
    api_response = api_instance.post_service(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ServicesApi->post_service: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Service**](Service.md)|  | 

### Return type

[**Service**](Service.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_service**
> Service put_service(body)

Put Service

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.ServicesApi()
body = stackl_sdk.Service() # Service | 

try:
    # Put Service
    api_response = api_instance.put_service(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ServicesApi->put_service: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Service**](Service.md)|  | 

### Return type

[**Service**](Service.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

