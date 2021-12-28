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
        '''
        modified to check for empty Sentences
        '''
        if isinstance(other, int):
            return len(self.cells) == other
        
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"
    
    def __sub__(self, other):
        '''
        Calculates difference between two sentences:
            Example -> ({A,B,C} = 2) - ({B,C} = 1) = ({A} = 1) 
        '''
        
        cells = self.cells - other.cells
        count = self.count - other.count
        return Sentence(cells, count)

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        
        Implementation: If we consider the set to be {A,B,C} is only known if
        the mine count is 3.
        So we return the full set of cells if its length is equal to the count
        or we return an empty set.
        
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        
        Implementation: If we consider the set to be {A,B,C}, it's only true if
        the mine count is 0. {A,B,C} = 0
        else we return an empty set
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        
        Implementation: If a cell has been markes as a mine, we only need to
        remove it from the set and decrease the mine count by 1 so that the 
        egality is equivelent. For example if {A, B, C} = 2 and we know that
        C is a mine, then we have the egality, {A, B} = 1
        
        Implementation error, make sure that the cell is in the set first
        """
        if cell not in self.cells:
            return None
        self.cells.remove(cell)
        self.count = self.count -1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        
        Implementation: If a cell has been markes as a safe, we only need to
        remove it from the set so that the egality is equivelent. 
        For example if {A, B, C} = 2 and we know that
        C is safe, then we have the egality, {A, B} = 2
        
        Implementation error: make sure that the cell is in the set first
        """
        if cell not in self.cells:
            return None
        
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
        
        #1 - mark the cell as a move that has been made
        
        self.moves_made.add(cell)
        
        #2 - mark the cell as safe
        
        self.mark_safe(cell)
        
        #3 add a new sentence to AI knowledge base
        '''
        create a new sentence by creating an empty set, add in all the
        surrounding cells of the chose cell and make it equal the count
        {surroundin cells} = count
        
        Function adapted from nearby_mines method in the Minesweeper class
        
        '''
        surrounding_cells = set()
        
        x,y = cell
        
        for i in range(x-1,x+2):
            for j in range(y-1,y+2):
                new_cell = (i,j)
                if new_cell != cell:
                    if 0 <= i and i < self.height and 0 <= j and j < self.width:
                        surrounding_cells.add(new_cell)
        
        new_sentence = Sentence(surrounding_cells, count)
        
        '''
        now we have our sentence. We need to make sure that it there isn't a
        cell inside that is known to be safe or know to be a mine and adjust it
        accordingly to get the most efficient sentence
        '''
        
        copy_sentence_cells = new_sentence.cells.copy()
        
        for c in copy_sentence_cells:
            if c in self.safes:
                new_sentence.mark_safe(c)
            if c in self.mines:
                new_sentence.mark_mine(c)
        
        self.knowledge.append(new_sentence)
        
        #4  mark any additional cells as safe or as mines if it can be 
        # concluded based on the AI's knowledge base
        
        '''
        We need to make sure that the KB does not add any new information than
        the data in the safe and mines sets. We need to keep searching the KB 
        until no additional data can be interpretated from it.
        '''
        consistent = False
        
        while consistent == False:
            
            consistent = True
            
            new_safe = set()
            new_mine = set()
            
            '''
            we get the safe and mines from the KB. When something is marked
            as safe or a mine, it is automatically removed from the KB so all
            the data we gather from the KB isn't in the mines of safes set
            '''
            for sentence in self.knowledge:
                s = sentence.known_safes()
                m = sentence.known_mines()
                new_safe = new_safe.union(s)
                new_mine = new_mine.union(m)
            
            '''
            if there are cells in the new_safe or the new_mine sets then there
            is data we can get from the KB that isn't in the safes and mines
            sets in this class. Meaning the data isn't consistent
            '''
            
            if len(new_safe) != 0 or len(new_mine) != 0:
                consistent = False
            
            #mark the new safes and the new mines
            
            if len(new_safe) != 0:
                for c in new_safe:
                    self.mark_safe(c)
                
            if len(new_mine) != 0:
                for c in new_mine:
                    self.mark_mine(c)
            
            #5- add any new sentences to the AI's knowledge base
            # if they can be inferred from existing knowledge
            
            '''
            to clean up the KB, we need to remove all empty Sentences {} = 0
            '''
            
            new_knowledge = []
            for sentence in self.knowledge:
                if sentence != 0:
                    new_knowledge.append(sentence)
            self.knowledge = new_knowledge[:]
            
            '''
            The idea is to add new sentences. From the information sheet if 
            the cells of a sentence is a subset of another sentence, their
            difference is also a valid sentence.
            '''
            for sentence in self.knowledge:
                for sentence1 in self.knowledge:
                    '''
                    make sure sentences are not the same. The substraction
                    will be always {} = 0 which is meaningless
                    '''
                    if sentence == sentence1:
                        continue
                    
                    if not sentence.cells.issubset(sentence1.cells):
                        continue
                    
                    new_sentence = sentence1 - sentence
                    
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
                        consistent = False
                    
            
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        
        We need to check if a safe move exists. We just need to substract
        the safe set and the moves.
        """
        safe_moves = self.safes - self.moves_made
        
        if len(safe_moves) != 0:
            return safe_moves.pop()
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        
        We only need to have an set with all the invalid cells (mines and chosen)
        and another set with all the possible combinations. Substract the two and
        just choose one.
        """
        invalid_cells = self.mines.union(self.moves_made)
        
        possible_cells = set()
        
        for i in range(self.height):
            for j in range(self.width):
                cell = (i,j)
                possible_cells.add(cell)
        
        possible_cells = possible_cells - invalid_cells
        if len(possible_cells) == 0:
            return None
        move = possible_cells.pop()
        return move
        

