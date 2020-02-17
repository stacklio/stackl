# stackl_sdk.DocumentsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_document**](DocumentsApi.md#delete_document) | **DELETE** /documents/{type_name}/{document_name} | Delete Document
[**get_document_by_type_and_name**](DocumentsApi.md#get_document_by_type_and_name) | **GET** /documents/{type_name}/{document_name} | Get Document By Type And Name
[**get_documents_by_type**](DocumentsApi.md#get_documents_by_type) | **GET** /documents/{type_name} | Get Documents By Type
[**get_types**](DocumentsApi.md#get_types) | **GET** /documents/types | Get Types
[**post_document**](DocumentsApi.md#post_document) | **POST** /documents | Post Document
[**put_document**](DocumentsApi.md#put_document) | **PUT** /documents | Put Document

# **delete_document**
> Object delete_document(type_name, document_name)

Delete Document

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.DocumentsApi()
type_name = 'type_name_example' # str | 
document_name = 'document_name_example' # str | 

try:
    # Delete Document
    api_response = api_instance.delete_document(type_name, document_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->delete_document: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type_name** | **str**|  | 
 **document_name** | **str**|  | 

### Return type

[**Object**](Object.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_by_type_and_name**
> BaseDocument get_document_by_type_and_name(type_name, document_name)

Get Document By Type And Name

Returns a specific document with a type and name

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.DocumentsApi()
type_name = 'type_name_example' # str | 
document_name = 'document_name_example' # str | 

try:
    # Get Document By Type And Name
    api_response = api_instance.get_document_by_type_and_name(type_name, document_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->get_document_by_type_and_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type_name** | **str**|  | 
 **document_name** | **str**|  | 

### Return type

[**BaseDocument**](BaseDocument.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_documents_by_type**
> list[BaseDocument] get_documents_by_type(type_name)

Get Documents By Type

Returns all documents with a specific type

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.DocumentsApi()
type_name = 'type_name_example' # str | 

try:
    # Get Documents By Type
    api_response = api_instance.get_documents_by_type(type_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->get_documents_by_type: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type_name** | **str**|  | 

### Return type

[**list[BaseDocument]**](BaseDocument.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_types**
> Object get_types()

Get Types

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.DocumentsApi()

try:
    # Get Types
    api_response = api_instance.get_types()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->get_types: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Object**](Object.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_document**
> BaseDocument post_document(body)

Post Document

Create the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.DocumentsApi()
body = stackl_sdk.BaseDocument() # BaseDocument | 

try:
    # Post Document
    api_response = api_instance.post_document(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->post_document: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BaseDocument**](BaseDocument.md)|  | 

### Return type

[**BaseDocument**](BaseDocument.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_document**
> BaseDocument put_document(body)

Put Document

UPDATES the document with a specific type and an optional name given in the payload

### Example
```python
from __future__ import print_function
import time
import stackl_sdk
from stackl_sdk.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = stackl_sdk.DocumentsApi()
body = stackl_sdk.BaseDocument() # BaseDocument | 

try:
    # Put Document
    api_response = api_instance.put_document(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->put_document: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BaseDocument**](BaseDocument.md)|  | 

### Return type

[**BaseDocument**](BaseDocument.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

