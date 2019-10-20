from pygame import Vector2


class Line():

    def __init__(self, p1, p2):
        self.min_x = min(p1.x, p2.x)
        self.max_x = max(p1.x, p2.x)
        self.min_y = min(p1.y, p2.y)
        self.max_y = max(p1.y, p2.y)
        self.vertical = False
        if self.max_x - self.min_x < .001:
            self.vertical = True
        else:
            self.slope = (p2.y - p1.y) / (p2.x - p1.x)
            self.intercept = p2.y - (self.slope * p2.x)

    def __str__(self):
        return("Slope: {0}, Intecept: {1}".format(self.slope, self.intercept))

    def __repr__(self):
        return "{} {} {} {}".format(self.min_x,self.max_x, self.min_y, self.max_y)

    def intersect(self, other_line):
        # Where does this line intersect with the other line
        if self.vertical == True or other_line.vertical == True:
            return None
        if other_line.slope == self.slope:
            return None

        point_of_intersect_x = (
            other_line.intercept - self.intercept) / (self.slope - other_line.slope)

        if other_line.min_x <= point_of_intersect_x <= other_line.max_x:
            point_of_intersect_y = (self.slope * other_line.intercept -
                                    other_line.slope * self.intercept) / (self.slope - other_line.slope)

            # for x in range(round(point_of_intersect_x - 5), round(point_of_intersect_x + 6),5):
            point_of_intersect_y = other_line.slope * \
                point_of_intersect_x + other_line.intercept
            if other_line.min_y - 10 <= point_of_intersect_y <= other_line.max_y + 10:
                return Vector2(round(point_of_intersect_x), round(point_of_intersect_y))
        return None

