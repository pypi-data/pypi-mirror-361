import urllib3
import warnings

from .content_config import ContentConfig
from .content_search import ContentSearch, IndexSearch
from .content_smart_chat import ContentSmartChat
from .content_archive_metadata import ContentArchiveMetadata
from .content_archive_policy import ContentArchivePolicy 
from .content_archive_policy_plus import ContentArchivePolicyPlus 
from .content_document import ContentDocument

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentServicesApi:
    """
    ContentServicesApi is the main class for interacting with the Mobius REST Content Repository.

    Attributes:
        config: A ContentConfig object with connection, logging, and other information.
    """
    def __init__(self, yaml_file):
        """
        Initializes the ContentServicesApi class from a YAML file.
        Args:
            yaml_file: [Mandatory] Path to the YAML configuration file.
        """
        self.config = ContentConfig(yaml_file)
 
    def search_index(self, index_search: IndexSearch) -> list:
        """
        Executes a search using an IndexSearch object.
        Args:
            index_search (IndexSearch): IndexSearch object with search parameters.
        Returns:
            list: List of objectIds resulting from the search.
        """
        search_obj = ContentSearch(self.config)
        return search_obj.search_index(index_search)
    
    def smart_chat(self, user_query, document_ids=None, conversation=""):
        """
        Interrogate Content Repository with Smart Chat.
        Args:
            user_query    : [Mandatory] The query to send to the Smart Chat API.
            document_ids: [Optional] An array of document IDs to limit the query scope.
            conversation: [Optional] A conversation ID to maintain context.           
        Returns:
            SmartChatResponse object.
        """
        smart_obj = ContentSmartChat(self.config)
        return smart_obj.smart_chat(user_query, document_ids, conversation)
 
    def archive_metadata(self, document_collection):
        """
        Archives a document using metadata.
        Args:
            document_collection: [Mandatory] ArchiveDocumentCollection object containing a list of documents with metadata.
        Returns:
            API response.
        """
        archive_obj = ContentArchiveMetadata(self.config)
        return archive_obj.archive_metadata(document_collection)

    def archive_policy(self, file_path, policy_name):
        """
        Archives a document using an archiving policy.
        Args:
            file_path: [Mandatory] Path to the file to archive.
            policy_name: [Mandatory] Name of an existing archiving policy in rocketcontent.
        Returns:
            API response.
        """
        archive_obj = ContentArchivePolicy(self.config)
        return archive_obj.archive_policy(file_path, policy_name)

    def archive_policy_plus(self, file_path, policy_name):
        """
        Archives a document using an archiving policy (plus version).
        Args:
            file_path: [Mandatory] Path to the file to archive.
            policy_name: [Mandatory] Name of an existing archiving policy in rocketcontent.
        Returns:
            API response.
        """
        archive_obj = ContentArchivePolicyPlus(self.config)
        return archive_obj.archive_policy(file_path, policy_name)

    def archive_policy_from_str(self, str_content, policy_name):
        """
        Archives a document using an archiving policy from a string.
        Args:
            str_content: [Mandatory] String to archive.
            policy_name: [Mandatory] Name of an existing archiving policy in rocketcontent.
        Returns:
            API response.
        """
        archive_obj = ContentArchivePolicy(self.config)
        return archive_obj.archive_policy_from_str(str_content, policy_name)
    
    # def create_content_class(self, content_class_json):
    #     admin_obj = ContentRepository(self.config)
    #     return admin_obj.create_content_class(content_class_json)
    
    # def create_index_group(self, index_group_json):
    #     admin_obj = ContentRepository(self.config)
    #     return admin_obj.create_index_group(index_group_json)
    
    def delete_document(self, document_id):
        """
        Delete a document in the Content Repository by ID.
        Args:
            document_id: [Mandatory] Document ID.
        Returns:
            API response (status code).
        """
        doc_obj = ContentDocument(self.config)
        return doc_obj.delete_document(document_id)
