Changelog
=========

Version 0.0.27 (2024-08-25)
-------------

- Added favorites feature with endpoints for creating, retrieving,
  deleting, and listing favorites.

Version 0.0.26 (2024-08-24)
-------------

- Added download tracking functionality, including a counter for
  document downloads and detailed record-keeping for each download
  event.
- Added endpoints and functionality to retrieve and manage download
  events, including listing and viewing individual downloads.

Version 0.0.25 (2024-08-24)
-------------

- Added SQLAlchemy model and Pydantic schemas for comment management,
  including validation.
- Added full set of CRUD operations for comments, encompassing creation,
  retrieval, updating, and deletion functionalities.

Version 0.0.24 (2024-08-24)
-------------

- Introduced subquery functionality in the entity manager for more
  complex querying capabilities.

Version 0.0.23 (2024-08-23)
-------------

- Improved error handling to enhance the management and response to
  exceptions. The update includes more precise logging for both
  validation errors and unhandled exceptions, providing detailed
  information to aid in debugging. The responses now include appropriate
  HTTP status codes and informative messages, reflecting the nature of
  the errors more accurately.
- Enhanced logging for requests and responses. The middleware now logs
  request and response details more comprehensively, including request
  method, URL, headers, and response status and headers, to better track
  and diagnose issues during request processing.
- Improved extension initialization. Refined the process for
  initializing extensions to ensure more reliable loading and
  registration of hooks from extension modules.

Version 0.0.22 (2024-08-23)
-------------

- Enhanced error handling across authentication and permission functions
  to provide more detailed and accurate error messages.

Version 0.0.21 (2024-08-21)
-------------

- Added libraries to improve accessibility and streamline imports across
  the application.
- Refactored helper functions to be standalone and classless,
  simplifying their usage and reducing overhead.
- Enhanced the E class by refining its structure and functionality,
  leading to better handling of error details and a more streamlined
  initialization process.


Version 0.0.20 (2024-08-18)
-------------

- Introduced the capability to add and manage tags associated with
  documents, enhancing metadata and search functionality.
- Enhanced cache management to prevent the storage of entities with
  broken relationships, ensuring data integrity and reducing potential
  cache errors.

Version 0.0.19 (2024-08-18)
-------------

- Added a static endpoint for retrieving document thumbnails, enhancing
  document preview capabilities.
- Refactored code structure and organization for better maintainability
  and performance.

Version 0.0.18 (2024-08-18)
-------------
- Implemented a new route to retrieve document details by ID. This route
  ensures that the user has the appropriate access level and triggers
  post-retrieval actions via a hook. It provides a detailed response
  containing the document's metadata and content if found, otherwise
  returning a 404 error if the document does not exist.

Version 0.0.17 (2024-08-18)
-------------

- Added asynchronous file copying functionality to the FileManager class,
  allowing for efficient handling of large file operations by copying
  files in chunks. This new feature enhances performance and memory
  management during file operations.
- Introduced methods to the FileManager class for determining file types
  based on MIME types. The is_image method identifies image files, while
  the is_video method identifies video files, expanding the file type
  handling capabilities of the class.
- Updated the unit tests for FileManager to include new test cases for
  the recently added file copy and file type determination methods.
  These enhancements ensure that the new features are thoroughly tested
  and reliable.
- Added the VideoHelper class to facilitate video processing, including
  a method for extracting frames from video files. This class uses
  ffmpeg to handle various video file operations, expanding the library's
  capabilities in video handling.
- Implemented automatic thumbnail generation for uploaded images and
  videos, providing users with visual previews of their content. This
  feature enhances the user experience by making it easier to view and
  manage uploaded media.
- Applied various minor fixes and improvements throughout the codebase
  to address issues and refine functionality, ensuring a more stable and
  polished application.

Version 0.0.16 (2024-08-17)
-------------

- Upgraded docstrings for the EntityManager and FileManager classes to
  provide more detailed and consistent descriptions.

Version 0.0.15 (2024-08-17)
-------------

- Enhanced the scripts used for generating Sphinx documentation to
  improve the overall documentation process and ensure more accurate and
  comprehensive documentation outputs.
- Upgraded docstrings in the EntityManager class to provide more
  detailed and consistent descriptions.
