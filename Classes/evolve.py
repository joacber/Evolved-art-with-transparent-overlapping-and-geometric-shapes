import os
import errno
import time
from Classes.fitness import *
from Classes.genome import *
import imageio


def mutate(self, genome):
    # mutate_func = randint(0, 0)  # change to (0, 2) to have a chance to only mutate one gene.
    if self.hybrid_medium_mutate_rate == 0:
        soft_mutate(self, genome)

        return
    elif self.hybrid_soft_mutate_rate == 0:
        medium_mutate(self, genome)

        return
    else:
        if self.hybrid_soft_mutate > 0:
            soft_mutate(self, genome)
            self.hybrid_soft_mutate -= 1
            return
        elif self.hybrid_medium_mutate > 1:
            medium_mutate(self, genome)
            self.hybrid_medium_mutate -= 1
            return
        else:
            medium_mutate(self, genome)
            self.hybrid_medium_mutate -= 1

            self.hybrid_soft_mutate = self.hybrid_soft_mutate_rate
            self.hybrid_medium_mutate = self.hybrid_medium_mutate_rate


def mutate_new_gene_structure(self, genome):
    # mutate child position
    for gene in range(0, self.number_of_genes):
        if uniform(0, 1) < self.mutation_probability:
            genome.medium_mutate_gene_position(gene)


def medium_mutate(self, genome):
    # print("Medium:")
    if self.mutation_type:  # only a % of the population mutate
        genome.medium_chunk_mutation()
    else:  # each have a % chance to mutate
        genome.medium_probability_mutation()


def soft_mutate(self, genome):
    # print("Soft:")

    if self.mutation_type:  # only a % of the population mutate
        genome.soft_chunk_mutation()
    else:  # each have a % chance to mutate
        genome.soft_probability_mutation()


# to make sure not cross with same parent, return new parent
def get_par(self, parent):
    for i in range(self.parent_genome.__len__()):
        if self.parent_genome[i] == parent:
            a = get_new_par(self, i)
            return a


# get new parent, but not same parent|
def get_new_par(self, parent_idx):
    exclude = [parent_idx]
    new_par = randint(0, self.amount_of_parents - 1)
    return get_new_par(self, parent_idx) if new_par in exclude else new_par


def crossover(self, parent):
    # to make sure not cross with same parent
    par_2 = get_par(self, parent)

    for gene in range(0, self.number_of_genes):
        color = self.parent_genome[par_2].genome[gene].color
        alpha = self.parent_genome[par_2].genome[gene].alpha
        self.child_genome[self.child_genome.__len__() - 1].genome[gene].color = color
        self.child_genome[self.child_genome.__len__() - 1].genome[gene].alpha = alpha


def get_fitness(self, i):
    return self.parent_genome[i].fitness


class Evolve:
    def __init__(self, image, image_name, output_folder, save_image_rate, max_generation, amount_of_parents,
                 children_per_parent, vertices, number_of_genes, shapes_ratio, mutation_probability, soft_mutate_rate,
                 hybrid_soft_mutate, hybrid_medium_mutate, mutation_type, gene_structure_rate, crossover_mutation,
                 export_gif_button):

        self.main_image = image
        self.image_name = image_name

        self.height, self.width, self.can = self.main_image.shape
        self.output_folder = output_folder
        self.save_image_rate = save_image_rate
        self.max_generation = max_generation
        self.vertices = vertices
        self.number_of_genes = number_of_genes
        self.shapes_ratio = shapes_ratio
        self.mutation_probability = mutation_probability
        self.soft_mutate_rate = soft_mutate_rate
        self.hybrid_soft_mutate = hybrid_soft_mutate
        self.hybrid_medium_mutate = hybrid_medium_mutate
        self.hybrid_soft_mutate_rate = hybrid_soft_mutate
        self.hybrid_medium_mutate_rate = hybrid_medium_mutate
        self.mutation_type = mutation_type

        self.gene_structure_rate = gene_structure_rate
        self.crossover_mutation = crossover_mutation
        self.gif_state = export_gif_button

        self.parent_genome = []
        self.child_genome = []
        self.amount_of_parents = amount_of_parents
        self.amount_of_children = children_per_parent
        self.fit = Fitness(self.main_image, self.width, self.height)
        self.generation = 0

        self.log_initial_state = "../%s/%s_initial_state.txt" % (self.output_folder, self.image_name)
        self.log_fitness = "../%s/%s_fitness.csv" % (self.output_folder, self.image_name)
        self.t0 = time.process_time()

        self.images = []

    def next_generation(self):

        self.create_children()
        for genome in self.child_genome:
            for i in range(len(self.parent_genome)):
                if self.parent_genome[i].fitness > genome.fitness:
                    self.parent_genome.insert(i, genome)
                    self.parent_genome.pop()
                    if i == 0 and self.gif_state:  # and self.generation % 5 == 0:
                        b, g, r = cv2.split(self.parent_genome[0].image)
                        opencv_image = cv2.merge((r, g, b))
                        self.images.append(opencv_image)
                    # print("New parent with fitness: %s" % genome.fitness)
                    break
        if self.generation % self.save_image_rate == 0 and self.generation != 0:
            self.save_image()
        # Log generation
        with open(self.log_fitness, "a") as f:
            f.write("%s, %s \n" % (self.generation, self.parent_genome[0].fitness))
        self.generation += 1

    def save_image(self):
        # saving each image
        i = 1
        for genome in self.parent_genome:
            cv2.imwrite("../%s/generation%s_parent%s_fitness%s.jpg" % (
                self.output_folder, self.generation, i, genome.fitness),
                        genome.image)
            i += 1

    def make_fin_image(self):
        self.parent_genome[0].make_fin_image()
        cv2.imwrite("../%s/generation%s_parent%s_fitness%s_Fin.jpg" % (
            self.output_folder, self.generation, 0, self.parent_genome[0].fitness),
                    self.parent_genome[0].fin_image)
    def make_gif(self):
        if self.gif_state:
            imageio.mimsave("../%s/GIF.gif" % self.output_folder, self.images, fps=120)

    def logging(self):
        #  Makes the directory output if it does not exist.
        if not os.path.exists(os.path.dirname(self.log_fitness)):
            try:
                os.makedirs(os.path.dirname(self.log_fitness))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        self.save_image()
        with open(self.log_fitness, "w") as f:
            f.write("%s,%s\n" % (self.width, self.height))
        with open(self.log_initial_state, "w") as f:
            f.write("Image name: %s\n"
                    "Image size: %s,%s\n"
                    "Population size: %s, parents: %s with %s children each \n"
                    "Number of genes: %s\n"
                    "Number of circles: %s\n"
                    "Number of polygons: %s\n"
                    "Number of lines: %s\n"
                    "Number of vertices: %s\n\n" % (self.image_name,
                                                    self.width, self.height,
                                                    ((
                                                             self.amount_of_parents * self.amount_of_children) + self.amount_of_parents),
                                                    self.amount_of_parents, self.amount_of_children,
                                                    self.number_of_genes,
                                                    int(self.shapes_ratio[1]),
                                                    int(self.shapes_ratio[0]),
                                                    int(self.shapes_ratio[2]),
                                                    self.vertices))

    def end_log(self):
        t1 = time.process_time()
        # print(t1 - self.t0)

        i = 1
        for genome in self.parent_genome:
            cv2.imwrite("../%s/generation%s_parent%s_fitness%s.jpg" %
                        (self.output_folder, self.generation, i, genome.fitness), genome.image)

            i += 1

        with open(self.log_initial_state, "a") as f:
            f.write("Mutation probability: %s\n"
                    "Soft mutate rate: %s\n"
                    "Hybrid mutate ratio: soft/medium: %s/%s\n"
                    "Stagnate limit: %s\n"
                    "Mutation type, True = chunk, false = probability: %s\n"
                    "Crossover_mutation: %s\n"
                    "Gene structure rate: %s\n\n" % (self.mutation_probability,
                                                     self.soft_mutate_rate,
                                                     self.hybrid_soft_mutate_rate,
                                                     self.hybrid_medium_mutate_rate,
                                                     0,
                                                     self.mutation_type,
                                                     self.crossover_mutation,
                                                     self.gene_structure_rate))
            for i in range(self.parent_genome.__len__()):
                f.write("Fitness for parent %s: %s\n" % (i, self.parent_genome[i].fitness))
            f.write("Time: %s" % (t1 - self.t0))

    def create_parents(self):
        # print("Amount of shapes being mutated according to mutation_probability: %s" % np.math.ceil(
        #    number_of_genes * mutation_probability))
        for i in range(self.amount_of_parents):
            self.parent_genome.append(
                Genome(self.vertices, self.number_of_genes, self.width, self.height, self.shapes_ratio,
                       self.mutation_probability,
                       self.soft_mutate_rate, 0))

            # make the parent image
            self.parent_genome[i].make_image()

            self.parent_genome[i].fitness = self.fit.get_fitness(self.parent_genome[i].image)

            # print("fitnes: %s" % self.parent_genome[i].fitness)
        self.parent_genome.sort(key=lambda x: x.fitness)

    def create_children(self):
        self.child_genome = []
        # For every parent, create amount of children.
        for parent in self.parent_genome:
            for child in range(self.amount_of_children):
                self.child_genome.append(copy.deepcopy(parent))
                if self.crossover_mutation:
                    crossover(self, parent)
                if self.generation < (self.max_generation * self.gene_structure_rate) \
                        and child == self.amount_of_children - 1:
                    mutate_new_gene_structure(self, self.child_genome[self.child_genome.__len__() - 1])

                mutate(self, self.child_genome[self.child_genome.__len__() - 1])
                # make image child
                self.child_genome[self.child_genome.__len__() - 1].make_image()

                self.child_genome[self.child_genome.__len__() - 1].fitness = self.fit.get_fitness(
                    self.child_genome[self.child_genome.__len__() - 1].image)
        self.child_genome.sort(key=lambda x: x.fitness)
