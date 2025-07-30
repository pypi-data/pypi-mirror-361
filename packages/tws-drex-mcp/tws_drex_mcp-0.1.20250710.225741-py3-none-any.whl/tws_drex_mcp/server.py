# server.py
import os
import httpx
import base64
import aiofiles
from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv
from LoginRadius import LoginRadius
import logging
import sys

logging.basicConfig(
    level=logging.INFO,  # Or logging.DEBUG for more detail
    stream=sys.stderr,  # Explicitly direct logs to stderr
    format="%(asctime)s - %(name)s - %(levelname)s - SERVER: %(message)s",  # Add SERVER prefix
)


mcp = FastMCP("DREX")
load_dotenv()

DREX_BASE_URL = os.getenv("DREX_BASE_URL")

lr = None
LR_API_KEY = os.getenv("LR_API_KEY")
LR_API_SECRET = os.getenv("LR_API_SECRET")


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
async def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    ctx = mcp.get_context()
    await ctx.session.send_log_message(
        level="info",
        data=f"Greeting user {name}",
    )
    return f"Hello, {name}!"


async def init_loginradius(ctx: Context | None = None) -> None:
    global lr
    if lr is not None:
        return

    if LR_API_KEY and LR_API_SECRET:
        LoginRadius.API_KEY = LR_API_KEY
        LoginRadius.API_SECRET = LR_API_SECRET
        lr = LoginRadius()

    await ctx.session.send_log_message(
        level="info", data="LoginRadius SDK initialised successfully"
    )


@mcp.tool(description="Get an auth token by logging in with username/password")
async def get_token(username: str, password: str) -> str:
    """
    Return an auth token by logging in with username/password.
    """
    ctx = mcp.get_context()  # ctx is never None for tools

    if not username or not password:
        return "No username or password provided. Skipping token generation."

    if not LR_API_KEY or not LR_API_SECRET:
        return "API Key and Secret are not configured. Cannot get token."

    if lr is None:
        await init_loginradius(ctx=ctx)

    try:
        email_authentication_model = {"email": username, "password": password}
        response = lr.authentication.login_by_email(email_authentication_model)
        await ctx.session.send_log_message(
            level="debug", data=f"Login response: {response}"
        )
        return response.get("access_token", "No access token found in response")
    except Exception as e:
        return f"Error during login: {str(e)}"


def is_valid_filename(
    filename: str, ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf", ".txt"}
) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


async def _prepare_file_data_from_paths(paths: list[str]) -> list[dict]:
    """
    Reads files from paths (or files within directories), validates them,
    and returns a list of dictionaries containing filename and base64 content.
    """
    file_data_list = []
    print(f"Processing path: {paths}", file=sys.stderr)
    for path in paths:
        if not os.path.exists(path):
            raise ValueError(f"Path not found: {path}")

        files_to_process = []
        if os.path.isdir(path):
            # If it's a directory, find valid files within it
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and is_valid_filename(item):
                    files_to_process.append(item_path)
        elif os.path.isfile(path):
            # If it's a file, process it directly
            filename = os.path.basename(path)
            if is_valid_filename(filename):
                files_to_process.append(path)
            else:
                raise ValueError(
                    f"Invalid or unsupported file type: {filename}. Valid example: <file>.png"
                )
        else:
            # Neither a file nor a directory that exists
            raise ValueError(f"Path is not a valid file or directory: {path}")

        for file_path in files_to_process:
            filename = os.path.basename(file_path)
            try:
                async with aiofiles.open(file_path, "rb") as f:
                    file_content_bytes = await f.read()
                file_content_base64 = base64.b64encode(file_content_bytes).decode(
                    "utf-8"
                )
                file_data_list.append(
                    {"filename": filename, "content": file_content_base64}
                )
            except Exception as e:
                raise ValueError(f"Failed to read and encode file '{filename}': {e}")

    if not file_data_list:
        raise ValueError("No valid files found in the provided paths.")

    return file_data_list


async def upload_base64_files(
    file_data: list[dict], uploaded_by: str, token: str
) -> str:
    """
    Upload multiple files (provided as base64 strings) to the DREX API.
    The processing time may range from 10 to 80 seconds.
    Please wait for the processing to complete before attempting to check status or retrieve results.

    Arguments:
        file_data (list[dict]): List of dictionaries, each containing 'filename' (str) and 'content' (str, base64 encoded).
        uploaded_by (str): Identifier (e.g., username or email) of the user performing the upload.
        token (str): Authorization token for authenticating API requests.

    Returns:
        str: JSON response from DREX API upon successful file upload.

    Raises:
        ValueError: If any filename is invalid or base64 content is malformed.
        Exception: If the API response indicates a failure during file upload.
    """
    endpoint = f"{DREX_BASE_URL}/file-upload"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"uploadedBy": uploaded_by}

    file_payload = []
    for item in file_data:
        filename = item.get("filename")
        base64_content = item.get("content")

        if not filename or not base64_content:
            raise ValueError(
                "Each item in file_data must have 'filename' and 'content' keys."
            )

        # Validate filename
        if not is_valid_filename(filename):
            raise ValueError(
                f"Invalid or unsupported file type: {filename}. Valid example: <file>.png"
            )

        try:
            # Decode base64 content back to bytes for upload
            file_content_bytes = base64.b64decode(base64_content)
        except Exception as e:
            raise ValueError(
                f"Failed to decode base64 content for file '{filename}': {e}"
            )

        file_payload.append(
            ("files", (filename, file_content_bytes, "application/octet-stream"))
        )  # TODO: consider when payload is too large (image too large)

    if not file_payload:
        raise ValueError("No valid file data provided for upload.")

    async with httpx.AsyncClient(
        timeout=30
    ) as client:  # Consider increasing timeout for large uploads
        response = await client.post(
            endpoint, headers=headers, data=data, files=file_payload
        )

    if response.status_code != 200:
        # Log the error for debugging
        logging.error(f"DREX API Error ({response.status_code}): {response.text}")
        raise Exception(
            f"Failed to upload files. Status: {response.status_code}, Response: {response.text}"
        )

    try:
        return response.json()
    except Exception as e:
        # Log the error for debugging
        logging.error(
            f"Failed to parse DREX API JSON response: {e}. Response text: {response.text}"
        )
        raise Exception(f"Failed to parse API response as JSON: {e}")


@mcp.tool(description="Upload files or directories to DREX API using paths.")
async def file_upload(
    file_paths: list[str] = ["path/to/img.png", "path/to/dir"],
    uploaded_by: str = "John Doe",
    token: str = "your-access-token",
) -> str:
    """
    Uploads files specified by paths or all valid files within specified directories to the DREX API.
    The processing time for each file may range from 10 to 80 seconds.
    Please wait for the processing to complete before attempting to check status or retrieve results.

    Arguments:
        file_paths (list[str]): List of absolute or relative paths to files or directories intended for upload.
        uploaded_by (str): Identifier (e.g., username or email) of the user performing the upload.
        token (str): Authorization token for authenticating API requests.

    Returns:
        str: JSON response from DREX API upon successful file upload.

    Raises:
        ValueError: If any path does not exist, is invalid, or contains no valid files.
        Exception: If the API response indicates a failure during file upload.
    """
    # Prepare the file data (convert paths to base64 dictionaries)
    ctx = mcp.get_context()  # ctx is never None for tools
    await ctx.session.send_log_message(
        level="info", data=f"Preparing file data from paths: {file_paths}"
    )
    file_data_list = await _prepare_file_data_from_paths(file_paths)

    # Call the internal function that handles base64 upload
    return await upload_base64_files(
        file_data=file_data_list, uploaded_by=uploaded_by, token=token
    )


@mcp.tool(description="Get the processing status of an uploaded file from DREX API")
async def get_status(file_id: str, token: str) -> dict:
    """
    Retrieve the processing status of an uploaded file from the DREX API.

    Arguments:
        file_id (str): Unique identifier returned after a successful file upload. Do not include the file extension.
        token (str): Authorization token for authenticating API requests.

    Returns:
        dict: Dictionary containing the current status details, such as processing state, timestamps, and any additional metadata.

    Raises:
        Exception: If the API response indicates a failure or the file ID is invalid.
    """
    # remove file extension from file_id if present
    file_id = os.path.splitext(file_id)[0]
    endpoint = f"{DREX_BASE_URL}/files/{file_id}/status"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(endpoint, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get file {file_id} status: {response.text}")
    return response.json()


@mcp.tool(description="Get the processed results of an uploaded file from DREX API")
async def get_file_results(file_id: str, token: str) -> dict:
    """
    Retrieve the processed results of an uploaded file from the DREX API.

    Arguments:
        file_id (str): Unique identifier returned after a successful file upload and processing completion. Do not include the file extension.
        token (str): Authorization token for authenticating API requests.

    Returns:
        dict: Dictionary containing the final processing results.

    Raises:
        Exception: If the results are unavailable, the processing is incomplete, or the API returns an error.
    """
    # remove file extension from file_id if present
    file_id = os.path.splitext(file_id)[0]
    endpoint = f"{DREX_BASE_URL}/blob-data-fetch/{file_id}"
    revgrid_endpoint = f"{DREX_BASE_URL}/drexRevGrid-fetch/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(endpoint, headers=headers)
        revgrid_response = await client.get(revgrid_endpoint, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get file {file_id} object details: {response.text}")
    if revgrid_response.status_code != 200:
        raise Exception(
            f"Failed to get file {file_id} revision grid: {revgrid_response.text}"
        )
    return {"file_details": response.json(), "revgrid": revgrid_response.json()}


if __name__ == "__main__":
    mcp.run(transport="stdio")
