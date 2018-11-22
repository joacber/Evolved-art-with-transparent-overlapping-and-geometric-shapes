import numpy as np


# TODO fitness function
class Fitness:

    def __init__(self, main_image, width, height):
        self.main_image = main_image
        self.height = height
        self.width = width

    def get_fitness(self, img2):
        """
        :param img2:
        :return: Sum of differences in Red, Green and Blue channels of two images (phenotypes)
        """
        #   Basic difference
        a = self.main_image - img2
        #   An array of either 1 or 255
        #   Depends on which image is the "lesser"
        b = np.uint8(self.main_image < img2) * 254 + 1
        #   Product of difference and either 1 or 255
        #   Multiplying 8 bit numbers with 255 is equivalent
        #   to multiplying by -1 and letting it overflow.
        diff = a * b
        #   Flattens the multidimensional array for easy summary
        #   Ex. [1, 2, 3], [4, 5, 6] = [1 2 3 4 5 6]
        diff = np.ravel(diff)
        #   Numpy sums the differences
        #   Max theoretical difference is 3 * 255 per pixel
        diff = np.sum(diff)
        return diff
