#Red Brick Industries Chess Project
#By Jack Barnet



import tkinter as tk
import chess
import chess.engine
from PIL import Image, ImageTk
import os


class ChessGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Red Brick Chess Game")
        self.geometry("600x600")
        self.game_over = False  # Add game_over attribute

        # Ensure the Stockfish engine path is correct
        self.engine_path = "stockfish.exe"  # Adjust the path as necessary
        if not os.path.isfile(self.engine_path):
            print(f"Stockfish engine not found at path: {self.engine_path}")
            return

        self.board = chess.Board()

        # Initialize chess engine
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            self.engine.configure({"Skill Level": 10})  # Adjust this value for different difficulties between 1-20
        except Exception as e:
            print(f"Error initializing the engine: {e}")
            return

        self.canvas = tk.Canvas(self, width=600, height=600)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.square_clicked)  # Bind left mouse clicks to square_clicked method

        self.selected_square = None
        self.piece_images = self.load_images()  # Load images
        self.draw_board()
        self.draw_pieces()

        self.show_piece_key()  # Display the chess piece key
        print("Board setup completed.")

    def load_images(self):
        print("Loading images...")
        piece_images = {}
        # Define file paths for each piece
        piece_paths = {
            'P': "images/white_pawn.png",
            'R': "images/white_rook.png",
            'N': "images/white_knight.png",
            'B': "images/white_bishop.png",
            'Q': "images/white_queen.png",
            'K': "images/white_king.png",
            'p': "images/black_pawn.png",
            'r': "images/black_rook.png",
            'n': "images/black_knight.png",
            'b': "images/black_bishop.png",
            'q': "images/black_queen.png",
            'k': "images/black_king.png"
        }

        for piece_symbol, path in piece_paths.items():
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Image file not found: {path}")
            image = Image.open(path)  # Open the image file
            image = image.resize((65, 65), Image.LANCZOS)  # Resize the image if necessary
            piece_images[piece_symbol] = ImageTk.PhotoImage(image)  # Create a PhotoImage
        print("Images loaded.")
        return piece_images

    def draw_board(self):
        self.canvas.delete("square")
        colors = ["white", "grey"]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(col * 75, row * 75, (col + 1) * 75, (row + 1) * 75, fill=color,
                                              tags="square")
        self.canvas.tag_raise("piece")
        self.canvas.tag_lower("square")

    def draw_pieces(self):
        self.canvas.delete("piece")
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                symbol = piece.symbol() if piece.color == chess.WHITE else piece.symbol().lower()
                image = self.piece_images[symbol]
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)  # row is reversed because tkinter starts from the top left corner
                x0 = (col * 75) + 5
                y0 = (row * 75) + 5
                self.canvas.create_image(x0, y0, image=image, tags=("piece",), anchor="nw")

    def square_clicked(self, event):
        col = event.x // 75
        row = 7 - (event.y // 75)
        square = chess.square(col, row)
        piece = self.board.piece_at(square)

        if self.selected_square:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.draw_pieces()
                print(f"Player moved: {move}")
                self.check_game_over()  # Check if the game is over after player's move
                if not self.game_over:  # Ensure game is not already over
                    print(f"AI's turn to move.")
                    self.after(100, self.engine_move)
            self.selected_square = None
        elif piece and (piece.color == self.board.turn):
            self.selected_square = square

    def engine_move(self):
        result = self.engine.play(self.board, chess.engine.Limit(time=0.1))
        self.board.push(result.move)
        self.draw_pieces()
        print(f"AI moved: {result.move}")
        self.check_game_over()  # Check if the game is over after AI's move
        if not self.game_over:  # Ensure game is not already over
            print(f"Player's turn to move.")

    def check_game_over(self):
        if self.board.is_checkmate():
            result = "Checkmate"
            self.game_over = True  # Set game_over flag to True
        elif self.board.is_stalemate():
            result = "Stalemate"
            self.game_over = True  # Set game_over flag to True
        elif self.board.is_insufficient_material():
            result = "Draw due to insufficient material"
            self.game_over = True  # Set game_over flag to True
        elif self.board.can_claim_draw():
            result = "Draw claimable"
            self.game_over = True  # Set game_over flag to True

    def show_piece_key(self):
        # Create a new Toplevel window
        key_window = tk.Toplevel(self)
        key_window.title("Chess Pieces Key")

        # Define labels and paths for each piece
        pieces_info = {
            'P': ("White Pawn Steven", "images/white_pawn.png"),
            'R': ("White Rook Thomas", "images/white_rook.png"),
            'N': ("White Knight Curtis", "images/white_knight.png"),
            'B': ("White Bishop Codie", "images/white_bishop.png"),
            'Q': ("White Queen Nathan", "images/white_queen.png"),
            'K': ("White King Jack", "images/white_king.png"),
            'p': ("Black Pawn Steven", "images/black_pawn.png"),
            'r': ("Black Rook Thomas", "images/black_rook.png"),
            'n': ("Black Knight Curtis", "images/black_knight.png"),
            'b': ("Black Bishop Codie", "images/black_bishop.png"),
            'q': ("Black Queen Nathan", "images/black_queen.png"),
            'k': ("Black King Jack", "images/black_king.png")
        }

        for symbol, (name, path) in pieces_info.items():
            frame = tk.Frame(key_window)
            frame.pack(side=tk.TOP, expand=True, fill=tk.X)
            try:
                img = Image.open(path)
                img.thumbnail((50, 50), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=tk_img)
                img_label.image = tk_img  # Keep a reference
                img_label.pack(side=tk.LEFT)
            except IOError:
                print(f"Unable to load image for {name}.")
                continue

            label = tk.Label(frame, text=name)
            label.pack(side=tk.LEFT)

    def on_close(self):
        if hasattr(self, 'engine') and self.engine:
            self.engine.quit()
        self.destroy()

if __name__ == "__main__":
    app = ChessGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()