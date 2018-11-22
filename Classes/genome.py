import copy
import cv2
from Classes.gene import *


class Genome:

    def __init__(self, vertices, number_of_genes, width, height, shapes_ratio, mutation_probability, soft_mutate_rate,
                 fitness, start_width,start_height):
        self.soft_mutate_rate = soft_mutate_rate
        self.mutation_probability = mutation_probability
        self.vertices = vertices
        self.number_of_genes = number_of_genes
        self.height = height
        self.width = width
        self.shapes_ratio = shapes_ratio
        self.genome = []
        self.start_genome = None
        self.generate_genome()
        self.fitness = fitness
        self.image = None
        self.fin_image = None
        self.blank_image = np.zeros((height, width, 3), np.uint8)  # A blank image for rendering process.
        self.wanted_width = start_width
        self.wanted_height = start_height

    def generate_genome(self):

        polygons = int(self.shapes_ratio[0])
        circles = int(self.shapes_ratio[1])
        lines = int(self.shapes_ratio[2])

        for i in range(circles):
            self.genome.append(Circle(self.width, self.height))
        for i in range(polygons):
            self.genome.append(Polygon(self.vertices, self.width, self.height))
        for i in range(lines):
            self.genome.append(Line(self.width, self.height))

        if self.start_genome is None:
            self.start_genome = copy.deepcopy(self.genome)

    def make_image(self):
        output = self.blank_image.copy()
        overlay = self.blank_image.copy()

        for gene in self.genome:
            color = gene.color  # red color value
            alpha = gene.alpha  # alpha color value
            coordinates = gene.coordinates  # list of coordinates

            if gene.__class__ == Polygon:
                # draw the polygon on to the overlay image
                cv2.fillPoly(overlay, [coordinates], color)
            elif gene.__class__ == Circle:
                radius = gene.radius
                cv2.circle(overlay, coordinates, radius, color, -1)
            else:
                coordinates_to = gene.coordinates_to
                thickness = gene.thickness
                cv2.line(overlay, coordinates, coordinates_to, color, thickness)

            # apply the overlay(alpha)
            cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

            overlay = output.copy()
        self.image = output

    def make_fin_image(self):
        output = np.zeros((self.wanted_height, self.wanted_width, 3), np.uint8)
        overlay = np.zeros((self.wanted_height, self.wanted_width, 3), np.uint8)

        for gene in self.genome:
            color = gene.color  # red color value
            alpha = gene.alpha  # alpha color value
            # coordinates = gene.coordinates  # list of coordinates
            coordinates = []
            if gene.__class__ == Polygon:
                for coordinates_ in gene.coordinates:
                    x, y = coordinates_
                    x_1 = x / self.width
                    y_1 = y / self.height
                    coordinates += [
                        ([int(x_1 * self.wanted_width), int(y_1 * self.wanted_height)])]  # list of coordinates
                    # draw the polygon on to the overlay image
                cv2.fillPoly(overlay, np.array([coordinates]), color)
            elif gene.__class__ == Circle:
                x, y = gene.coordinates
                coordinates = (int((x / self.width) * self.wanted_width), int((y / self.height) * self.wanted_height))
                radius = gene.radius
                radius = int((radius / self.width) * self.wanted_width)

                cv2.circle(overlay, coordinates, radius, color, -1)
            else:
                x, y = gene.coordinates
                x_1, y_1 = gene.coordinates_to
                coordinates = (int((x / self.width) * self.wanted_width), int((y / self.height) * self.wanted_height))
                coordinates_to = (
                int((x_1 / self.width) * self.wanted_width), int((y_1 / self.height) * self.wanted_height))
                thickness = gene.thickness
                thickness = (thickness / self.width)
                thickness = int(thickness * self.wanted_width)
                if thickness <= 0:
                    thickness = 1
                cv2.line(overlay, coordinates, coordinates_to, color, thickness)

            # apply the overlay(alpha)
            cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

            overlay = output.copy()
        self.fin_image = output

    def __repr__(self) -> str:
        return super().__repr__()

    # -------------------------mutation------------------------------------------------------------------------

    # each gene in the genome has a mutation_probability chance of mutating
    def medium_probability_mutation(self):
        amount_genes_mutate = 0
        for gene in range(0, self.number_of_genes):
            if uniform(0, 1) < self.mutation_probability:
                self.medium_mutate(gene)
                amount_genes_mutate += 1
        # print("Amount of genes mutated: %s" % amount_genes_mutate)

    # mutation_probability(10%) of amount of shapes gets mutated. 30 x 0.1 = 3 gens mutated.
    def medium_chunk_mutation(self):
        for i in range(np.math.ceil(self.number_of_genes * self.mutation_probability)):
            rand_gene = randint(0, self.number_of_genes - 1)
            self.medium_mutate(rand_gene)
        # print("Amount of genes mutated: %s" % np.math.ceil(self.number_of_genes * self.mutation_probability))

    # medium mutate, changes the gene/attribute completely.
    def medium_mutate(self, rand_gene):
        if self.genome[rand_gene].__class__ == Polygon:
            attribute = randint(0, 2)
        else:
            attribute = randint(0, 3)

        if attribute == 0:
            self.medium_mutate_color(rand_gene)
        elif attribute == 1:
            self.medium_mutate_alpha(rand_gene)
        elif attribute == 2:
            self.medium_mutate_coord(rand_gene)
        elif attribute == 3:
            if self.genome[rand_gene].__class__ == Circle:
                self.medium_mutate_radius(rand_gene)
            else:
                self.medium_mutate_thickness(rand_gene)

    def medium_mutate_alpha(self, gene):
        new_alpha = generate_alpha()
        # self.genome[gene].mutate_record.append(["alpha", self.genome[gene].alpha, new_alpha])
        self.genome[gene].alpha = new_alpha

        # print("New alpha with value: %s on polygon: %s" % (new_alpha, gene))

    def medium_mutate_color(self, gene):
        new_color = generate_color()
        rand_rgb = randint(0, 2)
        temp = list(self.genome[gene].color)
        temp[rand_rgb] = new_color
        # self.genome[gene].mutate_record.append(["color", self.genome[gene].color, temp])
        self.genome[gene].color = tuple(temp)
        # print("New color at: %s with value: %s on gene: %s" % (rand_rgb, new_color, gene))

    def medium_mutate_radius(self, gene):
        new_radius = generate_radius(self.genome[gene])
        # self.genome[gene].mutate_record.append(["radius", self.genome[gene].radius, new_radius])
        self.genome[gene].radius = new_radius
        # print("New radius: %s on circle: %s" % (new_radius, gene))

    def medium_mutate_thickness(self, gene):
        new_thickness = generate_thickness()
        self.genome[gene].thickness = new_thickness

    # medium mutate one coordinate of the gene of the polygon type.
    # Pick out one of the vertices and changes it completely with a new random (x,y)
    def medium_mutate_coord(self, gene):
        if self.genome[gene].__class__ == Polygon:
            vertices_list = self.genome[gene].coordinates
            rand_vertices = randint(0, self.vertices - 1)
            vertices_list[rand_vertices] = ([randint(0, self.width), randint(0, self.height)])
            # self.genome[gene].mutate_record.append(["coordinate", self.genome[gene].coordinates, vertices_list])
            self.genome[gene].coordinates = vertices_list
            # print("New coordinate with value: %s on polygon: %s" % (vertices_list[rand_vertices], gene))
        elif self.genome[gene].__class__ == Circle:
            new_circle_coordinate = generate_point_coordinate(self.genome[gene])
            # self.genome[gene].mutate_record.append(["coordinate", self.genome[gene].coordinates, new_circle_coordinate])
            self.genome[gene].coordinates = new_circle_coordinate
            # print("New coordinate with value: %s on circle: %s" % (self.genome[gene].coordinates, gene))
        else:
            new_coordinate = generate_point_coordinate(self.genome[gene])
            from_or_to = randint(0, 1)
            if from_or_to == 0:
                self.genome[gene].coordinates = new_coordinate
            else:
                self.genome[gene].coordinates_to = new_coordinate

    def medium_mutate_gene_position(self, rand_gene):
        new_position = randint(0, self.number_of_genes - 1)
        temp = self.genome.pop(rand_gene)
        self.genome.insert(new_position, temp)

    # each gene in the genome has a mutation_probability chance of mutating
    def soft_probability_mutation(self):
        amount_genes_mutate = 0
        for gene in range(self.number_of_genes):
            if uniform(0, 1) < self.mutation_probability:
                self.soft_mutate(gene)
                amount_genes_mutate += 1
        # print("Amount of genes mutated: %s" % amount_genes_mutate)

    # mutation_probability of amount of shapes gets mutated. 30 x 0.1 = 3 gens mutated.
    def soft_chunk_mutation(self):
        for i in range(np.math.ceil(self.number_of_genes * self.mutation_probability)):
            rand_gene = randint(0, self.number_of_genes - 1)
            self.soft_mutate(rand_gene)
        # print("Amount of genes mutated: %s" % np.math.ceil(self.number_of_genes * self.mutation_probability))

    # soft mutate, changes the gene/attribute with +-soft_mutate_rate
    def soft_mutate(self, rand_gene):
        if self.genome[rand_gene].__class__ == Polygon:
            attribute = randint(0, 2)
        else:
            attribute = randint(0, 3)

        if attribute == 0:
            self.soft_mutate_color(rand_gene)
        elif attribute == 1:
            self.soft_mutate_alpha(rand_gene)
        elif attribute == 2:
            self.soft_mutate_coordinates(rand_gene)
        elif attribute == 3:
            if self.genome[rand_gene].__class__ == Circle:
                self.soft_mutate_radius(rand_gene)
            else:
                self.soft_mutate_thickness(rand_gene)

    # takes the a(lpha) variable and chooses +-soft_mutate_rate and returns the new value
    def soft_mutate_alpha(self, gene):
        alpha = self.genome[gene].alpha
        if randint(0, 1) == 0:  # choose + or - soft_mutate_rate
            alpha = alpha - (alpha * self.soft_mutate_rate)
        else:
            alpha = alpha * (1 + self.soft_mutate_rate)
        if alpha > 1:
            alpha = 1
        elif alpha < 0:
            alpha = 0
        # self.genome[gene].mutate_record.append(["alpha", self.genome[gene].alpha, alpha])
        self.genome[gene].alpha = round(alpha, 4)

    # takes the c(olor) variable and chooses +-soft_mutate_rate and returns the new value
    def soft_mutate_color(self, gene):
        rand_rgb = randint(0, 2)
        color = list(self.genome[gene].color)

        if randint(0, 1) == 0:  # choose + or - soft_mutate_rate
            new_color = color[rand_rgb] - (color[rand_rgb] * self.soft_mutate_rate)
        else:
            new_color = color[rand_rgb] * (1 + self.soft_mutate_rate)
        if new_color > 255:
            new_color = 255
        elif new_color < 0:
            new_color = 0

        color[rand_rgb] = new_color
        # self.genome[gene].mutate_record.append(["color", self.genome[gene].color, tuple(color)])
        self.genome[gene].color = tuple(color)
        # print("New color at: %s with value: %s on gene: %s" % (rand_rgb, new_color, gene))

    # takes the r(aduis) variable and chooses +-soft_mutate_rate and returns the new value
    def soft_mutate_radius(self, gene):
        radius = self.genome[gene].radius
        chance = randint(0, 1)  # choose + or - soft_mutate_rate
        if chance == 0:
            radius = radius - (radius * self.soft_mutate_rate)
        else:
            radius = radius * (1 + self.soft_mutate_rate)
        if radius > self.width / 2:
            radius = np.math.ceil(self.width / 2)
        elif radius < 0:
            radius = 0
        # self.genome[gene].mutate_record.append(["radius", self.genome[gene].radius, np.math.ceil(radius)])
        self.genome[gene].radius = np.math.ceil(radius)

    def soft_mutate_thickness(self, gene):
        thickness = self.genome[gene].thickness
        chance = randint(0, 1)  # choose + or - soft_mutate_rate
        if chance == 0:
            thickness = thickness - (thickness * self.soft_mutate_rate)
        else:
            thickness = thickness * (1 + self.soft_mutate_rate)
        if thickness > 10:
            thickness = 10
        elif thickness < 0:
            thickness = 0
        # self.genome[gene].mutate_record.append(["thickness", self.genome[gene].thickness, np.math.ceil(thickness)])
        self.genome[gene].thickness = np.math.ceil(thickness)

    # takes the coordinate and splits it up inn x and y, then chooses +-soft_mutate_rate and returns the new values
    def soft_mutate_coordinates(self, gene):
        if self.genome[gene].__class__ == Polygon:
            vertices_list = self.genome[gene].coordinates
            rand_vertices = randint(0, self.vertices - 1)
            vertices_list[rand_vertices] = self.soft_update_coordinate(vertices_list[rand_vertices])
            # self.genome[gene].mutate_record.append(["coordinate", self.genome[gene].coordinates, vertices_list])
            self.genome[gene].coordinates = vertices_list
            # print("New coordinate with value: %s on polygon: %s" % (vertices_list[rand_vertices], gene))
        elif self.genome[gene].__class__ == Circle:
            new_circle_coordinate = self.soft_update_coordinate(self.genome[gene].coordinates)
            # self.genome[gene].mutate_record.append(["coordinate", self.genome[gene].coordinates, new_circle_coordinate])
            self.genome[gene].coordinates = new_circle_coordinate
            # print("New coordinate with value: %s on circle: %s" % (self.genome[gene].coordinates, gene))
        else:
            from_or_to = randint(0, 1)
            if from_or_to == 0:
                new_coordinate = self.soft_update_coordinate(self.genome[gene].coordinates)
                self.genome[gene].coordinates = new_coordinate
            else:
                new_coordinate = self.soft_update_coordinate(self.genome[gene].coordinates_to)
                self.genome[gene].coordinates_to = new_coordinate

    def soft_update_coordinate(self, coordinate):
        x, y = coordinate
        if randint(0, 1) == 0:  # choose + or - soft_mutate_rate
            x = x - (x * self.soft_mutate_rate)
            y = y - (y * self.soft_mutate_rate)
        else:
            x = x * (1 + self.soft_mutate_rate)
            y = y * (1 + self.soft_mutate_rate)
        if x > self.width:
            x = self.width
        elif x < 0:
            x = 0
        if y > self.height:
            y = self.height
        elif y < 0:
            y = 0
        return int(x), int(y)
