Changelog
=========

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
