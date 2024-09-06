How to obtain a token
---------------------

To obtain a token, first identify the type of token you need, such as
an API, authentication, or access token. Register or sign up on the
relevant website or service, then navigate to the token generation area,
often found under sections like "API Keys," "Developer Settings," or
"Account Settings." Follow the instructions to request a new token,
providing any necessary information. Configure the token's permissions
based on your requirements and generate the token, ensuring you copy and
store it securely. Integrate the token into your application or system
as specified in the documentation, and keep it confidential by using
environment variables or secure vaults. Regularly monitor and manage
your tokens, revoking any that are no longer needed or compromised.

Roles and permissions
---------------------

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
| Collections list  | +       | +       | +       | +       |
| Favorite insert      | +         | +         | +         | +         |
| Favorite select      | + (owner) | + (owner) | + (owner) | + (owner) |
| Favorite delete      | + (owner) | + (owner) | + (owner) | + (owner) |
| Favorites list       | + (owner) | + (owner) | + (owner) | + (owner) |
| Revision select      | +         | +         | +         | +         |
| Revision download    | +         | +         | +         | +         |
| Revisions list       | +         | +         | +         | +         |
| Download select      | +         | +         | +         | +         |
| Downloads list       | +         | +         | +         | +         |
| Comment insert       |           | +         | +         | +         |
| Comment select       | +         | +         | +         | +         |
| Comment update       |           |           | + (owner) | + (owner) |
| Comment delete       |           |           | + (owner) | + (owner) |
| Comments list        | +         | +         | +         | +         |
| Option select        |           |           |           | +         |
| Option insert/update |           |           |           | +         |
| Option delete        |           |           |           | +         |
| Option list          |           |           |           | +         |
