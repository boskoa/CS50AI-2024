import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop over all the words and remove the ones that don't fit
        for key, value in self.domains.items():
            for word in value.copy():
                if len(word) != key.length:
                    value.remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        words_x = self.domains[x]
        words_y = self.domains[y]
        # Set the revision condition
        revised = False
        # Get overlap
        intersection = self.crossword.overlaps[(x, y)]
        # Check if words overlap
        if not intersection:
            return revised
        # Loop over x words
        for word_x in words_x.copy():
            # Loop over y words and check if there is a corresponding value
            pair = False
            for word_y in words_y:
                if word_x[intersection[0]] == word_y[intersection[1]]:
                    pair = True
                    break
            # If not, remove x word and set revised to True
            if not pair:
                words_x.remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Get arcs from existing overlaps
        if arcs is None:
            arcs = [i for (i, j) in self.crossword.overlaps.items() if j]
        # Revise arcs
        while len(arcs):
            arc = arcs.pop(0)
            # If domain is changed
            if self.revise(arc[0], arc[1]):
                # If empty domain / not solvable
                if not len(self.domains[arc[0]]):
                    return False
                # Add new arcs
                for neighbor in self.crossword.neighbors(arc[0]) - {arc[1]}:
                    arcs.append((arc[0], neighbor))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for key, value in assignment.items():
            # Check if the value is not repeating
            if list(assignment.values()).count(value) > 1:
                return False
            # Check if value length correct
            if key.length != len(value):
                return False
            # Check if overlaps are the same
            neighbors = self.crossword.neighbors(key)
            if neighbors:
                for neighbor in neighbors:
                    cross = self.crossword.overlaps[(key, neighbor)]
                    if cross and key in assignment and neighbor in assignment:
                        if value[cross[0]] != assignment[neighbor][cross[1]]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        count = dict.fromkeys(self.domains[var], 0)
        # Get the number of excluded choices per var word
        neighbors = self.crossword.neighbors(var)
        for word in self.domains[var]:
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                for word_2 in self.domains[neighbor]:
                    cross = self.crossword.overlaps[(var, neighbor)]
                    if word[cross[0]] != word_2[cross[1]]:
                        count[word] += 1
        # Sort by excluded words, make a list and return
        count = sorted(count, key=count.get)

        return count

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        ordered = sorted(unassigned, key=lambda x: (
            len(self.domains[x]),
            -len(self.crossword.neighbors(x))
        ))

        return ordered[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Check if assignment is satisfactory
        if self.assignment_complete(assignment):
            return assignment
        # Get unassigneg variable
        unassigned_variable = self.select_unassigned_variable(assignment)
        # Assign a value to the variable
        for value in self.order_domain_values(unassigned_variable, assignment):
            assignment[unassigned_variable] = value
            # Run the backtrack again
            result = self.backtrack(assignment)
            # Return result if OK, otherwise - remove it
            if self.consistent(assignment):
                return result
            del assignment[unassigned_variable]

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
