def rect_collides_with_circle(rect, circle_center, circle_radius):
    cx, cy = circle_center

    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))

    dx = cx - closest_x
    dy = cy - closest_y

    return (dx * dx + dy * dy) <= (circle_radius * circle_radius)
