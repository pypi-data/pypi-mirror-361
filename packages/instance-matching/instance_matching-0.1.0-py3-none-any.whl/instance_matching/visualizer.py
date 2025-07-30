import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon

def plot(existing_instances, input_instances, map_perception_box, input_box):
    def plot_line(line, color, dot_color):
        x, y = line.xy
        plt.plot(x, y, color)
        plt.plot(x[0], y[0], 'o', color=dot_color, markersize=6, markeredgecolor='black')  # start
        plt.plot(x[-1], y[-1], 'o', color=dot_color, markersize=6, markeredgecolor='black')  # end

    plt.figure()

    for center_line in existing_instances['center_lines']['pts']:
        plot_line(center_line, 'r.', 'darkred')

    for lane_divider in existing_instances['lane_dividers']['pts']:
        plot_line(lane_divider, 'b.', 'navy')

    for center_line in input_instances['center_lines']['pts']:
        plot_line(center_line, 'm.', 'purple')

    for lane_divider in input_instances['lane_dividers']['pts']:
        plot_line(lane_divider, 'c.', 'teal')

    x, y = input_box.exterior.xy
    plt.plot(x, y, 'g-')

    if isinstance(map_perception_box, MultiPolygon):
        for poly in map_perception_box.geoms:
            x, y = poly.exterior.xy
            plt.plot(x, y, color='blue')
            plt.fill(x, y, color='skyblue', alpha=0.5)
    else:
        x, y = map_perception_box.exterior.xy
        plt.plot(x, y, color='blue')
        plt.fill(x, y, color='skyblue', alpha=0.5)

    plt.axis('equal')
    plt.show()
    