# coding: utf-8

"""
    FastAPI

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: 0.1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import re  # noqa: F401

# python 2 and python 3 compatibility library
import six

from stackl_sdk.api_client import ApiClient


class DocumentsApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def delete_document(self, type_name, document_name, **kwargs):  # noqa: E501
        """Delete Document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_document(type_name, document_name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str type_name: (required)
        :param str document_name: (required)
        :return: Object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.delete_document_with_http_info(type_name, document_name, **kwargs)  # noqa: E501
        else:
            (data) = self.delete_document_with_http_info(type_name, document_name, **kwargs)  # noqa: E501
            return data

    def delete_document_with_http_info(self, type_name, document_name, **kwargs):  # noqa: E501
        """Delete Document  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.delete_document_with_http_info(type_name, document_name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str type_name: (required)
        :param str document_name: (required)
        :return: Object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['type_name', 'document_name']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_document" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'type_name' is set
        if ('type_name' not in params or
                params['type_name'] is None):
            raise ValueError("Missing the required parameter `type_name` when calling `delete_document`")  # noqa: E501
        # verify the required parameter 'document_name' is set
        if ('document_name' not in params or
                params['document_name'] is None):
            raise ValueError("Missing the required parameter `document_name` when calling `delete_document`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'type_name' in params:
            path_params['type_name'] = params['type_name']  # noqa: E501
        if 'document_name' in params:
            path_params['document_name'] = params['document_name']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/documents/{type_name}/{document_name}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_document_by_type_and_name(self, type_name, document_name, **kwargs):  # noqa: E501
        """Get Document By Type And Name  # noqa: E501

        Returns a specific document with a type and name  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_document_by_type_and_name(type_name, document_name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str type_name: (required)
        :param str document_name: (required)
        :return: BaseDocument
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_document_by_type_and_name_with_http_info(type_name, document_name, **kwargs)  # noqa: E501
        else:
            (data) = self.get_document_by_type_and_name_with_http_info(type_name, document_name, **kwargs)  # noqa: E501
            return data

    def get_document_by_type_and_name_with_http_info(self, type_name, document_name, **kwargs):  # noqa: E501
        """Get Document By Type And Name  # noqa: E501

        Returns a specific document with a type and name  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_document_by_type_and_name_with_http_info(type_name, document_name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str type_name: (required)
        :param str document_name: (required)
        :return: BaseDocument
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['type_name', 'document_name']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_document_by_type_and_name" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'type_name' is set
        if ('type_name' not in params or
                params['type_name'] is None):
            raise ValueError("Missing the required parameter `type_name` when calling `get_document_by_type_and_name`")  # noqa: E501
        # verify the required parameter 'document_name' is set
        if ('document_name' not in params or
                params['document_name'] is None):
            raise ValueError("Missing the required parameter `document_name` when calling `get_document_by_type_and_name`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'type_name' in params:
            path_params['type_name'] = params['type_name']  # noqa: E501
        if 'document_name' in params:
            path_params['document_name'] = params['document_name']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/documents/{type_name}/{document_name}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='BaseDocument',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_documents_by_type(self, type_name, **kwargs):  # noqa: E501
        """Get Documents By Type  # noqa: E501

        Returns all documents with a specific type  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_documents_by_type(type_name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str type_name: (required)
        :return: list[BaseDocument]
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_documents_by_type_with_http_info(type_name, **kwargs)  # noqa: E501
        else:
            (data) = self.get_documents_by_type_with_http_info(type_name, **kwargs)  # noqa: E501
            return data

    def get_documents_by_type_with_http_info(self, type_name, **kwargs):  # noqa: E501
        """Get Documents By Type  # noqa: E501

        Returns all documents with a specific type  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_documents_by_type_with_http_info(type_name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str type_name: (required)
        :return: list[BaseDocument]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['type_name']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_documents_by_type" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'type_name' is set
        if ('type_name' not in params or
                params['type_name'] is None):
            raise ValueError("Missing the required parameter `type_name` when calling `get_documents_by_type`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'type_name' in params:
            path_params['type_name'] = params['type_name']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/documents/{type_name}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='list[BaseDocument]',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_types(self, **kwargs):  # noqa: E501
        """Get Types  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_types(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: Object
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_types_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_types_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_types_with_http_info(self, **kwargs):  # noqa: E501
        """Get Types  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_types_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :return: Object
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = []  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_types" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/documents/types', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='Object',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_document(self, body, **kwargs):  # noqa: E501
        """Post Document  # noqa: E501

        Create the document with a specific type and an optional name given in the payload  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_document(body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param BaseDocument body: (required)
        :return: BaseDocument
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.post_document_with_http_info(body, **kwargs)  # noqa: E501
        else:
            (data) = self.post_document_with_http_info(body, **kwargs)  # noqa: E501
            return data

    def post_document_with_http_info(self, body, **kwargs):  # noqa: E501
        """Post Document  # noqa: E501

        Create the document with a specific type and an optional name given in the payload  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_document_with_http_info(body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param BaseDocument body: (required)
        :return: BaseDocument
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_document" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `post_document`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/documents', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='BaseDocument',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def put_document(self, body, **kwargs):  # noqa: E501
        """Put Document  # noqa: E501

        UPDATES the document with a specific type and an optional name given in the payload  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.put_document(body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param BaseDocument body: (required)
        :return: BaseDocument
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.put_document_with_http_info(body, **kwargs)  # noqa: E501
        else:
            (data) = self.put_document_with_http_info(body, **kwargs)  # noqa: E501
            return data

    def put_document_with_http_info(self, body, **kwargs):  # noqa: E501
        """Put Document  # noqa: E501

        UPDATES the document with a specific type and an optional name given in the payload  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.put_document_with_http_info(body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param BaseDocument body: (required)
        :return: BaseDocument
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['body']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method put_document" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'body' is set
        if ('body' not in params or
                params['body'] is None):
            raise ValueError("Missing the required parameter `body` when calling `put_document`")  # noqa: E501

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/documents', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='BaseDocument',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
