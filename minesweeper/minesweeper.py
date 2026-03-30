import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) > 0 and self.count == len(self.cells):
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if len(self.cells) > 0 and self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) Keep record of move
        self.moves_made.add(cell)

        # 2) Mark cell safe
        self.mark_safe(cell)

        # 3) Make new sentence from unknown neighbors of cell
        neighbors = set()
        i, j = cell
        newer_count = count

        # Check surrounding cells
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj

                # Stay within limits of board
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    n_cell = (ni, nj)

                    # If known mine minus it from count
                    if n_cell in self.mines:
                        newer_count -= 1

                    # If not sure whether mine or safe; it is unknown
                    elif n_cell not in self.safes:
                        neighbors.add(n_cell)

        # If new sentence has unknown cells add it
        if len(neighbors) > 0:
            newer_sentence = Sentence(neighbors, newer_count)
            if newer_sentence not in self.knowledge:
                self.knowledge.append(newer_sentence)

        # 4) & 5) Until there is no knowledge to be gained apply inferences
        new_changes = True
        while new_changes:
            new_changes = False

            # Take out empty sentences
            self.knowledge = [x for x in self.knowledge if len(x.cells) > 0]

            # Keep track of new safes and new mines
            updated_safes = set()
            updated_mines = set()

            for sentence in self.knowledge:
                updated_safes |= sentence.known_safes()
                updated_mines |= sentence.known_mines()

            # Apply new safe then mine conclusions
            for c_ell in updated_safes:
                if c_ell not in self.safes:
                    self.mark_safe(c_ell)
                    new_changes = True

            for c_ell in updated_mines:
                if c_ell not in self.mines:
                    self.mark_mine(c_ell)
                    new_changes = True

            self.knowledge = [s_ent for s_ent in self.knowledge if len(s_ent.cells) > 0]

            newer_sentences = []

            # iterate over sentences
            for x, y in itertools.combinations(self.knowledge, 2):

                # like e.g in project background cells and counts being subsets of each other
                if x.cells.issubset(y.cells):
                    other_cells = y.cells - x.cells
                    other_count = y.count - x.count

                    if len(other_cells) > 0:
                        inferred = Sentence(other_cells, other_count)
                        if inferred not in self.knowledge and inferred not in newer_sentences:
                            newer_sentences.append(inferred)
                elif y.cells.issubset(x.cells):
                    other_cells = x.cells - y.cells
                    other_count = x.count - y.count

                    if len(other_cells) > 0:
                        inferred = Sentence(other_cells, other_count)
                        if inferred not in self.knowledge and inferred not in newer_sentences:
                            newer_sentences.append(inferred)

            # Inferred sentences are added and another loop is executed if anything has changed
            if newer_sentences:
                self.knowledge.extend(newer_sentences)
                new_changes = True

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        av_choices = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    av_choices.append(cell)

        if not av_choices:
            return None

        return random.choice(av_choices)
