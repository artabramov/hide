# Changelog

## Version 0.0.33 (2024-08-31)
- Added revisions for uploaded files, enhancing the capability to manage
  and track different versions of files throughout their lifecycle.

## Version 0.0.33 (2024-08-31)
- Added a locking mechanism to prevent concurrent modifications of
  records. This feature ensures that all records of a specified model
  class are locked during critical operations, enhancing data integrity
  and consistency in multi-user environments.

## Version 0.0.31 (2024-08-29)
- Added filters for document count and document size in the collections
  list router.

## Version 0.0.30 (2024-08-27)
- Added external application description to Markdown (.md) file for
  improved documentation and user understanding.
- Added minor fixes to Pydantic schemas to enhance data validation and
  consistency.

## Version 0.0.29 (2024-08-25)
- Added an example extension for managing application hooks.
- Added lifecycle hooks for user actions, collection operations, and
  document management.

## Version 0.0.28 (2024-08-25)
- Added an editable field for user signatures, allowing users to input
  and update their signature information.
- Added tracking for the date when users last signed in.
- Added the ability for each user to define their own token expiration
  date upon login, providing flexibility in managing token validity.

## Version 0.0.27 (2024-08-25)
- Added favorites feature with endpoints for creating, retrieving,
  deleting, and listing favorites.

## Version 0.0.26 (2024-08-24)
- Added download tracking functionality, including a counter for
  document downloads and detailed record-keeping for each download event.
- Added endpoints and functionality to retrieve and manage download
  events, including listing and viewing individual downloads.

## Version 0.0.25 (2024-08-24)
- Added SQLAlchemy model and Pydantic schemas for comment management,
  including validation.
- Added full set of CRUD operations for comments, encompassing creation,
  retrieval, updating, and deletion functionalities.

## Version 0.0.24 (2024-08-24)
- Introduced subquery functionality in the entity manager for more
  complex querying capabilities.

## Version 0.0.23 (2024-08-23)
- Improved error handling to enhance the management and response to
  exceptions, including more precise logging and informative responses.
- Enhanced logging for requests and responses, including method, URL,
  headers, and status details.
- Improved extension initialization for more reliable loading and
  registration of hooks from extension modules.

## Version 0.0.22 (2024-08-23)
- Enhanced error handling across authentication and permission functions
  to provide more detailed and accurate error messages.

## Version 0.0.21 (2024-08-21)
- Added libraries to improve accessibility and streamline imports across
  the application.
- Refactored helper functions to be standalone and classless,
  simplifying their usage.
- Enhanced the E class by refining its structure and functionality.

## Version 0.0.20 (2024-08-18)
- Introduced the capability to add and manage tags associated with
  documents, enhancing metadata and search functionality.
- Enhanced cache management to prevent the storage of entities with
  broken relationships, ensuring data integrity.

## Version 0.0.19 (2024-08-18)
- Added a static endpoint for retrieving document thumbnails.
- Refactored code structure and organization for better maintainability
  and performance.

## Version 0.0.18 (2024-08-18)
- Implemented a route to retrieve document details by ID with access
  level checks and post-retrieval actions via a hook.

## Version 0.0.17 (2024-08-18)
- Added asynchronous file copying functionality to the FileManager
  class for efficient large file operations.
- Introduced methods for determining file types based on MIME types and
  added a VideoHelper class for video processing.
- Implemented automatic thumbnail generation for images and videos.
- Updated unit tests for new features and applied various minor fixes
  and improvements.

## Version 0.0.16 (2024-08-17)
- Upgraded docstrings for the EntityManager and FileManager classes to
  provide more detailed descriptions.

## Version 0.0.15 (2024-08-17)
- Enhanced Sphinx documentation generation scripts for more accurate and
  comprehensive outputs.
- Upgraded docstrings in the EntityManager class.