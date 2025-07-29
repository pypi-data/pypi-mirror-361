from typing import Optional, Dict, Any, Union
import os
import requests
import mimetypes
from tqdm import tqdm
from glob import glob

from fissionbox.core.sample import Sample
from .connection import Connection

ALLOWED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
]


class SampleClient:
    def __init__(self, connection: Connection):
        self._connection = connection

    def upload_folder(self, path: str, metadata: Optional[Dict[str, Any]] = {}, batch_id: str = None) -> Dict[str, Sample]:
        """
        Upload all samples in a folder to the FissionBox platform.

        Args:
            path (str): The folder path containing samples to upload.
            metadata (Optional[Dict[str, Any]]): Additional metadata for the samples.
        Returns:
            Dict[str, Sample]: A dictionary mapping sample names to Sample objects.
        """
        if not os.path.isdir(path):
            raise NotADirectoryError(f"The path {path} is not a directory.")
        
        samples = {}
        for root, _, files in os.walk(path):
            for file in tqdm(files, desc="Uploading samples"):
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                if ext.lower() in ALLOWED_EXTENSIONS:
                    sample = self.upload(file_path, metadata, batch_id)
                    samples[sample.name] = sample
        return samples

    def upload(self, path: str, metadata: Optional[Dict[str, Any]] = {}, batch_id: str = None) -> Sample:
        """
        Upload a sample to the FissionBox platform.

        Args:
            path (str): The file path of the sample to upload.
            metadata (Optional[Dict[str, Any]]): Additional metadata for the sample.
        Returns:
            Sample: The uploaded sample object.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file at {path} does not exist.")
        content_type, _ = mimetypes.guess_type(path)
        if not content_type:
            content_type = "application/octet-stream"
        file2upload = open(path, "rb")
        body = {"name": os.path.basename(path), "metadata": metadata, "batch_id": batch_id}

        # 1. Get the upload info
        response = self._connection.request("POST", "/samples/uploads", json=body)
        data: dict = response.json()
        upload_id = data.get("id")
        presigned_s3_url = data.get("upload_url")
        if not presigned_s3_url:
            raise ValueError("No upload URL returned from the server.")
        # 2. Upload the file to S3
        upload_response = requests.put(
            presigned_s3_url,
            data=file2upload,
            headers={
                "Content-Type": content_type,
            },
        )
        if upload_response.status_code != 200:
            raise ValueError(f"Failed to upload file: {upload_response.text}")
        # 3. ACK the upload
        response = self._connection.request(
            "POST",
            f"/samples/uploads/{upload_id}/ack",
            json={"name": os.path.basename(path)},
        )

        data = response.json()["data"]

        return Sample(
            id=data.get("id"),
            name=data.get("attributes").get("name"),
            type=data.get("attributes").get("type"),
            media=data.get("attributes").get("media"),
        )
