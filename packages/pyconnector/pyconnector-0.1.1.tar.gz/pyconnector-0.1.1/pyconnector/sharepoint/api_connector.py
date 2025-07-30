from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder

class SharePointConnector:
    """
    Secure SharePoint Online API Connector using Office365-REST-Python-Client.

    Usage:
        with SharePointConnector(site_url, client_id, client_secret) as sp:
            files = sp.list_files('/Shared Documents')
    """

    def __init__(self, site_url, client_id, client_secret):
        """
        Initialize the connector.

        :param site_url: SharePoint site URL (e.g., 'https://yourtenant.sharepoint.com/sites/yoursite')
        :param client_id: Azure AD application client ID
        :param client_secret: Azure AD application client secret
        """
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.ctx = None

    def __enter__(self):
        """Establishes a secure session with SharePoint."""
        credentials = ClientCredential(self.client_id, self.client_secret)
        self.ctx = ClientContext(self.site_url).with_credentials(credentials)
        return self

    def list_files(self, folder_url):
        """
        List files in a SharePoint folder.

        :param folder_url: Server-relative URL of the folder (e.g., '/Shared Documents')
        :return: List of file properties
        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
        files = folder.files.get().execute_query()
        return [file.properties for file in files]

    def get_file_details(self, file_url):
        """
        Get file details and properties.

        :param file_url: Server-relative URL of the file
        :return: File properties
        """
        file = self.ctx.web.get_file_by_server_relative_url(file_url)
        file_properties = file.get().execute_query()
        return file_properties.properties

    def upload_file(self, folder_url, file_name, file_content):
        """
        Upload a file to a SharePoint folder.

        :param folder_url: Server-relative URL of the folder
        :param file_name: Name of the file to upload
        :param file_content: Bytes content of the file
        :return: Uploaded file properties
        """
        folder = self.ctx.web.get_folder_by_server_relative_url(folder_url)
        upload_file = folder.upload_file(file_name, file_content).execute_query()
        return upload_file.properties

    def download_file(self, file_url, local_path):
        """
        Download a file from SharePoint.

        :param file_url: Server-relative URL of the file
        :param local_path: Local path to save the file
        """
        file = self.ctx.web.get_file_by_server_relative_url(file_url)
        with open(local_path, "wb") as f:
            file.download(f).execute_query()

    def list_permissions(self, item_url):
        """
        List permissions for a file or folder.

        :param item_url: Server-relative URL of the item
        :return: List of role assignments
        """
        item = self.ctx.web.get_file_by_server_relative_url(item_url)
        item.get().expand(["RoleAssignments"]).execute_query()
        return item.properties.get("RoleAssignments", [])

    # Additional methods for add/remove/modify permissions, create folders, upload large files, etc., can be added here.






    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleans up the session securely."""
        self.ctx = None

