import boto3
from botocore.client import BaseClient, Paginator
from botocore.paginate import PageIterator
from io import BytesIO
from logging import Logger
from pathlib import Path
from pypomes_core import Mimetype
from typing import Any, BinaryIO

from .s3_common import (
    S3Engine, S3Param, _get_param, _get_params, _normalize_tags, _except_msg
)


def get_client(errors: list[str],
               logger: Logger = None) -> BaseClient:
    """
    Obtain and return a *AWS* client object.

    :param errors: incidental error messages
    :param logger: optional logger
    :return: the AWS client object
    """
    # initialize the return variable
    result: BaseClient | None = None

    # retrieve the access parameters
    aws_params: dict[S3Param, Any] = _get_params(engine=S3Engine.AWS)

    # obtain the AWS client
    try:
        result = boto3.client(service_name="s3",
                              region_name=aws_params.get(S3Param.REGION_NAME),
                              use_ssl=aws_params.get(S3Param.SECURE_ACCESS),
                              verify=False,
                              endpoint_url=aws_params.get(S3Param.ENDPOINT_URL),
                              aws_access_key_id=aws_params.get(S3Param.ACCESS_KEY),
                              aws_secret_access_key=aws_params.get(S3Param.SECRET_KEY))
        if logger:
            logger.debug(msg="AWS client created")

    except Exception as e:
        errors.append(_except_msg(exception=e,
                                  engine=S3Engine.AWS))
    return result


def startup(errors: list[str],
            bucket: str,
            logger: Logger = None) -> bool:
    """
    Prepare the *AWS* client for operations.

    This function should be called just once, at startup,
    to make sure the interaction with the S3 service is fully functional.

    :param errors: incidental error messages
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param logger: optional logger
    :return: *True* if service is fully functional, *False* otherwise
    """
    # initialize the return variable
    result: bool = False

    # obtain a client
    client: BaseClient = get_client(errors=errors,
                                    logger=logger)
    # was the client obtained ?
    if client:
        # yes, proceed
        try:
            client.head_bucket(Bucket=bucket)
            result = True
            if logger:
                logger.debug(msg=f"Started AWS, bucket '{bucket}' asserted")
        except Exception as e1:
            # log the exception and try to create a bucket
            errors.append(_except_msg(exception=e1,
                                      engine=S3Engine.AWS))
            try:
                client.create_bucket(Bucket=bucket)
                result = True
                if logger:
                    logger.debug(msg=f"Started AWS, bucket '{bucket}' created")
            except Exception as e2:
                errors.append(_except_msg(exception=e2,
                                          engine=S3Engine.AWS))
    return result


def data_retrieve(errors: list[str],
                  identifier: str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  data_range: tuple[int, int] = None,
                  client: BaseClient = None,
                  logger: Logger = None) -> bytes:
    """
    Retrieve data from the *AWS* store.

    :param errors: incidental error messages
    :param identifier: the data identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the data from
    :param data_range: the begin-end positions within the data (in bytes, defaults to *None* - all bytes)
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: the bytes retrieved, or *None* if error or data not found
    """
    # initialize the return variable
    result: bytes | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    # was the client obtained ?
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        # retrieve the data
        obj_range: str = f"bytes={data_range[0]}-{data_range[1]}" if data_range else None
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_key: str = obj_path.as_posix()
            else:
                obj_key: str = identifier
            reply: dict[str: Any] = client.get_object(Bucket=bucket,
                                                      Key=obj_key,
                                                      Range=obj_range)
            result = reply["Body"]
            if logger:
                logger.debug(msg=f"Retrieved '{obj_key}', bucket '{bucket}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not hasattr(e, "code") or e.code != "NoSuchKey":
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.AWS))
    return result


def data_store(errors: list[str],
               identifier: str,
               data: bytes | str | BinaryIO,
               bucket: str = None,
               prefix: str | Path = None,
               length: int = None,
               mimetype: Mimetype | str = Mimetype.BINARY,
               tags: dict[str, str] = None,
               client: BaseClient = None,
               logger: Logger = None) -> bool:
    """
    Store *data* at the *AWS* store.

    In case *length* cannot be determined, it should be set to *None*.

    :param errors: incidental error messages
    :param identifier: the data identifier
    :param data: the data to store
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param length:  the length of the data
    :param prefix: optional path specifying the location to store the file at
    :param mimetype: the data mimetype
    :param tags: optional metadata tags describing the file
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: *True* if the data was successfully stored, *False* otherwise
    """
    # initialize the return variable
    result: bool = False

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        bin_data: BinaryIO
        if isinstance(data, BinaryIO):
            bin_data = data
        else:
            bin_data = BytesIO(data) if isinstance(data, bytes) else \
                       BytesIO(bytes(data, "utf-8"))
            bin_data.seek(0)

        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_key: str = obj_path.as_posix()
            else:
                obj_key: str = identifier
            if isinstance(mimetype, Mimetype):
                mimetype = mimetype.value
            client.put_object(Body=bin_data,
                              Bucket=bucket,
                              ContentLength=length,
                              ContentType=mimetype,
                              Key=obj_key,
                              Metadata=_normalize_tags(tags))
            if logger:
                logger.debug(msg=(f"Stored '{obj_key}', bucket '{bucket}', "
                                  f"content type '{mimetype}', tags '{tags}'"))
            result = True
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.AWS))
    return result


def file_retrieve(errors: list[str],
                  identifier: str,
                  filepath: Path | str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  client: BaseClient = None,
                  logger: Logger = None) -> Any:
    """
    Retrieve a file from the *AWS* store.

    :param errors: incidental error messages
    :param identifier: the file identifier, tipically a file name
    :param filepath: the path to save the retrieved file at
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the file from
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: information about the file retrieved, or *None* if error or file not found
    """
    # initialize the return variable
    result: Any = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_key: str = obj_path.as_posix()
            else:
                obj_key: str = identifier
            file_path: str = Path(filepath).as_posix()
            result = client.download_file(Bucket=bucket,
                                          Filename=file_path,
                                          Key=obj_key)
            if logger:
                logger.debug(msg=f"Retrieved '{obj_key}', bucket '{bucket}', to '{file_path}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not hasattr(e, "code") or e.code != "NoSuchKey":
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.AWS))
    return result


def file_store(errors: list[str],
               identifier: str,
               filepath: Path | str,
               mimetype: Mimetype | str,
               bucket: str = None,
               prefix: str | Path = None,
               tags: dict[str, str] = None,
               client: BaseClient = None,
               logger: Logger = None) -> bool:
    """
    Store a file at the *AWS* store.

    :param errors: incidental error messages
    :param identifier: the file identifier, tipically a file name
    :param filepath: optional path specifying where the file is
    :param mimetype: the file mimetype
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to store the file at
    :param tags: optional metadata tags describing the file
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: *True* if the file was successfully stored, *False* otherwise
    """
    # initialize the return variable
    result: bool = False

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)

        extra_args: dict[str, Any] | None = None
        if mimetype or tags:
            extra_args = {}
            if mimetype:
                if isinstance(mimetype, Mimetype):
                    mimetype = mimetype.value
                extra_args["ContentType"] = mimetype
            if tags:
                extra_args["Metadata"] = _normalize_tags(tags)

        # store the file
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_key: str = obj_path.as_posix()
            else:
                obj_key: str = identifier
            file_path: str = Path(filepath).as_posix()
            client.upload_file(Filename=file_path,
                               Bucket=bucket,
                               Key=obj_key,
                               ExtraArgs=extra_args)
            if logger:
                logger.debug(msg=(f"Stored '{obj_key}', bucket '{bucket}', "
                                  f"from '{file_path}', content type '{mimetype}', tags '{tags}'"))
            result = True
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.AWS))
    return result


def item_get_info(errors: list[str],
                  identifier: str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  client: BaseClient = None,
                  logger: Logger = None) -> dict[str, Any]:
    """
    Retrieve and return information about an item in the *AWS* store.

    The item might be interpreted as unspecified data, a file, or an object.
    The information returned is shown below. Please refer to the published *AWS*
    documentation for the meaning of any of these attributes.
    {
        'DeleteMarker': True|False,
        'LastModified': datetime(2015, 1, 1),
        'VersionId': 'string',
        'RequestCharged': 'requester',
        'ETag': 'string',
        'Checksum': {
            'ChecksumCRC32': 'string',
            'ChecksumCRC32C': 'string',
            'ChecksumSHA1': 'string',
            'ChecksumSHA256': 'string'
        },
        'ObjectParts': {
            'TotalPartsCount': 123,
            'PartNumberMarker': 123,
            'NextPartNumberMarker': 123,
            'MaxParts': 123,
            'IsTruncated': True|False,
            'Parts': [
                {
                    'PartNumber': 123,
                    'Size': 123,
                    'ChecksumCRC32': 'string',
                    'ChecksumCRC32C': 'string',
                    'ChecksumSHA1': 'string',
                    'ChecksumSHA256': 'string'
                },
            ]
        },
        'StorageClass': 'STANDARD' | 'REDUCED_REDUNDANCY' | 'STANDARD_IA' | 'ONEZONE_IA' |
                        'INTELLIGENT_TIERING' | 'GLACIER' | 'DEEP_ARCHIVE' | 'OUTPOSTS' |
                        'GLACIER_IR' | 'SNOW' | 'EXPRESS_ONEZONE',
        'ObjectSize': 123
    }

    :param errors: incidental error messages
    :param identifier: the item identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying where to locate the item
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: information about the item, or *None* if error or item not found
    """
    # initialize the return variable
    result: dict[str, Any] | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_key: str = obj_path.as_posix()
            else:
                obj_key: str = identifier
            result = client.get_object_attributes(Bucket=bucket,
                                                  Key=obj_key)
            if logger:
                logger.debug(msg=f"Got info for '{obj_key}', bucket '{bucket}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not hasattr(e, "code") or e.code != "NoSuchKey":
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.AWS))
    return result


def item_get_tags(errors: list[str],
                  identifier: str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  client: BaseClient = None,
                  logger: Logger = None) -> dict[str, str]:
    """
    Retrieve and return the existing metadata tags for an item in the *AWS* store.

    The item might be interpreted as unspecified data, a file, or an object.
    If item has no associated metadata tags, an empty *dict* is returned.
    The information returned by the native invocation is shown below. The *dict* returned is the
    value of the *Metadata* attribute. Please refer to the published *AWS* documentation
    for the meaning of any of these attributes.
    {
        'DeleteMarker': True|False,
        'AcceptRanges': 'string',
        'Expiration': 'string',
        'Restore': 'string',
        'ArchiveStatus': 'ARCHIVE_ACCESS'|'DEEP_ARCHIVE_ACCESS',
        'LastModified': datetime(2015, 1, 1),
        'ContentLength': 123,
        'ChecksumCRC32': 'string',
        'ChecksumCRC32C': 'string',
        'ChecksumSHA1': 'string',
        'ChecksumSHA256': 'string',
        'ETag': 'string',
        'MissingMeta': 123,
        'VersionId': 'string',
        'CacheControl': 'string',
        'ContentDisposition': 'string',
        'ContentEncoding': 'string',
        'ContentLanguage': 'string',
        'ContentType': 'string',
        'Expires': datetime(2015, 1, 1),
        'WebsiteRedirectLocation': 'string',
        'ServerSideEncryption': 'AES256'|'aws:kms'|'aws:kms:dsse',
        'Metadata': {
            'string': 'string'
        },
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'BucketKeyEnabled': True|False,
        'StorageClass': 'STANDARD' | 'REDUCED_REDUNDANCY' | 'STANDARD_IA' | 'ONEZONE_IA' |
                        'INTELLIGENT_TIERING' | 'GLACIER' | 'DEEP_ARCHIVE' | 'OUTPOSTS' |
                        'GLACIER_IR' | 'SNOW' | 'EXPRESS_ONEZONE',
        'RequestCharged': 'requester',
        'ReplicationStatus': 'COMPLETE'|'PENDING'|'FAILED'|'REPLICA'|'COMPLETED',
        'PartsCount': 123,
        'ObjectLockMode': 'GOVERNANCE'|'COMPLIANCE',
        'ObjectLockRetainUntilDate': datetime(2015, 1, 1),
        'ObjectLockLegalHoldStatus': 'ON'|'OFF'
    }

    :param errors: incidental error messages
    :param identifier: the object identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the item from
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: the metadata tags associated with the item, or *None* if error or item not found
    """
    # initialize the return variable
    result: dict[str, Any] | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_key: str = obj_path.as_posix()
            else:
                obj_key: str = identifier
            head_info: dict[str, str] = client.head_object(Bucket=bucket,
                                                           Key=obj_key)
            result = head_info.get("Metadata")
            if logger:
                logger.debug(msg=f"Retrieved '{obj_key}', bucket '{bucket}', tags '{result}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not hasattr(e, "code") or e.code != "NoSuchKey":
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.AWS))

    return result


def item_remove(errors: list[str],
                identifier: str,
                bucket: str = None,
                prefix: str | Path = None,
                client: BaseClient = None,
                logger: Logger = None) -> int:
    """
    Remove an item from the *AWS* store.

    The item might be interpreted as unspecified data, a file, or an object.
    To remove items in a given folder, use *items_remove()*, instead.

    :param errors: incidental error messages
    :param identifier: the item identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to delete the item at
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: The number of items successfully removed
    """
    # initialize the return variable
    result: int = 0

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        # was the identifier provided ?
        if identifier:
            # yes, remove the item
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_key: str = obj_path.as_posix()
            else:
                obj_key: str = identifier
            result += _item_delete(errors=errors,
                                   bucket=bucket,
                                   obj_key=obj_key,
                                   client=client,
                                   logger=logger)
        else:
            # no, remove the items in the folder
            op_errors: list[str] = []
            items_data: list[dict[str, Any]] = items_list(errors=op_errors,
                                                          max_count=10000,
                                                          bucket=bucket,
                                                          prefix=prefix)
            for item_data in items_data:
                if op_errors or result >= 10000:
                    break
                obj_key: str = item_data.get("Key")
                result += _item_delete(errors=op_errors,
                                       bucket=bucket,
                                       obj_key=obj_key,
                                       client=client,
                                       logger=logger)
    return result


def items_count(errors: list[str],
                bucket: str = None,
                prefix: str | Path = None,
                client: BaseClient = None,
                logger: Logger = None) -> int or None:
    """
    Retrieve and return the number of items in *prefix*, in the *AWS* store.

    A count operation on the contents of a *prefix* may be time-consuming, as the least inefficient way to
    obtain such information with the *boto3* package is by paginating the elements and accounting for the
    sizes of these pages.

    :param errors: incidental error messages
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the items from
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: the number of items in *prefix*, 0 if *prefix* not found, or *None* if error
    """
    # initialize the return variable
    result: int | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        try:
            # initialize a page iterator
            paginator: Paginator = client.get_paginator(operation_name="list_objects_v2")
            iterator: PageIterator = paginator.paginate(Bucket=bucket,
                                                        Prefix=Path(prefix).as_posix() if prefix else None,
                                                        Delimiter="/")
            # traverse the pages, counting the items
            result = sum(page.get("KeyCount", 0) for page in iterator)
            if logger:
                logger.debug(msg=f"Counted {result} items in '{prefix}', bucket '{bucket}'")
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.AWS))
    return result


def items_list(errors: list[str],
               max_count: int = None,
               bucket: str = None,
               prefix: str | Path = None,
               client: BaseClient = None,
               logger: Logger = None) -> list[dict[str, Any]]:
    """
    Recursively retrieve and return information on a list of items in *prefix*, in the *AWS* store.

    if *max_count* is a positive integer, the number of items returned may be less, but not more,
    than its value, otherwise it is ignored and all existing items in *prefix* are returned.

    The first element in the list is the folder indicated in *prefix*. The information returned by the
    native invocation is shown below. The *list* returned contains the items of the *Contents* attribute.
    Refer to the published *AWS* documentation for the meaning of any of these attributes.
    {
        'IsTruncated': True|False,
        'Contents': [
            {
                'Key': 'string',
                'LastModified': datetime(2015, 1, 1),
                'ETag': 'string',
                'ChecksumAlgorithm': [
                    'CRC32'|'CRC32C'|'SHA1'|'SHA256',
                ],
                'Size': 123,
                'StorageClass': 'STANDARD' | 'REDUCED_REDUNDANCY' | 'STANDARD_IA' | 'ONEZONE_IA' |
                                'INTELLIGENT_TIERING' | 'GLACIER' | 'DEEP_ARCHIVE' | 'OUTPOSTS' |
                                'GLACIER_IR' | 'SNOW' | 'EXPRESS_ONEZONE',
                'Owner': {
                    'DisplayName': 'string',
                    'ID': 'string'
                },
                'RestoreStatus': {
                    'IsRestoreInProgress': True|False,
                    'RestoreExpiryDate': datetime(2015, 1, 1)
                }
            },
        ],
        'Name': 'string',
        'Prefix': 'string',
        'Delimiter': 'string',
        'MaxKeys': 123,
        'CommonPrefixes': [
            {
                'Prefix': 'string'
            },
        ],
        'EncodingType': 'url',
        'KeyCount': 123,
        'ContinuationToken': 'string',
        'NextContinuationToken': 'string',
        'StartAfter': 'string',
        'RequestCharged': 'requester'
    }

    :param errors: incidental error messages
    :param max_count: the maximum number of items to return (defaults to all items)
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the items from
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: information on a list of items in *prefix*, or *None* if error or *prefix* not found
    """
    # initialize the return variable
    result: list[dict[str, Any]] | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        if not isinstance(max_count, int) or \
           isinstance(max_count, bool) or max_count < 0:
            max_count = 0
        max_keys: int = max_count if 0 < max_count < 1000 else 1000
        try:
            items: list[dict[str, Any]] = []
            proceed: bool = True
            continuation: str | None = None
            while proceed:
                # retrieve the objects
                reply: dict[str, Any] = client.list_objects_v2(Bucket=bucket,
                                                               Prefix=Path(prefix).as_posix() if prefix else None,
                                                               Delimiter="/",
                                                               MaxKeys=max_keys,
                                                               StartAfter=continuation)
                # retrieve from the list (it might be empty)
                proceed = False
                objs: list[dict[str, Any]] = reply.get("Contents")
                if objs:
                    rem: int = min(max_count - len(items), len(objs)) if max_count else len(objs)
                    items.extend(objs[:rem])
                    rem = max_count - len(items) if max_count else 1000
                    if rem > 0:
                        # get the last key read
                        continuation = objs[-1].get("Key")
                        # set the value for the 'MaxKeys' parameter in the next objects retrieval
                        max_keys = min(max_keys, rem)
                        proceed = True

            # save the items and log the results
            result = items
            if logger:
                logger.debug(msg=f"Listed {len(result)} items in '{prefix}', bucket '{bucket}'")
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.AWS))
    return result


def items_remove(errors: list[str],
                 max_count: int = None,
                 bucket: str = None,
                 prefix: str | Path = None,
                 client: BaseClient = None,
                 logger: Logger = None) -> int:
    """
    Recursively remove up to *max_count* items in a folder, from the *AWS* store.

    The removal process is aborted if an error occurs.

    :param errors: incidental error messages
    :param max_count: the maximum number of items to remove (defaults to all items)
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to remove the items from
    :param client: optional AWS client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: The number of items successfully removed
    """
    # initialize the return variable
    result: int = 0

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.AWS,
                                      param=S3Param.BUCKET_NAME)
        op_errors: list[str] = []
        items_data: list[dict[str, Any]] = items_list(errors=op_errors,
                                                      max_count=max_count,
                                                      bucket=bucket,
                                                      prefix=prefix)
        for item_data in items_data:
            if op_errors or result >= max_count:
                break
            # skip item, if it is a folder
            if item_data.get("Key").endswith("/"):
                result += 1
            else:
                obj_key: str = item_data.get("Key")
                result += _item_delete(errors=op_errors,
                                       bucket=bucket,
                                       obj_key=obj_key,
                                       client=client,
                                       logger=logger)
    return result


def _item_delete(errors: list[str],
                 obj_key: str,
                 client: BaseClient,
                 bucket: str,
                 logger: Logger) -> int:
    """
    Delete the item in the *AWS* store.

    :param errors: incidental error messages
    :param obj_key: the item's name, including its path
    :param client: the AWS client object
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param logger: optional logger
    :return: '1' if the item was deleted, '0' otherwise
    """
    result: int = 0
    try:
        client.remove_object(Bucket=bucket,
                             Key=obj_key)
        if logger:
            logger.debug(msg=f"Deleted '{obj_key}', bucket '{bucket}'")
        result = 1
    except Exception as e:
        # noinspection PyUnresolvedReferences
        if not hasattr(e, "code") or e.code != "NoSuchKey":
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.AWS))
    return result
