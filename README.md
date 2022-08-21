# food-delivery

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
| Request type | URL | Description | Permissions |
|---|---|---|---|
| POST | merchant/restaurants/ | Create a restaurant | AllowAny |
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

| WebSocket Action | URL | Description | Permissions |
|---|---|---|
| subscribe_to_order_actvity | merchant/restaurants/{restaurant_id}/orders/ | Subscribe to orders | Authenticated |

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



# Backend Design 
- Maintain single source of truth for everything in models. 
- Request body processing happens in serializers only.
- Implement logic within model methods to encourage code reuse, whenever possible.
