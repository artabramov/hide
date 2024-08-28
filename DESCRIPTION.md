## Roles and Permissions

This table details the permissions associated with different roles in
the application. It specifies what actions each role can perform,
including inserting, reading, updating, and deleting data. Use this
table to understand the access levels granted to each role within
the application.


| Action            | Reader  | Writer  | Editor  | Admin   |
|-------------------|---------|---------|---------|---------|
| Collection insert |         | +       | +       | +       |
| Collection select | +       | +       | +       | +       |
| Collection update |         |         | +       | +       |
| Collection delete |         |         |         | +       |