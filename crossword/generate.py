import sys

from crossword import Variable, Crossword


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
        for var in self.domains:
            removal = set()

            # Taking note of words not consistent with length (unary constraint)
            for w in self.domains[var]:
                if len(w) != var.length:
                    removal.add(w)

            # Remove aforementioned words
            for w in removal:
                self.domains[var].remove(w)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False

        over_l = self.crossword.overlaps.get((x, y))
        if over_l is None:
            return False

        i, j = over_l
        removal = set()

        for word_x in self.domains[x]:
            # Acceptance for word_x if there is existence of word_y in domain[y]
            # with matching conistency at the position where there is an overlap
            if not any(word_x[i] == word_y[j] for word_y in self.domains[y]):
                removal.add(word_x)

        if removal:
            for word_x in removal:
                self.domains[x].remove(word_x)
            revision = True

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Queue initialization
        if arcs is None:
            q_ = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    q_.append((x, y))

        else:
            q_ = list(arcs)

        # Queue processing
        while q_:
            x, y = q_.pop(0)

            if self.revise(x, y):
                # If domain is empty this isnt solvable
                if len(self.domains[x]) == 0:
                    return False

                # Add all arcs (z, x) back except the one we came from
                for z in self.crossword.neighbors(x):
                    if z != y:
                        q_.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # All values have correct length
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # All values are different
        w = list(assignment.values())
        if len(w) != len(set(w)):
            return False

        # There are no conflicts in terms of neighbor vars
        for x in assignment:
            for y in assignment:
                if x == y:
                    continue

                over_l = self.crossword.overlaps.get((x, y))
                if over_l is None:
                    continue

                i, j = over_l
                if assignment[x][i] != assignment[y][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Looking only at neighboring variables not assigned yet
        n_unassigned = [
            neigh for neigh in self.crossword.neighbors(var)
            if neigh not in assignment
        ]

        def ruled_out_count(word):
            """
            Return the number of neighbor-domain values that would be
            ruled out if `var` were assigned this word.
            """
            count = 0

            for neighbor in n_unassigned:
                over_l = self.crossword.overlaps.get((var, neighbor))
                if over_l is None:
                    continue

                i, j = over_l
                for neigh_word in self.domains[neighbor]:
                    if word[i] != neigh_word[j]:
                        count += 1

            return count

        # starting at least constraining, sort domain values by how few these rule out
        return sorted(self.domains[var], key=ruled_out_count)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [va for va in self.crossword.variables if va not in assignment]

        # MRV or minimum remaing values
        min_domain_size = min(len(self.domains[va]) for va in unassigned)
        var_candidates = [va for va in unassigned if len(self.domains[va]) == min_domain_size]

        # Var with most neighbors i.e degree heuristic
        if len(var_candidates) > 1:
            max_d = max(len(self.crossword.neighbors(va)) for va in var_candidates)
            var_candidates = [va for va in var_candidates if len(
                self.crossword.neighbors(va)) == max_d]

        # Last spec regarding breaking ties that remain in an arbitrary manner
        return var_candidates[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # The work is finished if all variables have been assigned
        if self.assignment_complete(assignment):
            return assignment

        # Using heuristics pick the next variable to look at
        var = self.select_unassigned_variable(assignment)

        # Try values in least-constraining order, minimizing future conflicts
        for val in self.order_domain_values(var, assignment):

            # Provisional assignment
            newer_a = assignment.copy()
            newer_a[var] = val

            # If consistent i.e no violation of constraints continue on this line
            if self.consistent(newer_a):
                answer = self.backtrack(newer_a)
                if answer is not None:
                    return answer

        # Backtrack to previous decision as no valid assignment found
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
