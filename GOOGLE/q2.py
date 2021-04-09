# Linear: try all split points
# Keeping track of letters in L and R all along in an array for ea
# And keeping sum

import sys


def solution(S):
    # Special case:
    if len(S) == 2:
        return 1
    num_valid_splits = 0
    # Initialize right letters to nothing
    right_letters = []
    # Initialize left letters to letters of entire string
    # Use dict to store *left-most* index of the letter so you know when to remove it
    left_letters = {}
    left_letter_keys = set(S)
    for key in left_letter_keys:
        left_letters[key] = S.find(key)
    # Count number of unique letters in each
    right_num = 0
    left_num = len(left_letter_keys)
    # split_idx is before corresponding char
    for split_idx in range(len(S) - 1, 0, -1): # Really len(S)-1 to 1
        # Each move of split point adds letter to right letters
        # and removes same letter from left letters
        letter = S[split_idx]
        if letter in right_letters:
            pass
        else:
            right_letters.append(letter)
            right_num = right_num + 1
        if left_letters[letter] == split_idx: # remove from left_letters
            del left_letters[letter]
            left_num = left_num - 1
        else:
            pass
        if right_num == left_num:
            num_valid_splits = num_valid_splits + 1
    return num_valid_splits


def main():
    """Read from stdin, solve the problem, write answer to stdout."""
    input = sys.stdin.readline().strip()
    sys.stdout.write(str(solution(input)))


if __name__ == "__main__":
    main()