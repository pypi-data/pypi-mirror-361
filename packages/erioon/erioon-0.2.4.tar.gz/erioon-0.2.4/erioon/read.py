# Copyright 2025-present Erioon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Visit www.erioon.com/dev-docs for more information about the python SDK

import io
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import async_log

# GET ALL RECORDS OF A COLLECTION
def handle_get_all(user_id, db_id, coll_id, limit, container_url):
    """
    Retrieves up to a specified number of records from a collection stored in storage 
    and logs the operation status asynchronously.

    Parameters:
    - user_id (str): Identifier of the user making the request.
    - db_id (str): Database identifier (used as the directory prefix).
    - coll_id (str): Collection identifier (subdirectory under the database).
    - limit (int): Maximum number of records to retrieve (must not exceed 1,000,000).
    - container_url: Container SAS URL.

    Behavior:
    - Scans all specified collection path (`db_id/coll_id/`).
    - Reads shard files, each containing a list of records.
    - Skips duplicate records by checking their `_id`.
    - Stops reading once the record limit is reached.
    - Skips empty or non-conforming collection.

    Returns:
    - tuple(dict, int): A tuple containing:
        - A status dictionary with:
            - "status": "OK" or "KO"
            - "count": number of records returned (0 if none)
            - "results": list of records (only for successful responses)
            - "error": error message (on failure)
        - HTTP status code:
            - 200 if data is successfully returned.
            - 404 if collection is missing or no data found.
            - 500 on unexpected errors.
    """
    if limit > 1_000_000:
        async_log(user_id, db_id, coll_id, "GET", "ERROR", "Limit of 1,000,000 exceeded", 1, container_url)
        return {"status": "KO", "count": 0, "error": "Limit of 1,000,000 exceeded"}, 404

    directory_path = f"{db_id}/{coll_id}/"
    container_client = ContainerClient.from_container_url(container_url)

    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list]

    if not blob_names:
        async_log(user_id, db_id, coll_id, "GET", "ERROR", f"No collection {coll_id} found.", 1, container_url)
        return {"status": "KO", "count": 0, "error": f"No collection {coll_id} found."}, 404

    results = []
    seen_ids = set()

    for blob in blob_names:
        try:
            if blob.endswith(".msgpack"):
                blob_client = container_client.get_blob_client(blob)
                msgpack_data = blob_client.download_blob().readall()

                if not msgpack_data:
                    continue

                with io.BytesIO(msgpack_data) as buffer:
                    unpacked_data = msgpack.unpackb(buffer.read(), raw=False)
                    if isinstance(unpacked_data, list):
                        for record in unpacked_data:
                            if record["_id"] in seen_ids:
                                continue

                            results.append(record)
                            seen_ids.add(record["_id"])

                            if len(results) >= limit:
                                async_log(user_id, db_id, coll_id, "GET", "SUCCESS", f"OK", len(results), container_url)
                                return {"status": "OK", "count": len(results), "results": results}, 200

        except Exception:
            continue

    if results:
        async_log(user_id, db_id, coll_id, "GET", "SUCCESS", f"OK", len(results), container_url)
        return {"status": "OK", "count": len(results), "results": results}, 200

    async_log(user_id, db_id, coll_id, "GET", "ERROR", "No data found", 1, container_url)
    return {"status": "KO", "count": 0, "error": "No data found"}, 404

# FIND ONE RECORD
def handle_find_one(user_id, db_id, coll_id, search_criteria, container_url):
    """
    Search for a single record matching all given criteria in a collection stored in storage.

    The function loads each collection under `{db_id}/{coll_id}/` and iterates records to find
    the first one where all key-value criteria match, including nested keys using dot notation.
    It logs the operation result asynchronously.

    Args:
        user_id (str): ID of the user making the request.
        db_id (str): Identifier for the database.
        coll_id (str): Identifier for the collection.
        search_criteria (list[dict]): List of key-value dicts representing the search filters.
                                      Nested keys are supported via dot notation (e.g., "address.city").
        container_url: Container SAS URL.

    Returns:
        tuple(dict, int): A tuple containing:
            - A dictionary with keys:
                - "status" (str): "OK" if a record is found, "KO" if not.
                - "record" (dict): The found record if successful.
                - "error" (str): Error message if not found.
            - HTTP status code (int): 200 if found, 404 if no matching record or collection.
    """

    directory_path = f"{db_id}/{coll_id}/"
    container_client = ContainerClient.from_container_url(container_url)
    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]

    if not blob_names:
        async_log(user_id, db_id, coll_id, "GET_ONE", "ERROR", f"No collection {coll_id} found.", 1, container_url)
        return {"status": "KO", "error": f"No collection {coll_id} found."}, 404

    for blob_name in blob_names:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            msgpack_data = blob_client.download_blob().readall()
            if not msgpack_data:
                continue

            records = msgpack.unpackb(msgpack_data, raw=False)

            for record in records:
                matched_all = True
                for criteria in search_criteria:
                    key, value = list(criteria.items())[0]
                    current = record
                    for part in key.split("."):
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            matched_all = False
                            break
                    if current != value:
                        matched_all = False
                        break

                if matched_all:
                    async_log(user_id, db_id, coll_id, "GET_ONE", "SUCCESS", "Found one record", 1, container_url)
                    return {"status": "OK", "record": record}, 200

        except Exception:
            continue

    async_log(user_id, db_id, coll_id, "GET_ONE", "ERROR", "No matching record found", 1, container_url)
    return {"status": "KO", "error": "No matching record found"}, 404

# FIND MULTIPLE RECORDS
def handle_find_many(user_id, db_id, coll_id, search_criteria, limit, container_url):
    """
    Search for multiple records matching all given criteria in a collection stored as collections.

    The function scans all collections under `{db_id}/{coll_id}/` and collects unique records 
    that match all provided search criteria, supporting nested keys with dot notation.
    It returns up to `limit` records and logs the operation asynchronously.

    Args:
        user_id (str): ID of the user making the request.
        db_id (str): Identifier for the database.
        coll_id (str): Identifier for the collection.
        search_criteria (list[dict]): List of key-value dicts for filtering records.
        limit (int): Maximum number of matching records to return.
        container_url: Container SAS URL.

    Returns:
        tuple(dict, int): A tuple containing:
            - A dictionary with keys:
                - "status" (str): "OK" if matching records found, "KO" otherwise.
                - "count" (int): Number of records returned.
                - "results" (list[dict]): List of matching records if successful.
                - "error" (str): Error message if none found.
            - HTTP status code (int): 200 if matches found, 404 if none or collection missing.
    """
    
    directory_path = f"{db_id}/{coll_id}/"
    container_client = ContainerClient.from_container_url(container_url)
    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]

    if not blob_names:
        async_log(user_id, db_id, coll_id, "GET_MANY", "ERROR", f"No collection {coll_id} found.", 1, container_url)
        return {"status": "KO", "count": 0, "error": f"No collection {coll_id} found."}, 404

    results = []
    seen_ids = set()

    for blob_name in blob_names:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            msgpack_data = blob_client.download_blob().readall()
            if not msgpack_data:
                continue

            records = msgpack.unpackb(msgpack_data, raw=False)

            for record in records:
                if record.get("_id") in seen_ids:
                    continue

                matched_all = True
                for criteria in search_criteria:
                    key, value = list(criteria.items())[0]
                    current = record
                    for part in key.split("."):
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            matched_all = False
                            break
                    if current != value:
                        matched_all = False
                        break

                if matched_all:
                    results.append(record)
                    seen_ids.add(record.get("_id"))
                    if len(results) >= limit:
                        async_log(user_id, db_id, coll_id, "GET_MANY", "SUCCESS", "OK", len(results), container_url)
                        return {"status": "OK", "count": len(results), "results": results}, 200

        except Exception:
            continue

    if results:
        async_log(user_id, db_id, coll_id, "GET_MANY", "SUCCESS", "OK", len(results), container_url)
        return {"status": "OK", "count": len(results), "results": results}, 200

    async_log(user_id, db_id, coll_id, "GET_MANY", "ERROR", "No matching records found", 1, container_url)
    return {"status": "KO", "count": 0, "error": "No matching records found"}, 404

# COUNT ALL THE RECORDS
def handle_count_records(user_id, db_id, coll_id, container_url):
    """
    Count all records stored as .msgpack files in a given collection in Azure Blob Storage.

    Args:
        user_id (str): ID of the user making the request.
        db_id (str): Database identifier.
        coll_id (str): Collection identifier.
        container_url (str): Container SAS URL.

    Returns:
        tuple: (total_record_count: int, status_code: int)
    """
    import msgpack
    from azure.storage.blob import ContainerClient

    directory_path = f"{db_id}/{coll_id}/"
    container_client = ContainerClient.from_container_url(container_url)

    try:
        blob_list = container_client.list_blobs(name_starts_with=directory_path)
        blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]
    except Exception as e:
        async_log(user_id, db_id, coll_id, "COUNT", "ERROR", f"Blob listing failed: {str(e)}", 0, container_url)
        return 0, 500

    if not blob_names:
        async_log(user_id, db_id, coll_id, "COUNT", "ERROR", f"No collection {coll_id} found.", 0, container_url)
        return 0, 404

    total_count = 0

    for blob_name in blob_names:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            msgpack_data = blob_client.download_blob().readall()

            if msgpack_data:
                records = msgpack.unpackb(msgpack_data, raw=False)
                if isinstance(records, list):
                    total_count += len(records)
                else:
                    # Optional: warn on unexpected format
                    continue
        except Exception as e:
            # Optional: log per-blob error if needed
            continue

    async_log(user_id, db_id, coll_id, "COUNT", "SUCCESS", f"Total records: {total_count}", total_count, container_url)
    return total_count, 200
