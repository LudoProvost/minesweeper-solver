import random
import pyautogui
import time
import keyboard
pyautogui.PAUSE = 0


# time.sleep(2)
# print(len(list(pyautogui.locateAllOnScreen('images/tile_flag.png', region=(529, 127, 500, 330)))))
# print(pyautogui.position()) top-left corner of board: ~(x=529, y=127)
# time.sleep(4)
# print(pyautogui.position()) bottom-right corner of board: ~(x=1028, y=446)
# im2 = pyautogui.screenshot('ss.png', region=(529, 127, 500, 330))
# exit(-4)


def random_click():
    unknown_locations = read_board(1)
    random_unknown = unknown_locations[random.randint(0, len(unknown_locations))]
    pyautogui.click(random_unknown.left, random_unknown.top)


# placing numbered tiles
def read_board(check_for_unknowns_only):

    # getting cursor out of the way
    # pyautogui.moveTo(529, 127)

    if not check_for_unknowns_only:

        # calculating smallest region
        minesweeper_board = Resolution(530, 127, 500, 330)
        left = minesweeper_board.get_left()
        top = minesweeper_board.get_top()
        width = minesweeper_board.get_width()
        height = minesweeper_board.get_height()

        for tile_num in range(9):  # top left corner (center): 548 192                   REGIONS ALL USE: 530, 127, 500, 330
            for pos_tile_num in pyautogui.locateAllOnScreen(tile_states.get('tile').format(tile_num), region=(left, top, abs(width), abs(height))):
                location = pyautogui.center(pos_tile_num)
                board[round((location.y - 192) / 16)][round((location.x - 548) / 16)] = tile_num

        # looking for flags
        for pos_tile_num in pyautogui.locateAllOnScreen('images/tile_flag.png', region=(left, top, abs(width), abs(height))):
            location = pyautogui.center(pos_tile_num)
            board[round((location.y - 192) / 16)][round((location.x - 548) / 16)] = -1

    elif check_for_unknowns_only:
        unknown_loc = list(pyautogui.locateAllOnScreen('images/tile.png', region=(530, 127, 500, 330)))
        return unknown_loc


def read_full_board():
    for tile_num in range(9):  # top left corner (center): 548 192
        for pos_tile_num in pyautogui.locateAllOnScreen(tile_states.get('tile').format(tile_num),
                                                        region=(530, 127, 500, 330)):
            location = pyautogui.center(pos_tile_num)
            board[round((location.y - 192) / 16)][round((location.x - 548) / 16)] = tile_num

    # looking for flags
    for pos_tile_num in pyautogui.locateAllOnScreen('images/tile_flag.png', region=(530, 127, 500, 330)):
        location = pyautogui.center(pos_tile_num)
        board[round((location.y - 192) / 16)][round((location.x - 548) / 16)] = -1


def print_board(board_to_print):
    # printing board
    for i in range(height):
        print(board_to_print[i])
    print("\n\n\n\n")


def check_around(tile_row, tile_column):
    for row in range(tile_row - 1, tile_row + 2):
        for column in range(tile_column - 1, tile_column + 2):
            if row == tile_row and column == tile_column:
                continue
            print(board[row][column])


def num_unknown(tile_row, tile_column, bomb_or_safe, stuck):
    """ returns number of unknown tiles around numbered tile
        bomb_or_safe: 1 to count bombs, 0 to count safe tiles
    """
    unknowns = 0

    min_row = tile_row - 1
    min_row = 0 if min_row < 0 else min_row

    max_row = tile_row + 1
    max_row = height - 1 if max_row >= height else max_row

    min_column = tile_column - 1
    min_column = 0 if min_column < 0 else min_column

    max_column = tile_column + 1
    max_column = width - 1 if max_column >= width else max_column

    for row in range(min_row, max_row + 1):
        for column in range(min_column, max_column + 1):
            if row == tile_row and column == tile_column:
                continue

            if stuck and board[row][column] == 9:
                unknowns += 1

            # counts bombs
            if (bomb_or_safe and not stuck) and board[row][column] == -1:
                unknowns += 1

            # counts safe tiles
            if (not bomb_or_safe and not stuck) and (board[row][column] == 9 or board[row][column] == -1):
                unknowns += 1

    return unknowns


def clear_tiles(tile_row, tile_column, bomb_or_safe):
    """ makes sure the surrounding tiles are correctly tagged
        bomb_or_safe: 1 if bomb, 0 if safe
    """

    board_changed = False

    min_row = tile_row - 1
    min_row = 0 if min_row < 0 else min_row

    max_row = tile_row + 1
    max_row = height - 1 if max_row >= height else max_row

    min_column = tile_column - 1
    min_column = 0 if min_column < 0 else min_column

    max_column = tile_column + 1
    max_column = width - 1 if max_column >= width else max_column

    for row in range(min_row, max_row + 1):
        for column in range(min_column, max_column + 1):
            if row == tile_row and column == tile_column:
                continue

            # tags all bombs
            if bomb_or_safe and board[row][column] == 9:
                pyautogui.rightClick((column * 16) + 548, (row * 16) + 192)
                board[row][column] = -1
                # board_changed = True
                # print("({}, {}): Click on ({}, {}) all bombs".format(tile_row, tile_column, row, column))

            # clicks all safe tiles
            if not bomb_or_safe and board[row][column] == 9:
                pyautogui.click((column * 16) + 548, (row * 16) + 192)
                board[row][column] = 0
                # board_changed = True
                # print("({}, {}): Click on ({}, {}) all safe".format(tile_row, tile_column, row, column))
    # return board_changed


def stuck():
    """ creates matrix where tiles have a percent chance of being bombs
    returns highest percent tile location
    """
    percent_matrix = [[round(0, 1) for i in range(width)] for j in range(height)]
    for row in range(height):
        for column in range(width):
            tile = board[row][column]
            unknowns = num_unknown(row, column, 0, 1)
            if tile == -1:
                percent_matrix[row][column] = -1

            elif num_unknown(row, column, 1, 0) == tile:
                continue

            elif tile != 0 and tile != -1 and tile != 9 and unknowns != 0:
                percent_value = tile/unknowns

                min_row = row - 1
                min_row = 0 if min_row < 0 else min_row

                max_row = row + 1
                max_row = height - 1 if max_row >= height else max_row

                min_column = column - 1
                min_column = 0 if min_column < 0 else min_column

                max_column = column + 1
                max_column = width - 1 if max_column >= width else max_column

                for row_unknown in range(min_row, max_row + 1):
                    for column_unknown in range(min_column, max_column + 1):
                        if row_unknown == row and column_unknown == column:
                            continue
                        elif board[row_unknown][column_unknown] == 9:
                            percent_matrix[row_unknown][column_unknown] = round((percent_matrix[row_unknown][column_unknown]+percent_value), 1)

    print_board(percent_matrix)

    biggest_percent = 0
    for row in range(height):
        for column in range(width):
            percent = percent_matrix[row][column]
            if 3 > percent > biggest_percent:  # here to restrict randomness
                biggest_percent = percent

    loc_all_biggest = []
    loc_all_biggest.clear()
    for row in range(height):
        for column in range(width):
            if percent_matrix[row][column] == biggest_percent:
                loc_all_biggest.append(((column * 16) + 548, (row * 16) + 192))

    return loc_all_biggest[0]


def start_over(should_board_reset):
    if should_board_reset:
        reset = pyautogui.locateCenterOnScreen('images/reset_button.png', grayscale=True)  # , region=(761, 138, 35, 35)
        # location.x, location.y
        if not reset:
            reset = pyautogui.locateCenterOnScreen('images/reset_lost.png', grayscale=True)  # , region=(761, 138, 35, 35)
            if not reset:
                print("Reset button not found.")
                exit(1)
        pyautogui.click(reset.x, reset.y)
        random_click()


def count_bombs():
    num_bombs = 0
    for row in range(height):
        num_bombs += board[row].count(-1)

    return num_bombs


class Resolution:

    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def get_left(self):
        left_most_tile = 29
        for row in range(height):
            for column in range(width):
                if board[row][column] != 9 and column < left_most_tile:
                    left_most_tile = column
        return (left_most_tile * 16) + 532

    def get_top(self):
        top_most_tile = 15
        for row in range(height):
            for column in range(width):
                if board[row][column] != 9 and row < top_most_tile:
                    top_most_tile = row
        return (top_most_tile * 16) + 156

    def get_width(self):
        right_most_tile = 0
        for row in range(height):
            for column in range(width):
                if board[row][column] != 9 and column > right_most_tile:
                    right_most_tile = column
        return (right_most_tile * 16) - self.get_left() + 564

    def get_height(self):
        bottom_most_tile = 0
        for row in range(height):
            for column in range(width):
                if board[row][column] != 9 and row > bottom_most_tile:
                    bottom_most_tile = row
        return (bottom_most_tile * 16) - self.get_top() + 200


time.sleep(2)

won = False


while not won:
    # initial variables
    height = 16
    width = 30
    win_counter = 0

    tile_states = {
        "tile": 'images/tile_{}.png'
    }

    board = [[9 for i in range(width)] for j in range(height)]

    start_over(1)  # 0 for not starting over, 1 to start over
    counter = 1

    dead = False

    prev_board = [[9 for i in range(width)] for j in range(height)]

    # bot starts

    read_full_board()

    # print('-------------------FIRST BOARD---------------------')
    # print_board(board)

    while not dead:

        print_board(board)
        # create previous board
        for tile_num in range(9):  # top left corner (center): 548 192
            for pos_tile_num in pyautogui.locateAllOnScreen(tile_states.get('tile').format(tile_num), region=(530, 127, 500, 330)):
                location = pyautogui.center(pos_tile_num)
                prev_board[round((location.y - 192) / 16)][round((location.x - 548) / 16)] = tile_num

        # looking for flags
        for pos_tile_num in pyautogui.locateAllOnScreen('images/tile_flag.png', region=(530, 127, 500, 330)):
            location = pyautogui.center(pos_tile_num)
            prev_board[round((location.y - 192) / 16)][round((location.x - 548) / 16)] = -1

        for row in range(height):
            for column in range(width):
                tile = board[row][column]
                if tile != -1 and tile != 0 and tile != 9:

                    if keyboard.is_pressed('q'):
                        exit(-1)
                    # surrounding tiles are all bombs
                    if tile == num_unknown(row, column, 0, 0):
                        clear_tiles(row, column, 1)
                        break

                    # surrounding tiles are all safe
                    elif tile == num_unknown(row, column, 1, 0):
                        clear_tiles(row, column, 0)
                        break

            # dead
            if pyautogui.locateOnScreen('images/reset_lost.png', grayscale=True):  # , region=(761, 138, 35, 35)
                dead = True
                print('lmao u lost.')
                break
                # exit(-1)

            # won
            if pyautogui.locateOnScreen('images/reset_won.png', grayscale=True):  # , region=(761, 138, 35, 35)
                won = True
                print('Congrats! You won.')
                exit(0)

        # print('---------------------------PREVIOUS BOARD---------------------------')
        # print_board(prev_board)
        # print('---------------------------BOARD---------------------------')
        # print_board(board)

        if counter % 3 == 0:
            read_full_board()
        else:
            read_board(0)

        num_bombs = count_bombs()

        if num_bombs == 100:
            unknown_locations = read_board(1)
            for unknown in unknown_locations:
                pyautogui.click(unknown.left, unknown.top)

        if prev_board == board:
            # print('------------- IM STUCK ------------------')

            if keyboard.is_pressed('q'):
                exit(-1)

            if num_bombs > 5:
                # print("GUESSING")
                (column_biggest, row_biggest) = stuck()
                pyautogui.click(column_biggest, row_biggest)
                # board[row][column] = -1
            else:
                # print('RANDOMLY CLICKING')
                random_click()
                read_full_board()

        counter += 1
