## Level 1 — Initial Design & Basic Functions

- **`add_server(server_id, capacity)`**
  - Add a server. `RuntimeError` if `server_id` already exists.

- **`remove_server(server_id)`**
  - Remove a server. `RuntimeError` if it doesn't exist.

- **`route(request_id)`**
  - Route to the server with the **lowest current load**.
  - Ties broken by **lowest `server_id`** (string comparison).
  - Return the chosen `server_id`, or `None` if no server has capacity.
  - `RuntimeError` if the `request_id` is already active.

- **`complete(request_id)`**
  - Mark the request complete, freeing its slot.
  - `RuntimeError` if not active.
