# Food Delivery Service API
This is a RESTFul API for a generic food delivery service with three apps — client, merchant, and rider. Also includes WebSocket endpoint for merchants to subscribe to new orders. 

Endpoints are split into different folders based on which app they service:
- `client/`: Endpoints for the app for end users.
- `merchant/`: Endpoints for the app for restaurant owners.
- `rider/`: Endpoints for the app for delivery riders.
- `delivery/`: Base app, contains common models and logic.

The server is meant to be deployed as a whole, and not as 3 separate services. 

# Backend Design 
- Maintain single source of truth for everything.
- Implement logic in model methods to encourage code reuse, whenever possible.
- Prefer Django REST Framework generics and patterns.
- Request body processing happens in serializers only.
- Only client users should be able to access client app endpoints, etc.

# Features
### Merchant app
- Restaurant management
  - Create a restaurant, menus, and use different menus for specific times and days of the week. 
  - Create or change menu items and item options.
  - Go on a holiday, and temporarily close the restaurant.
  - Pause taking orders for a specified amount of time, or resume business immediately from a pause.
- Order management
  - Subscribe to incoming orders via WebSocket.
  - Indicate that an order is ready for pickup (i.e. finished cooking).
  - Delay or cancel an order.
  - Adjust an order item based on specific customer requests.

### Client app
- Restaurant browsing
  - List restaurants.
  - Get restaurant details, including menu items, prices, reviews and average rating.
- Making orders
  - Make a delivery or self-pickup order.
  - Cancel or confirm order received.
  - Write a review for a restaurant you've recently ordered from.

### Rider app
- Session management
  - Start a new session (i.e. begin taking deliveries!).
  - End or extend the current session.
- Making deliveries
  - List currently available delivery orders to take.
  - Accept a delivery request.
  - Confirm order pickup from restaurant.
  - Confirm successful delivery to client.
  - Cancel a delivery.

# API Documentation
### Client App
| Request type | URL | Description | Permissions |
|---|---|---|---|
| POST | client/register/ | Register a client user | Any |
| GET | client/restaurants/ | List nearby restaurants | Authenticated |
| GET | client/restaurants/{restaurant_id} | Get restaurant details | Authenticated |
| GET | client/restaurants/{restaurant_id}/items/{item_id}/ | Get menu item details | Authenticated |
| GET | client/restaurants/{restaurant_id}/reviews/ | List restaurant reviews | Authenticated |
| GET | client/orders | List the client's orders | Authenticated |
| POST | client/orders/delivery/ | Make a delivery order | Authenticated |
| POST | client/orders/self-pickup/ | Make a self-pickup order | Authenticated |
| POST | client/orders/{order_id}/ | Get order detail | Authenticated |
| POST | client/orders/{order_id}/cancel/ | Cancel order | Authenticated |
| POST | client/orders/{order_id}/confirm-received/ | Confirm order received | Authenticated |
| POST | client/orders/{order_id}/review/ | Write a review for the restaurant | Authenticated |


### Merchant App
| WebSocket Action | URL | Description | Permissions |
|---|---|---|---|
| subscribe_to_order_actvity | merchant/restaurants/{restaurant_id}/orders/ | Subscribe to orders | Authenticated |

| Request type | URL | Description | Permissions |
|---|---|---|---|
| POST | merchant/restaurants/ | Create a restaurant | Any |
| GET | merchant/restaurants/{restaurant_id}/menu-hours/ | List the restaurant's menu hours | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/menu-hours/ | Update menu hours | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/status/ | Get restaurant status | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/status/ | Pause or resume taking orders | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/holidays/ | Get upcoming holidays | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/holidays/ | Create holidays | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/holidays/{holiday_id} | Get holiday details | Authenticated |
| PUT | merchant/restaurants/{restaurant_id}/holidays/{holiday_id} | Modify holiday details | Authenticated |
| DELETE | merchant/restaurants/{restaurant_id}/holidays/{holiday_id} | Delete holiday | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/menus/ | List restaurant menus | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/menus/ | Create a menu, and designate its menu hours | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/menus/{menu_id}/ | Get menu details | Authenticated |
| PUT | merchant/restaurants/{restaurant_id}/menus/{menu_id}/ | Update menu details | Authenticated |
| DESTROY | merchant/restaurants/{restaurant_id}/menus/{menu_id}/ | Delete menu | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/menus/{menu_id}/items/ | List menu items | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/menus/{menu_id}/items/ | Create a menu item | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/menus/{menu_id}/items/{item_id}/ | Get menu item details | Authenticated |
| PUT | merchant/restaurants/{restaurant_id}/menus/{menu_id}/items/{item_id}/ | Update menu item details | Authenticated |
| DESTROY | merchant/restaurants/{restaurant_id}/menus/{menu_id}/items/{item_id}/ | Delete menu item | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/orders/ | List orders for restaurant | Authenticated |
| GET | merchant/restaurants/{restaurant_id}/orders/{order_id}/ | Get order details | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/orders/{order_id}/finish-cooking/ | Finish cooking order, and signal for rider/client pickup | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/orders/{order_id}/cancel/ | Cancel order | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/orders/{order_id}/delay/ | Delay order by a specified amount of time | Authenticated |
| POST | merchant/restaurants/{restaurant_id}/orders/{order_id}/items/{order_item_id}/adjust-price/ | Make price adjustment to order item | Authenticated |


### Rider App
| Request type | URL | Description | Permissions |
|---|---|---|---|
| POST | rider/register/ | Register a rider account | Any |
| GET | rider/sessions/ | List past and current sessions | Authenticated|
| POST | rider/sessions/ | Start a new session | Authenticated|
| POST | rider/sessions/current/end/ | End the current session | Authenticated|
| POST | rider/sessions/current/extend/ | Extend the current session | Authenticated|
| POST | rider/sessions/current/orders/ | List orders under the current session | Authenticated|
| GET | rider/sessions/{session_id}/orders/ | List orders under the session | Authenticated|
| GET | rider/orders/ | List orders fulfilled by rider | Authenticated|
| GET | rider/orders/{order_id}/ | Get order details | Authenticated|
| POST | rider/orders/{order_id}/accept/ | Accept delivery request | Authenticated|
| POST | rider/orders/{order_id}/pickup/ | Confirm order pickup from restaurant | Authenticated|
| POST | rider/orders/{order_id}/complete/ | Confirm successful delivery to client | Authenticated|
| POST | rider/orders/{order_id}/cancel/ | Cancel order | Authenticated|

