from collections.abc import Iterator
from io import BytesIO
from logging import Logger
from minio import Minio
from minio.datatypes import Object as MinioObject
from minio.commonconfig import Tags
from pathlib import Path
from pypomes_core import Mimetype
from typing import Any, BinaryIO
from urllib3.response import HTTPResponse

from .s3_common import (
    S3Engine, S3Param,
    _get_param, _get_params, _normalize_tags, _except_msg
)


def startup(errors: list[str],
            bucket: str,
            logger: Logger = None) -> bool:
    """
    Prepare the *MinIO* client for operations.

    This function should be called just once, at startup,
    to make sure the interaction with the MinIo service is fully functional.

    :param errors: incidental error messages
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param logger: optional logger
    :return: *True* if service is fully functional, *False* otherwise
    """
    # initialize the return variable
    result: bool = False

    # obtain a client
    client: Minio = get_client(errors=errors,
                               logger=logger)
    # was the client obtained ?
    if client:
        # yes, proceed
        try:
            if client.bucket_exists(bucket_name=bucket):
                action: str = "asserted"
            else:
                client.make_bucket(bucket_name=bucket)
                action: str = "created"
            result = True
            if logger:
                logger.debug(msg=f"Started MinIO, {action} bucket '{bucket}'")
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.MINIO))
    return result


def get_client(errors: list[str],
               logger: Logger = None) -> Minio:
    """
    Obtain and return a *MinIO* client object.

    :param errors: incidental error messages
    :param logger: optional logger
    :return: the MinIO client object
    """
    # initialize the return variable
    result: Minio | None = None

    # retrieve the access parameters
    minio_params: dict[S3Param, Any] = _get_params(engine=S3Engine.MINIO)

    # obtain the MinIO client
    try:
        result = Minio(access_key=minio_params.get(S3Param.ACCESS_KEY),
                       secret_key=minio_params.get(S3Param.SECRET_KEY),
                       endpoint=minio_params.get(S3Param.ENDPOINT_URL),
                       secure=minio_params.get(S3Param.SECURE_ACCESS),
                       region=minio_params.get(S3Param.REGION_NAME))
        if logger:
            logger.debug(msg="Minio client created")

    except Exception as e:
        errors.append(_except_msg(exception=e,
                                  engine=S3Engine.MINIO))
    return result


def data_retrieve(errors: list[str],
                  identifier: str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  data_range: tuple[int, int] = None,
                  client: Minio = None,
                  logger: Logger = None) -> bytes:
    """
    Retrieve data from the *MinIO* store.

    :param errors: incidental error messages
    :param identifier: the data identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the data from
    :param data_range: the begin-end positions within the data (in bytes, defaults to *None* - all bytes)
    :param client: optional MinIO client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: the bytes retrieved, or *None* if error or data not found
    """
    # initialize the return variable
    result: bytes | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        offset: int = data_range[0] if data_range else 0
        length: int = data_range[1] - data_range[0] + 1 if data_range else 0

        # retrieve the data
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_name: str = obj_path.as_posix()
            else:
                obj_name: str = identifier
            response: HTTPResponse = client.get_object(bucket_name=bucket,
                                                       object_name=obj_name,
                                                       offset=offset,
                                                       length=length)
            result = response.data
            if logger:
                logger.debug(msg=f"Retrieved '{obj_name}', bucket '{bucket}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not hasattr(e, "code") or e.code != "NoSuchKey":
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.MINIO))
    return result


def data_store(errors: list[str],
               identifier: str,
               data: bytes | str | BinaryIO,
               bucket: str = None,
               prefix: str | Path = None,
               length: int = -1,
               mimetype: Mimetype | str = Mimetype.BINARY,
               tags: dict[str, str] = None,
               client: Minio = None,
               logger: Logger = None) -> bool:
    """
    Store *data* at the *MinIO* store.

    In case *length* cannot be determined, it should be set to *-1*.

    :param errors: incidental error messages
    :param identifier: the data identifier
    :param data: the data to store
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to store the file at
    :param length: the length of the data (defaults to -1: unknown)
    :param mimetype: the data mimetype
    :param tags: optional metadata tags describing the file
    :param client: optional MinIO client (obtains a new one, if not provided)
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
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        bin_data: BinaryIO
        if isinstance(data, BinaryIO):
            bin_data = data
        else:
            bin_data = BytesIO(data) if isinstance(data, bytes) else \
                       BytesIO(bytes(data, "utf-8"))
            bin_data.seek(0)
        tags = _minio_tags(tags)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_name: str = obj_path.as_posix()
            else:
                obj_name: str = identifier
            if isinstance(mimetype, Mimetype):
                mimetype = mimetype.value
            client.put_object(bucket_name=bucket,
                              object_name=obj_name,
                              data=bin_data,
                              length=length,
                              content_type=mimetype,
                              tags=tags)
            if logger:
                logger.debug(msg=(f"Stored '{obj_name}', bucket '{bucket}', "
                                  f"content type '{mimetype}', tags '{tags}'"))
            result = True
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.MINIO))
    return result


def file_retrieve(errors: list[str],
                  identifier: str,
                  filepath: Path | str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  client: Minio = None,
                  logger: Logger = None) -> Any:
    """
    Retrieve a file from the *MinIO* store.

    :param errors: incidental error messages
    :param identifier: the file identifier, tipically a file name
    :param filepath: the path to save the retrieved file at
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the file from
    :param client: optional MinIO client (obtains a new one, if not provided)
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
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_name: str = obj_path.as_posix()
            else:
                obj_name: str = identifier
            file_path: str = Path(filepath).as_posix()
            result = client.fget_object(bucket_name=bucket,
                                        object_name=obj_name,
                                        file_path=file_path)
            if logger:
                logger.debug(msg=f"Retrieved '{obj_name}', bucket '{bucket}', to '{file_path}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not hasattr(e, "code") or e.code != "NoSuchKey":
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.MINIO))
    return result


def file_store(errors: list[str],
               identifier: str,
               filepath: Path | str,
               mimetype: Mimetype | str,
               bucket: str = None,
               prefix: str | Path = None,
               tags: dict[str, str] = None,
               client: Minio = None,
               logger: Logger = None) -> bool:
    """
    Store a file at the *MinIO* store.

    :param errors: incidental error messages
    :param identifier: the file identifier, tipically a file name
    :param filepath: optional path specifying where the file is
    :param mimetype: the file mimetype
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to store the file at
    :param tags: optional metadata tags describing the file
    :param client: optional MinIO client (obtains a new one, if not provided)
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
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        tags = _minio_tags(tags)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_name: str = obj_path.as_posix()
            else:
                obj_name: str = identifier
            file_path: str = Path(filepath).as_posix()
            if isinstance(mimetype, Mimetype):
                mimetype = mimetype.value
            client.fput_object(bucket_name=bucket,
                               object_name=obj_name,
                               file_path=file_path,
                               content_type=mimetype,
                               tags=tags)
            if logger:
                logger.debug(msg=(f"Stored '{obj_name}', bucket '{bucket}', "
                                  f"from '{file_path}', content type '{mimetype}', tags '{tags}'"))
            result = True
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.MINIO))
    return result


def item_get_info(errors: list[str],
                  identifier: str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  client: Minio = None,
                  logger: Logger = None) -> dict[str, Any]:
    """
    Retrieve and return information about an item in the *MinIO* store.

    The item might be interpreted as unspecified data, a file, or an object.
    The information about the item might include:
        - *last_modified*: the date and time the item was last modified
        - *size*: the size of the item in bytes
        - *etag*: a hash of the item
        - *is_dir*: a *bool* indicating if the item is a directory
        - *version_id*: the version of the item, if bucket versioning is enabled

    :param errors: incidental error messages
    :param identifier: the item identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying where to locate the item
    :param client: optional MinIO client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: information about the item, an empty 'dict' if item not found, or *None* if error
    """
    # initialize the return variable
    result: dict[str, Any] | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_name: str = obj_path.as_posix()
            else:
                obj_name: str = identifier
            stats: MinioObject = client.stat_object(bucket_name=bucket,
                                                    object_name=obj_name)
            result = vars(stats)
            if logger:
                logger.debug(msg=f"Got info for '{obj_name}', bucket '{bucket}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if hasattr(e, "code") or e.code != "NoSuchKey":
                result = {}
            else:
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.MINIO))
    return result


def item_get_tags(errors: list[str],
                  identifier: str,
                  bucket: str = None,
                  prefix: str | Path = None,
                  client: Minio = None,
                  logger: Logger = None) -> dict[str, str]:
    """
    Retrieve and return the existing metadata tags for an item in the *MinIO* store.

    The item might be interpreted as unspecified data, a file, or an object.
    If item was not found, or has no associated metadata tags, an empty *dict* is returned.

    :param errors: incidental error messages
    :param identifier: the object identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the item from
    :param client: optional MinIO client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: the metadata tags, an empty 'dict' if item not found os has no tags, or *None* if error
    """
    # initialize the return variable
    result: dict[str, Any] | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        try:
            if prefix:
                obj_path: Path = Path(prefix) / identifier
                obj_name: str = obj_path.as_posix()
            else:
                obj_name: str = identifier
            tags: Tags = client.get_object_tags(bucket_name=bucket,
                                                object_name=obj_name)
            if tags:
                result = dict(tags.items())
            else:
                result = {}
            if logger:
                logger.debug(msg=f"Retrieved '{obj_name}', bucket '{bucket}', tags '{result}'")
        except Exception as e:
            # noinspection PyUnresolvedReferences
            if not hasattr(e, "code") or e.code != "NoSuchKey":
                errors.append(_except_msg(exception=e,
                                          engine=S3Engine.MINIO))
    return result


def item_remove(errors: list[str],
                identifier: str,
                bucket: str = None,
                prefix: str | Path = None,
                client: Minio = None,
                logger: Logger = None) -> int:
    """
    Remove an item from the *MinIO* store.

    The item might be interpreted as unspecified data, a file, or an object.
    To remove items in a given folder, use *items_remove()*, instead.

    :param errors: incidental error messages
    :param identifier: the item identifier
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to delete the item at
    :param client: optional MinIO client (obtains a new one, if not provided)
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
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)

        obj_path: Path = Path(prefix) / identifier
        obj_name: str = obj_path.as_posix()
        result = _item_delete(errors=errors,
                              bucket=bucket,
                              obj_name=obj_name,
                              client=client,
                              logger=logger)
    return result


def items_count(errors: list[str],
                bucket: str = None,
                prefix: str | Path = None,
                client: Minio = None,
                logger: Logger = None) -> int or None:
    """
    Retrieve and return the number of items in *prefix*, in the *MinIO* store.

    A count operation on the contents of a *prefix* may be extremely time-consuming, as the only way to
    obtain such information with the *minio* package is by retrieving and counting the elements from the
    appropriate iterators.

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
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        obj_path: str = Path(prefix).as_posix()
        try:
            count: int = 0
            proceed: bool = True
            continuation: str | None = None
            while proceed:
                # obtain an iterator on the items in the folder
                iterator: Iterator = client.list_objects(bucket_name=bucket,
                                                         prefix=obj_path,
                                                         include_user_meta=True,
                                                         recursive=True,
                                                         start_after=continuation)
                # traverse the iterator (it might be empty)
                proceed = False
                for obj in iterator:
                    count += 1
                    continuation = obj.object_name
                    proceed = True

            # save the count and log the results
            result = count
            if logger:
                logger.debug(msg=f"Counted {result} items in '{prefix}', bucket '{bucket}'")
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.MINIO))
    return result


def items_list(errors: list[str],
               max_count: int,
               bucket: str = None,
               prefix: str | Path = None,
               client: Minio = None,
               logger: Logger = None) -> list[dict[str, Any]]:
    """
    Recursively retrieve and return information on a list of items in *prefix*, in the *MinIO* store.

    if *max_count* is a positive integer, the number of items returned may be less, but not more,
    than its value, otherwise it is ignored and all existing items in *prefix* are returned.

    The first element in the list is the folder indicated in *prefix*.
    The information about each item might include:
        - *object_name*: the name of the item
        - *last_modified*: the date and time the item was last modified
        - *size*: the size of the item in bytes
        - *etag*: a hash of the item
        - *is_dir*: a *bool* indicating if the item is a directory
        - *version_id*: the version of the item, if bucket versioning is enabled

    :param errors: incidental error messages
    :param max_count: the maximum number of items to return
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to retrieve the items from
    :param client: optional MinIO client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: the iterator into the list of items, or *None* if error or path not found
    """
    # initialize the return variable
    result: list[dict[str, Any]] | None = None

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        obj_path: str = Path(prefix).as_posix()
        try:
            items: list[dict[str, Any]] = []
            proceed: bool = True
            continuation: str | None = None
            while proceed:
                # obtain an iterator on the items in the folder
                iterator: Iterator[MinioObject] = client.list_objects(bucket_name=bucket,
                                                                      prefix=obj_path,
                                                                      include_user_meta=True,
                                                                      recursive=True,
                                                                      start_after=continuation)
                # traverse the iterator (it might be empty)
                proceed = False
                for obj in iterator:
                    items.append(vars(obj))
                    if max_count and len(items) == max_count:
                        break
                    continuation = obj.object_name
                    proceed = True

            # save the items and log the results
            result = items
            if logger:
                logger.debug(msg=f"Listed {len(result)} items in '{prefix}', bucket '{bucket}'")
        except Exception as e:
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.MINIO))
    return result


def items_remove(errors: list[str],
                 max_count: int,
                 bucket: str = None,
                 prefix: str | Path = None,
                 client: Minio = None,
                 logger: Logger = None) -> int:
    """
    Recursively remove up to *max_count* items in a folder, from the *MinIO* store.

    The removal process is aborted if an error occurs.

    :param errors: incidental error messages
    :param max_count: the maximum number of items to remove
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param prefix: optional path specifying the location to remove the items from
    :param client: optional MinIO client (obtains a new one, if not provided)
    :param logger: optional logger
    :return: The number of items successfully removed
    """
    # initialize the return variable
    result: int = 0

    # make sure to have a client
    client = client or get_client(errors=errors,
                                  logger=logger)
    # was the client obtained ?
    if client:
        # make sure to have a bucket
        bucket = bucket or _get_param(engine=S3Engine.MINIO,
                                      param=S3Param.BUCKET_NAME)
        op_errors: list[str] = []
        items_data: list[dict[str, Any]] = items_list(errors=op_errors,
                                                      bucket=bucket,
                                                      prefix=prefix,
                                                      max_count=10000)
        for item_data in items_data:
            if op_errors or result >= max_count:
                break
            # skip item, if it is a folder
            if hasattr(items_data, "is_dir") and items_data.is_dir:
                result += 1
            else:
                obj_name: str = item_data.get("key")
                result += _item_delete(errors=op_errors,
                                       bucket=bucket,
                                       obj_name=obj_name,
                                       client=client,
                                       logger=logger)
    return result


def _item_delete(errors: list[str],
                 obj_name: str,
                 client: Minio,
                 bucket: str,
                 logger: Logger = None) -> int:
    """
    Delete the item in the *MinIO* store.

    :param errors: incidental error messages
    :param obj_name: the item's name, including its path
    :param client: the MinIO client object
    :param bucket: the bucket to use (uses the default bucket, if not provided)
    :param logger: optional logger
    :return: '1' if the item was deleted, '0' otherwise
    """
    # initialize the return variable
    result: int = 0

    try:
        client.remove_object(bucket_name=bucket,
                             object_name=obj_name)
        if logger:
            logger.debug(msg=f"Removed item '{obj_name}', bucket '{bucket}'")
        result = 1
    except Exception as e:
        # SANITY CHECK: in case of concurrent exclusion
        # noinspection PyUnresolvedReferences
        if not hasattr(e, "code") or e.code != "NoSuchKey":
            errors.append(_except_msg(exception=e,
                                      engine=S3Engine.MINIO))
    return result


def _minio_tags(tags: dict[str, str]) -> Tags:

    # initialize the return variable
    result: Tags | None = None

    # have tags been defined ?
    if tags:
        # yes, process them
        result = Tags(for_object=True)
        for key, value in _normalize_tags(tags=tags).items():
            result[key] = value

    return result
