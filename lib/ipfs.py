import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import HTTPException

from models.settings import Settings

settings = Settings()


config = cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name, api_key=settings.cloudinary_api_key, api_secret=settings.cloudinary_api_secret,  secure=True)


def upload_to_ipfs(image):
    try:
        res = cloudinary.uploader.upload(image, folder="hydratest", resource_type="image")

        result = {
            "url": res["url"],
            "public_id": res["public_id"],
            "secure_url": res["secure_url"]
        }

        return result

    except Exception as e:

        if settings.debug:
            print(e)

        raise HTTPException(
            500, "An error occured while trying to upload resource.")