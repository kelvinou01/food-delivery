from datetime import timedelta
import math

def calc_distance_from_coords(lat_1, lon_1, lat_2, lon_2):
    EARTH_RADIUS = 6371e3  # meters
    phi_1 = lat_1 * math.pi / 180  # radians
    phi_2 = lat_2 * math.pi / 180   # radians
    delta_phi = (lat_2 - lat_1) * math.pi / 180  
    delta_lambda = (lon_2 - lon_1) * math.pi / 180

    a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) \
        + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2) * math.sin(delta_lambda / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c  # meters

def round_to_base(x, base=5):
    return base * round(x/base)
    
def calc_delivery_cost(restaurant, user_latitude, user_longitude):
    dist = calc_distance_from_coords(float(restaurant.latitude), float(restaurant.longitude), 
                                     float(user_latitude), float(user_longitude))
    return round(dist * 2, 1)

def calc_delivery_time(restaurant, user_latitude, user_longitude):
    dist = calc_distance_from_coords(restaurant.latitude, restaurant.longitude, 
                                     user_latitude, user_longitude)
    transit_time = timedelta(minutes=round_to_base(20 + dist * 60 / 20, 5))
    return transit_time + restaurant.order_fulfillment_time
    
    