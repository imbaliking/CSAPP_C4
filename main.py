
from motherBoard import mother_board

if __name__ == "__main__":
    board = mother_board()
    start_address = ""
    program_data = ""
    board.load_data(start_address,program_data)
    board.run()