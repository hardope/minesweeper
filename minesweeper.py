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
        return self.cells if len(self.cells) == self.count else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        
        if cell in self.cells:

            self.cells.remove(cell)
            self.count -= 1
            return True

        return False

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        
        if cell in self.cells:

            self.cells.remove(cell)
            return True

        return False


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
        
        self.moves_made.add(cell)
        self.safes.add(cell)
        neighbors = []
        cells = []
        i = cell[0]
        j = cell[1]

        if (i > 0):
            neighbors.append((i-1, j))
            if (j > 0):
                neighbors.append((i-1, j-1))
            if (j < self.width - 1):
                neighbors.append((i-1, j+1))

        if (i < self.height - 1):
            neighbors.append((i+1, j))
            if (j > 0):
                neighbors.append((i+1, j-1))     
            if (j < self.width - 1):
                neighbors.append((i+1, j+1))   

        if (j < self.width-1):
            neighbors.append((i, j+1))

        if (j > 0):
            neighbors.append((i, j-1))                    

        for neighbor in neighbors:
            if neighbor not in self.safes:
                cells.append(neighbor)

        newSentence = Sentence(cells, count)

        # Update newSentence considering known mines in the vicinity
        for sentence in self.knowledge:

            for known_mine in self.mines:
                if known_mine in newSentence.cells:
                    newSentence.mark_mine(known_mine)

        # Add the updated newSentence to knowledge base if it's not already present
        if newSentence not in self.knowledge:
            self.knowledge.append(newSentence)

        # Infer additional mines and safes based on current knowledge
        self.mark_cells()

        # Infer new sentences from existing knowledge base
        new_sentences = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2:
                    # If sentence1 cells are a subset of sentence2 cells, calculate the difference
                    if sentence1.cells.issubset(sentence2.cells):
                        modified_set = sentence2.cells - sentence1.cells
                        modified_count = sentence2.count - sentence1.count

                        # Ensure the modified set has cells and the count is non-negative
                        if len(modified_set) > 0 and modified_count >= 0:
                            new_sentence = Sentence(modified_set, modified_count)

                            # Check if the new sentence is not already in knowledge base
                            if new_sentence not in self.knowledge:
                                new_sentences.append(new_sentence)

        # Add newly inferred sentences to knowledge base
        for sentence in new_sentences:
            self.knowledge.append(sentence)

        # Infer additional mines and safes based on current knowledge
        self.mark_cells()                  

    def mark_cells(self):
        safes = []
        mines = []

        for sentence in self.knowledge:
            for safe in sentence.known_safes():
                if safe not in safes and safe not in self.safes:
                    safes.append(safe)
            for mine in sentence.known_mines():
                if mine not in mines and mine not in self.mines:
                    mines.append(mine)   

        for tempSafe in safes:
            self.mark_safe(tempSafe)
        for tempMine in mines:
            self.mark_mine(tempMine)  

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        for safe in self.safes:

            if safe not in self.moves_made:
                return safe

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        for i in range(self.height):
            for j in range(self.width):

                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    return (i, j)

        return None
