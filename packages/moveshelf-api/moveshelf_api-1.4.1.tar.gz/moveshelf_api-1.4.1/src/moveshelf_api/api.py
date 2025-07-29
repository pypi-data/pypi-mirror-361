"""
This module provides core components for interacting with Moveshelf, including data types and an API client
for managing projects, subjects, sessions, conditions, and clips. 

Dependencies:
    - Python standard library modules: `base64`, `json`, `logging`, `re`, `struct`, `os.path`
    - Third-party modules: `requests`, `six`, `enum` (optional), `crcmod`, `mypy_extensions`
"""

import base64
import json
import logging
import re
import struct
from datetime import datetime
from os import path
import enum
from typing import TypedDict

import urllib3
from urllib3.util import Retry
import six
from crcmod.predefined import mkPredefinedCrcFun

logger = logging.getLogger('moveshelf-api')

class TimecodeFramerate(enum.Enum):
    """
    Enum representing supported video framerates for timecodes.

    Attributes:
        FPS_24 (str): 24 frames per second.
        FPS_25 (str): 25 frames per second.
        FPS_29_97 (str): 29.97 frames per second.
        FPS_30 (str): 30 frames per second.
        FPS_50 (str): 50 frames per second.
        FPS_59_94 (str): 59.94 frames per second.
        FPS_60 (str): 60 frames per second.
        FPS_1000 (str): 1000 frames per second.
    """
    FPS_24 = '24'
    FPS_25 = '25'
    FPS_29_97 = '29.97'
    FPS_30 = '30'
    FPS_50 = '50'
    FPS_59_94 = '59.94'
    FPS_60 = '60'
    FPS_1000 = '1000'

Timecode = TypedDict('Timecode', {
    'timecode': str,
    'framerate': TimecodeFramerate
    })
"""
A typed dictionary representing a timecode.

Keys:
    - timecode (str): The timecode string in `HH:MM:SS:FF` format.
    - framerate (TimecodeFramerate): The framerate associated with the timecode.
"""

Metadata = TypedDict('Metadata', {
    'title': str,
    'description': str,
    'previewImageUri': str,
    'allowDownload': bool,
    'allowUnlistedAccess': bool,
    'startTimecode': Timecode
    }, total=False)
"""
A typed dictionary representing metadata for a clip.

Keys:
    - title (str): The title of the clip.
    - description (str): The description of the clip.
    - previewImageUri (str): The URI for the preview image.
    - allowDownload (bool): Whether downloading is allowed.
    - allowUnlistedAccess (bool): Whether unlisted access is allowed.
    - startTimecode (Timecode): Optional start timecode for the clip.
"""

class MoveshelfApi(object):
    """
    Client for interacting with the Moveshelf API.

    This class provides methods to manage projects, subjects, sessions, conditions, and clips on the Moveshelf platform.

    Attributes:
        api_url (str): The API endpoint URL.
        _auth_token (BearerTokenAuth): Authentication token for API requests.
        _crc32c (function): CRC32C checksum function for file validation.
        http (urllib3.PoolManager): HTTP client for making requests.
    """

    def __init__(self, api_key_file='mvshlf-api-key.json', api_url='https://api.moveshelf.com/graphql'):
        """
        Initialize the Moveshelf API client.

        Args:
            api_key_file (str): Path to the JSON file containing the API key. Defaults to 'mvshlf-api-key.json'.
            api_url (str): URL for the Moveshelf GraphQL API. Defaults to 'https://api.moveshelf.com/graphql'.

        Raises:
            ValueError: If the API key file is not found or invalid.
        """
        self._crc32c = mkPredefinedCrcFun('crc32c')
        self.api_url = api_url

        if not path.isfile(api_key_file):
            raise ValueError("No valid API key. Please check instructions on https://github.com/moveshelf/python-api-example")

        with open(api_key_file, 'r') as key_file:
            data = json.load(key_file)
            self._auth_token = BearerTokenAuth(data['secretKey'])

        # Configure retry strategy for urllib3
        retry_strategy = Retry(
            total=5,  # Maximum 5 total retries
            status_forcelist=[404, 500, 502, 503, 504],
            backoff_factor=5,  # With 5: ~5s, 10s, 20s (to get 10-120s range)
            backoff_max=120,  # Maximum 120 seconds wait time
            allowed_methods=["PUT", "POST"],  # Only methods used by this API
            raise_on_status=True,  # Raise exception after retry exhaustion
            respect_retry_after_header=True,  # Respect server's Retry-After header
        )

        # Initialize urllib3 PoolManager with retry strategy
        self.http = urllib3.PoolManager(
            retries=retry_strategy,
            timeout=urllib3.Timeout(connect=10, read=120)
        )

    def getProjectDatasets(self, project_id):
        """
        Retrieve datasets for a given project.

        Args:
            project_id (str): The ID of the project.

        Returns:
            list: A list of datasets, each containing `name` and `downloadUri`.
        """
        data = self._dispatch_graphql(
            '''
            query getProjectDatasets($projectId: ID!) {
            node(id: $projectId) {
                ... on Project {
                id,
                name,
                datasets {
                    name,
                    downloadUri
                }
                }
            }
            }
            ''',
            projectId=project_id
        )
        return [d for d in data['node']['datasets']]

    def getUserProjects(self):
        """
        Retrieve all projects associated with the current user.

        Returns:
            list: A list of dictionaries, each containing the `name` and `id` of a project.
        """
        data = self._dispatch_graphql(
            '''
            query {
                viewer {
                    projects {
                        name
                        id
                    }
                }
            }
            '''
        )
        return [{k: v for k, v in p.items() if k in ['name', 'id']} for p in data['viewer']['projects']]

    def createClip(self, project, metadata=Metadata()):
        """
        Create a new clip in the specified project with optional metadata.

        Args:
            project (str): The project ID.
            metadata (Metadata): Metadata for the new clip. Defaults to an empty Metadata dictionary.

        Returns:
            str: The ID of the created clip.
        """
        creation_response = self._createClip(project, {
            'clientId': 'manual',
            'metadata': metadata
        })
        logging.info('Created clip ID: %s', creation_response['mocapClip']['id'])

        return creation_response['mocapClip']['id']

    def uploadFile(self, file_path, project, metadata=None):
        """
        Upload a file to a specified project.

        Args:
            file_path (str): The local path to the file being uploaded.
            project (str): The project ID where the file will be uploaded.
            metadata (dict): Metadata for the file. Defaults to an empty dict.

        Returns:
            str: The ID of the created clip.
        """
        if metadata is None:
            metadata = Metadata()

        logger.info("Uploading %s", file_path)

        metadata["title"] = metadata.get("title", path.basename(file_path))
        metadata["allowDownload"] = metadata.get("allowDownload", False)
        metadata["allowUnlistedAccess"] = metadata.get("allowUnlistedAccess", False)

        if metadata.get("startTimecode"):
            self._validateAndUpdateTimecode(metadata["startTimecode"])

        creation_response = self._createClip(
            project,
            {
                "clientId": file_path,
                "crc32c": self._calculateCrc32c(file_path),
                "filename": path.basename(file_path),
                "metadata": metadata,
            },
        )
        logging.info("Created clip ID: %s", creation_response["mocapClip"]["id"])

        # Upload file using urllib3
        with open(file_path, "rb") as fp:
            file_data = fp.read()

        try:
            response = self.http.request(
                "PUT",
                creation_response["uploadUrl"],
                body=file_data,
                headers={"Content-Type": "application/octet-stream"},
            )
            if response.status >= 400:
                raise urllib3.exceptions.HTTPError(
                    f"Upload failed with status {response.status}: {response.reason}"
                )
        except urllib3.exceptions.MaxRetryError as e:
            logger.error(f"All retries exhausted during file upload: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during file upload: {e}")
            raise

        return creation_response["mocapClip"]["id"]

    def uploadAdditionalData(self, file_path, clipId, dataType, filename):
        """
        Upload additional data to an existing clip.

        Args:
            file_path (str): The local path to the file being uploaded.
            clipId (str): The ID of the clip to associate with the data.
            dataType (str): The type of the additional data (e.g., 'video', 'annotation').
            filename (str): The name to assign to the uploaded file.

        Returns:
            str: The ID of the uploaded data.
        """
        logger.info("Uploading %s", file_path)

        creation_response = self._createAdditionalData(
            clipId,
            {
                "clientId": file_path,
                "crc32c": self._calculateCrc32c(file_path),
                "filename": filename,
                "dataType": dataType,
            },
        )
        logging.info("Created additional data ID: %s", creation_response["data"]["id"])

        # Upload file using urllib3
        with open(file_path, "rb") as fp:
            file_data = fp.read()

        try:
            response = self.http.request(
                "PUT",
                creation_response["uploadUrl"],
                body=file_data,
                headers={"Content-Type": "application/octet-stream"},
            )
            if response.status >= 400:
                raise urllib3.exceptions.HTTPError(
                    f"Upload failed with status {response.status}: {response.reason}"
                )
        except urllib3.exceptions.MaxRetryError as e:
            logger.error(f"All retries exhausted during additional data upload: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during additional data upload: {e}")
            raise

        return creation_response["data"]["id"]

    def updateClipMetadata(self, clip_id: str, metadata: dict, custom_options: str = None):
        """
        Update the metadata for an existing clip.

        Args:
            clip_id (str): The ID of the clip to update.
            metadata (dict): The updated metadata for the clip.
            custom_options (str, optional): JSON string containing clip custom options. Defaults to None

        Returns:
            None
        """
        logger.info('Updating metadata for clip: %s', clip_id)

        if metadata.get('startTimecode'):
            self._validateAndUpdateTimecode(metadata['startTimecode'])

        res = self._dispatch_graphql(
            '''
            mutation updateClip($input: UpdateClipInput!) {
                updateClip(clipData: $input) {
                    clip {
                        id
                    }
                }
            }
            ''',
            input={
                'id': clip_id,
                'metadata': metadata,
                'customOptions': custom_options
            }
        )
        logging.info('Updated clip ID: %s', res['updateClip']['clip']['id'])

    def createSubject(self, project_id, name):
        """
        Create a new subject within a project.

        Args:
            project_id (str): The ID of the project where the subject will be created.
            name (str): The name of the new subject.

        Returns:
            dict: A dictionary containing the `id` and `name` of the created subject.
        """
        data = self._dispatch_graphql(
            '''
                mutation createPatientMutation($projectId: String!, $name: String!) {
                    createPatient(projectId: $projectId, name: $name) {
                        patient {
                            id
                            name
                        }
                    }
                }
            ''',
            projectId=project_id,
            name=name
        )

        return data['createPatient']['patient']

    def updateSubjectMetadataInfo(self, subject_id, info_to_save, skip_validation: bool = False):
        """
        Update the metadata for an existing subject.

        Args:
            subject_id (str): The ID of the subject to update.
            info_to_save (dict): The metadata to save for the subject.
            skip_validation (bool, optional): True to skip metadata validation, False otherwise. Defaults to False.

        Returns:
            bool: Whether the metadata update was successful.
        """
        # Update subject metadata info:
        # 1) if skip_validation == False, validate the imported metadata and check if there are validation errors
        # 2) if there are no validation errors, we retrieve existing metadata and merge existing subject metadata
        # and imported metadata to update only empty fields (only for subject metadata, interventions are always
        #  overridden), and update metadata. Otherwise we print validation errors and skip the update

        my_imported_metadata = json.loads(info_to_save)
        imported_intervention_metadata = my_imported_metadata.get("interventions", [])
        imported_subject_metadata = my_imported_metadata
        if "interventions" in imported_subject_metadata.keys():
            imported_subject_metadata.pop("interventions")

        # Validate metadata only if skip_validation == False
        if not skip_validation:
            has_subject_metadata_errors = False
            has_intervention_errors = False
            # First we validate subject metadata
            subject_metadata_validation = self._dispatch_graphql(
                '''
                    query MetadataValidator(
                        $importedMetadata: String!,
                        $whichTabToValidate: String!,
                        $sessionId: String,
                        $subjectId: String
                        ) {
                        metadataValidator(
                            importedMetadata: $importedMetadata,
                            whichTabToValidate: $whichTabToValidate,
                            sessionId: $sessionId,
                            subjectId: $subjectId
                        )
                        {
                        validationErrors
                        }
                        }
                ''',
                importedMetadata = json.dumps(imported_subject_metadata),
                whichTabToValidate = "subjectMetadata",
                subjectId = subject_id
            )

            if len(subject_metadata_validation["metadataValidator"]["validationErrors"]) > 0:
                has_subject_metadata_errors = True
                print("The following errors with subject metadata were found:")
                for validation_error in subject_metadata_validation["metadataValidator"]["validationErrors"]:
                    print(validation_error)

            # Now we validate intervention metadata
            intervention_metadata_validation = self._dispatch_graphql(
                '''
                    query MetadataValidator(
                        $importedMetadata: String!,
                        $whichTabToValidate: String!,
                        $sessionId: String,
                        $subjectId: String
                        ) {
                        metadataValidator(
                            importedMetadata: $importedMetadata,
                            whichTabToValidate: $whichTabToValidate,
                            sessionId: $sessionId,
                            subjectId: $subjectId
                        )
                        {
                        validationErrors
                        }
                        }
                ''',
                importedMetadata = json.dumps(imported_intervention_metadata),
                whichTabToValidate = "interventionMetadata",
                subjectId = subject_id
            )

            if len(intervention_metadata_validation["metadataValidator"]["validationErrors"]) > 0:
                has_intervention_errors = True
                print("The following errors with intervention metadata were found:")
                for validation_error in intervention_metadata_validation["metadataValidator"]["validationErrors"]:
                    print(validation_error)

            if has_subject_metadata_errors or has_intervention_errors:
                return subject_metadata_validation["metadataValidator"]["validationErrors"].extend(intervention_metadata_validation["metadataValidator"]["validationErrors"])

        # Retrieve existing metadata
        data = self._dispatch_graphql(
            '''
            query getPatient($patientId: ID!) {
                node(id: $patientId) {
                    ... on Patient {
                        id,
                        metadata
                    }
                }
            }
            ''',
            patientId=subject_id
        )

        metadata_str = data['node'].get('metadata')
        if metadata_str is not None:
            existing_metadata = json.loads(metadata_str)
        else:
            existing_metadata = None

        existing_intervention_metadata = existing_metadata.get("interventions", []) if existing_metadata else []
        existing_subject_metadata = existing_metadata if existing_metadata else {}
        if "interventions" in existing_subject_metadata.keys():
            existing_subject_metadata.pop("interventions")

        # Merge dictionaries
        merged_subject_metadata = self._merge_metadata_dictionaries(existing_subject_metadata, imported_subject_metadata)
        if len(imported_intervention_metadata) > 0:
            merged_subject_metadata["interventions"] = imported_intervention_metadata


        data = self._dispatch_graphql(
            '''
                mutation updatePatientMutation($patientId: ID!, $metadata: JSONString) {
                    updatePatient(patientId: $patientId, metadata: $metadata) {
                        updated
                    }
                }
            ''',
            patientId=subject_id,
            metadata=json.dumps(merged_subject_metadata)
        )

        return data['updatePatient']['updated']

    def getSubjectContext(self, subject_id):
        """
        Retrieve the context information for a specific subject.

        Args:
            subject_id (str): The ID of the subject to retrieve.

        Returns:
            dict: A dictionary containing subject details such as ID, name, metadata,
                  and associated project information (i.e., project ID, description, canEdit permission, and unlistedAccess permission).
        """
        data = self._dispatch_graphql(
            '''
                query getPatientContext($patientId: ID!) {
                    node(id: $patientId) {
                        ... on Patient {
                            id,
                            name,
                            metadata,
                            project {
                                id
                                description
                                canEdit
                                unlistedAccess
                            }
                        }
                    }
                }
            ''',
            patientId=subject_id
        )

        return data['node']

    def createSession(
        self, project_id, session_path, subject_id, session_date: str | None = None
    ):
        """
        Create a session for a specified subject within a project.

        Args:
            project_id (str): The ID of the project where the session will be created.
            session_path (str): The path to associate with the session.
            subject_id (str): The ID of the subject for whom the session is created.
            session_date (str, optional): The date of the session in `YYYY-MM-DD` format.

        Returns:
            dict: A dictionary containing the session's ID and project path.
        """

        create_session_date = None

        # Check if session_date is provided
        if session_date:
            # Validate the date format
            try:
                datetime.strptime(session_date, "%Y-%m-%d")
                create_session_date = session_date
            except ValueError:
                # If the date format is invalid, raise an error and return
                print("Invalid date format. Please use YYYY-MM-DD.")
                return

        # If session_date is not provided or is invalid, extract it from the session_path
        if not create_session_date:
            # Split the path and extract the session date
            # Assuming path is always in format "/subjectName/YYYY-MM-DD/"
            session_path_parts = session_path.strip("/").split("/")

            # The date should be the last part if path follows the expected format
            if len(session_path_parts) >= 2:
                my_session = session_path_parts[1]

                # Try to validate the date format
                try:
                    datetime.strptime(my_session, "%Y-%m-%d")
                    create_session_date = my_session
                except ValueError:
                    # If the date format is invalid, keep it None
                    pass

        data = self._dispatch_graphql(
            """
                mutation createSessionMutation($projectId: String!, $projectPath: String!, $patientId: ID!, $sessionDate: String) {
                    createSession(projectId: $projectId, projectPath: $projectPath, patientId: $patientId, sessionDate: $sessionDate) {
                        session {
                            id
                            projectPath
                        }
                    }
                }
            """,
            projectId=project_id,
            projectPath=session_path,
            patientId=subject_id,
            sessionDate=create_session_date,
        )

        return data["createSession"]["session"]

    def updateSessionMetadataInfo(self, session_id: str, session_name: str, session_metadata: str, skip_validation: bool = False, session_date = None, previous_updated_at = None):
        """
        Update the metadata for an existing session.

        Args:
            session_id (str): The ID of the session to update.
            session_name (str): The new name for the session to update.
            session_metadata (str): The metadata to save for the session.
            skip_validation (bool, optional): True to skip metadata validation, False otherwise. Defaults to False.
            session_date (str, optional): The new date for the session to update. If empty, skips update of session date. Defaults to None.
            previous_updated_at (str, optional): The previous updated in ISO format. If empty, force update. Defaults to None.

        Returns:
            bool: Whether the metadata update was successful.
        """
        # Update session metadata info:
        # 1) if skip_validation == False, validate the imported metadata and check if there are validation errors
        # 2) if there are no validation errors, retrieve existing metadata, merge existing metadata and imported 
        # metadata to update only empty fields, and update metadata. Otherwise we print validation errors and skip the update

        my_imported_metadata = json.loads(session_metadata).get("metadata", {})
        
        # Validate metadata only if skip_validation == False 
        if not skip_validation:
            data = self._dispatch_graphql(
                '''
                    query MetadataValidator(
                        $importedMetadata: String!,
                        $whichTabToValidate: String!,
                        $sessionId: String,
                        $subjectId: String
                        ) {
                        metadataValidator(
                            importedMetadata: $importedMetadata,
                            whichTabToValidate: $whichTabToValidate,
                            sessionId: $sessionId,
                            subjectId: $subjectId
                        )
                        {
                        validationErrors
                        }
                        }
                ''',
                importedMetadata=json.dumps(my_imported_metadata),
                whichTabToValidate="sessionMetadata",
                sessionId=session_id
            )

            if len(data["metadataValidator"]["validationErrors"]) > 0:
                print("The following errors with session metadata were found:")
                for validation_error in data["metadataValidator"]["validationErrors"]:
                    print(validation_error)
                return data["metadataValidator"]["validationErrors"]

        # Retrieve existing metadata
        data = self._dispatch_graphql(
            '''
            query getSessionMetadata($sessionId: ID!) {
                node(id: $sessionId) {
                    ... on Session {
                        id,
                        metadata
                    }
                }
            }
            ''',
            sessionId=session_id
        )

        metadata_str = data['node'].get('metadata')
        metadata_obj = json.loads(metadata_str) if metadata_str is not None else {}
        existing_metadata = metadata_obj.get("metadata", None)
        
        # Merge dictionaries and write into resulting dict
        merged_metadata = self._merge_metadata_dictionaries(existing_metadata, my_imported_metadata)
        metadata_obj["metadata"] = merged_metadata

        # Update session metadata
        data = self._dispatch_graphql(
            '''
                mutation updateSession($sessionId: ID!, $sessionName: String!, $sessionMetadata: JSONString, $sessionDate: String, $previousUpdatedAt: String) {
                    updateSession(
                        sessionId: $sessionId,
                        sessionName: $sessionName,
                        sessionMetadata: $sessionMetadata,
                        sessionDate: $sessionDate,
                        previousUpdatedAt: $previousUpdatedAt
                    ) {
                        updated
                    }
                }
            ''',
            sessionId=session_id,
            sessionName=session_name,
            sessionMetadata=json.dumps(metadata_obj),
            sessionDate=session_date,
            previousUpdatedAt=previous_updated_at
        )

        return data['updateSession']['updated']

    @staticmethod
    def _merge_metadata_dictionaries(existing_metadata: dict, imported_metadata: dict):
        """
        Merge existing metadata and imported metadata dictionaries. The objective is to
        only update fields in the existing metadata that are empty
        
        Args:
            existing_metadata (dict): Current metadata available on Moveshelf.
            imported_metadata (dict): Metadata to be imported.

        Returns:
            dict: Merged dictionary.

        """
        # Merge dictionaries
        if existing_metadata:
            merged_metadata = existing_metadata.copy()  
            for key, value in existing_metadata.items():
                # Case 1: Empty string
                if isinstance(value, str) and value == "":
                    if key in imported_metadata:
                        merged_metadata[key] = imported_metadata[key]

                # Case 2: Dict with empty "value"
                elif isinstance(value, dict):
                    if value.get("value") in ["", []]: 
                        if key in imported_metadata:
                            merged_metadata[key] = imported_metadata[key]

                # Case 3: List of dicts
                elif isinstance(value, list):
                    for i, entry in enumerate(value):
                        if isinstance(entry, dict) and entry.get("value") in ["", []]:
                            if "context" in entry:
                                # Match by context
                                if key in imported_metadata:
                                    imported_entries = imported_metadata.get(key, [])
                                    for imported_entry in imported_entries:
                                        if (
                                            isinstance(imported_entry, dict)
                                            and imported_entry.get("context") == entry["context"]
                                        ):
                                            merged_metadata[key][i] = imported_entry
                            else:
                                if key in imported_metadata:
                                    merged_metadata[key] = imported_metadata[key]
            
            # Now we add keys that were not in existing_metadata
            for key, value in imported_metadata.items():
                if key not in merged_metadata.keys():
                    merged_metadata[key] = value
        else:
            merged_metadata = imported_metadata
        
        return merged_metadata

    def getProjectClips(self, project_id, limit, include_download_link=False):
        """
        Retrieve clips from a specified project.

        Args:
            project_id (str): The ID of the project from which to fetch clips.
            limit (int): The maximum number of clips to retrieve.
            include_download_link (bool): Whether to include download link information in the result. Defaults to False.

        Returns:
            list: A list of dictionaries, each containing clip information such as ID, title, and project path. 
                  If `include_download_link` is True, includes file name and download URI.
        """
        query = '''
            query getAdditionalDataInfo($projectId: ID!, $limit: Int) {
            node(id: $projectId) {
                ... on Project {
                id,
                name,
                clips(first: $limit) {
                edges {
                    node {
                        id,
                        title,
                        projectPath
                    }
                    }
                }
                }
            }
            }
            '''
        if include_download_link:
            query = '''
                query getAdditionalDataInfo($projectId: ID!, $limit: Int) {
                node(id: $projectId) {
                    ... on Project {
                    id,
                    name,
                    clips(first: $limit) {
                    edges {
                        node {
                            id,
                            title,
                            projectPath
                            originalFileName
                            originalDataDownloadUri
                        }
                        }
                    }
                    }
                }
                }
                '''

        data = self._dispatch_graphql(
            query,
            projectId=project_id,
            limit=limit
        )

        return [c['node'] for c in data['node']['clips']['edges']]

    def getAdditionalData(self, clip_id):
        """
        Retrieve additional data associated with a specific clip.

        Args:
            clip_id (str): The ID of the clip for which to fetch additional data.

        Returns:
            list: A list of dictionaries, each containing details about additional data, including:
                  ID, data type, upload status, original file name, preview data URI, 
                  and original data download URI.
        """
        data = self._dispatch_graphql(
            '''
            query getAdditionalDataInfo($clipId: ID!) {
            node(id: $clipId) {
                ... on MocapClip {
                id,
                additionalData {
                    id
                    dataType
                    uploadStatus
                    originalFileName
                    previewDataUri
                    originalDataDownloadUri
                }
                }
            }
            }
            ''',
            clipId=clip_id
        )

        return data['node']['additionalData']

    def getClipData(self, clip_id):
        """
        Retrieve information about a specific clip.

        Args:
            clip_id (str): The ID of the clip to retrieve.

        Returns:
            dict: A dictionary containing the clip's ID, title, description, and custom options.
        """
        data = self._dispatch_graphql(
            '''
            query getClipInfo($clipId: ID!) {
            node(id: $clipId) {
                ... on MocapClip {
                id,
                title,
                description,
                customOptions
                }
            }
            }
            ''',
            clipId=clip_id
        )

        return data['node']

    def getProjectAndClips(self):
        """
        Retrieve a list of all projects and the first 20 clips associated with each project.

        Returns:
            list: A list of dictionaries, where each dictionary contains project details 
                  (ID and name) and a nested list of clip details (ID and title).
        """
        data = self._dispatch_graphql(
            '''
            query {
                viewer {
                    projects {
                        id
                        name
                        clips(first: 20) {
                            edges {
                                node {
                                    id,
                                    title
                                    }
                                }
                            }
                    }
                }
            }
            '''
        )
        return [p for p in data['viewer']['projects']]
    
    def getProjectSubjects(self, project_id):
        """
        Retrieve all subjects (patients) associated with a specific project.

        Args:
            project_id (str): The ID of the project to retrieve subjects for.

        Returns:
            list: A list of dictionaries, each containing the subject's ID, name, update date, and externalId (i.e., EHR-ID/MRN).
        """
        data = self._dispatch_graphql(
            '''
            query getProjectPatients($projectId: ID!) {
                node(id: $projectId) {
                    ... on Project {
                        id,
                        name,
                        description,
                        configuration,
                        canEdit,
                        template {
                            name,
                            data  
                        },
                        patientsList {
                            id
                            name
                            updated
                            externalId
                        }
                    }
                }
            }
            ''',
            projectId=project_id
        )
        return data['node']['patientsList']
    
    def getProjectSubjectByEhrId(self, ehr_id, project_id):
        """
        Retrieve the subject with the specified ehr_id associated with a specific project.

        Args:
            ehr_id (str): The EHR-ID/MRN of the subject to be retrieved
            project_id (str): The ID of the project to retrieve the subject for.
        Returns:
            dict: A dictionary containing the subject's ID and name. Returns None if no subject with
                matching EHR-ID/MRN exists in the specified project.
        """
        data = self._dispatch_graphql(
            '''
            query getPatientByEhrId($ehrId: String!, $projectId: String!) {
                patient(ehrId: $ehrId, projectId: $projectId) {
                id
                name
                }
            }
            ''',
            ehrId=ehr_id,
            projectId=project_id
        )
        return data['patient']

    def getSubjectDetails(self, subject_id):
        """
        Retrieve details about a specific subject, including metadata, 
        associated projects, reports, sessions, clips, and norms.

        Args:
            subject_id (str): The ID of the subject to retrieve.

        Returns:
            dict: A dictionary containing the subject's details, including:
                  - ID, name, and metadata.
                  - Associated project details (ID).
                  - List of reports (ID and title).
                  - List of sessions with nested clips and norms details.
        """
        data = self._dispatch_graphql(
            '''
            query getPatient($patientId: ID!) {
                node(id: $patientId) {
                    ... on Patient {
                        id,
                        name,
                        metadata,
                        project {
                            id
                        }
                        reports {
                            id
                            title
                        }
                        sessions {
                            id
                            projectPath
                            clips {
                                id
                                title
                                created
                                projectPath
                                uploadStatus
                                hasCharts
                            }
                            norms {
                                id
                                name
                                uploadStatus
                                projectPath
                                clips {
                                    id
                                    title
                                }
                            }
                        }
                    }
                }
            }
            ''',
            patientId=subject_id
        )
        return data['node']

    def processGaitTool(self, clip_ids, trial_type):
        """
        Submit a Gait Tool processing job for the specified clips and trial type.

        Args:
            clip_ids (list): A list of clip IDs to process.
            trial_type (str): The trial type for the processing job.

        Returns:
            str: The job ID of the created processing task.
        """
        data = self._dispatch_graphql(
            '''
            mutation processGaitTool($clips: [String!], $trialType: String) {
                processGaitTool(clips: $clips, trialType: $trialType) {
                    jobId
                }
            }
            ''',
            clips=clip_ids,
            trialType=trial_type
        )
        return data['processGaitTool']['jobId']

    def getJobStatus(self, job_id):
        """
        Retrieve the status of a specific job by its ID.

        Args:
            job_id (str): The ID of the job to check.

        Returns:
            dict: A dictionary containing the job's ID, status, result, and description.
        """
        data = self._dispatch_graphql(
            '''
            query jobStatus($jobId: ID!) {
                node(id: $jobId) {
                    ... on Job {
                        id,
                        status,
                        result,
                        description
                    }
                }
            }
            ''',
            jobId=job_id
        )
        return data['node']

    def getSessionById(self, session_id):
        """
        Retrieve detailed information about a session by its ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            dict: A dictionary containing session details, including:
                  - ID, projectPath, and metadata.
                  - Associated project, clips, norms, and patient information.
        """
        data = self._dispatch_graphql(
            '''
            query getSession($sessionId: ID!) {
                node(id: $sessionId) {
                    ... on Session {
                        id,
                        projectPath,
                        metadata,
                        project {
                            id
                            name
                            canEdit
                        }
                        clips {
                            id
                            title
                            created
                            projectPath
                            uploadStatus
                            hasCharts
                            hasVideo
                        }
                        norms {
                            id
                            name
                            uploadStatus
                            projectPath
                            clips {
                                id
                                title
                            }
                        }
                        patient {
                        id
                        name
                        }
                    }
                }
            }
            ''',
            sessionId=session_id
        )
        return data['node']

    def _validateAndUpdateTimecode(self, tc):
        """
        Validate and update a timecode dictionary.

        Args:
            tc (dict): A dictionary containing timecode and framerate information.

        Raises:
            AssertionError: If timecode or framerate is invalid.
        """
        assert tc.get('timecode')
        assert tc.get('framerate')
        assert isinstance(tc['framerate'], TimecodeFramerate)
        assert re.match('\d{2}:\d{2}:\d{2}[:;]\d{2,3}', tc['timecode'])
        tc['framerate'] = tc['framerate'].name

    def _createClip(self, project, clip_creation_data):
        """
        Create a new clip in the specified project.

        Args:
            project (str): The ID of the project where the clip will be created.
            clip_creation_data (dict): The data required to create the clip.

        Returns:
            dict: A dictionary containing the client ID, upload URL, and clip ID.
        """
        data = self._dispatch_graphql(
            '''
            mutation createClip($input: ClipCreationInput!) {
                createClips(input: $input) {
                    response {
                        clientId,
                        uploadUrl,
                        mocapClip {
                            id
                        }
                    }
                }
            }
            ''',
            input={
                'project': project,
                'clips': [clip_creation_data]
            }
        )
        return data['createClips']['response'][0]

    def _calculateCrc32c(self, file_path):
        """
        Calculate the CRC32C checksum of a file.

        Args:
            file_path (str): The path to the file to calculate the checksum for.

        Returns:
            str: The Base64-encoded CRC32C checksum.
        """
        with open(file_path, 'rb') as fp:
            crc = self._crc32c(fp.read())
            b64_crc = base64.b64encode(struct.pack('>I', crc))
            return b64_crc if six.PY2 else b64_crc.decode('utf8')

    def _createAdditionalData(self, clipId, metadata):
        """
        Create additional data for a specific clip.

        Args:
            clipId (str): The ID of the clip to associate the additional data with.
            metadata (dict): Metadata for the additional data, including data type and filename.

        Returns:
            dict: A dictionary containing the upload URL and data details (ID, type, and upload status).
        """
        data = self._dispatch_graphql(
            '''
            mutation createAdditionalData($input: CreateAdditionalDataInput) {
                createAdditionalData(input: $input) {
                uploadUrl
                data {
                    id
                    dataType
                    originalFileName
                    uploadStatus
                }
                }
            }
            ''',
            input={
                'clipId': clipId,
                'dataType': metadata['dataType'],
                'crc32c': metadata['crc32c'],
                'filename': metadata['filename'],
                'clientId': metadata['clientId']
            }
        )
        return data['createAdditionalData']

    def _dispatch_graphql(self, query, **kwargs):
        """
        Send a GraphQL query or mutation to the API and return the response data.

        Args:
            query (str): The GraphQL query or mutation string.
            **kwargs: Variables to be passed into the GraphQL query.

        Raises:
            urllib3.exceptions.HTTPError: If the HTTP request fails.
            GraphQlException: If the GraphQL response contains errors.

        Returns:
            dict: The `data` field from the GraphQL response, containing the requested information.
        """
        payload = {"query": query, "variables": kwargs}

        # Prepare headers with authentication
        headers = {
            "Content-Type": "application/json",
            **self._auth_token.get_auth_header(),
        }

        try:
            response = self.http.request(
                "POST",
                self.api_url,
                body=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )

            if response.status >= 400:
                raise urllib3.exceptions.HTTPError(
                    f"GraphQL request failed with status {response.status}: {response.reason}"
                )

            json_data = json.loads(response.data.decode("utf-8"))

            if "errors" in json_data:
                raise GraphQlException(json_data["errors"])

            return json_data["data"]

        except urllib3.exceptions.MaxRetryError as e:
            logger.error(f"All retries exhausted for GraphQL request: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during GraphQL request: {e}")
            raise


class BearerTokenAuth:
    """
    A custom authentication class for using Bearer tokens with HTTP requests.
    Adapted for urllib3 from the original requests-based version.

    Attributes:
        _auth (str): The formatted Bearer token string.
    """

    def __init__(self, token):
        """
        Initialize the BearerTokenAuth instance with a token.

        Args:
            token (str): The Bearer token to use for authentication.
        """
        self._auth = 'Bearer {}'.format(token)

    def get_auth_header(self):
        """
        Get the Authorization header dictionary for urllib3 requests.

        Returns:
            dict: Dictionary containing the Authorization header.
        """
        return {'Authorization': self._auth}



class GraphQlException(Exception):
    """
    An exception raised when a GraphQL response contains errors.

    Attributes:
        error_info (list): A list of error information returned by the GraphQL API.
    """

    def __init__(self, error_info):
        """
        Initialize the GraphQlException with error information.

        Args:
            error_info (list): The list of errors from the GraphQL response.
        """
        self.error_info = error_info
