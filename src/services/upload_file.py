import cloudinary
import cloudinary.uploader


class UploadFileService:
    """Service for uploading and managing files in Cloudinary.

    This service handles file uploads to Cloudinary, specifically optimized for
    user avatars. It configures the Cloudinary client and provides methods
    for file upload with automatic image optimization.

    Attributes:
        cloud_name (str): Cloudinary cloud name from dashboard
        api_key (str): Cloudinary API key
        api_secret (str): Cloudinary API secret
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """Initialize the upload service with Cloudinary credentials.

        Args:
            cloud_name (str): Cloudinary cloud name from dashboard
            api_key (str): Cloudinary API key
            api_secret (str): Cloudinary API secret
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """Upload a file to Cloudinary and return its optimized URL.

        Uploads the file to a user-specific folder in Cloudinary and returns
        a URL for an automatically optimized version of the image.

        Args:
            file (UploadFile): FastAPI UploadFile object containing the image
            username (str): Username for creating a unique public_id

        Returns:
            str: URL of the uploaded and optimized image on Cloudinary.
                The image will be:
                - Resized to 250x250 pixels
                - Cropped to fill the square dimensions
                - Served over HTTPS
                - Versioned to prevent caching issues

        Note:
            - Files are stored in the 'RestApp/{username}' path
            - Existing files with the same name will be overwritten
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
