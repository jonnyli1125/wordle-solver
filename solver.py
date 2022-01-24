import argparse


class Solver:
    def __init__(self, n_letters=5, top_k_results=10, hard_mode=False,
                 vocab_path='vocab.txt',
                 guess_vocab_path='guess_vocab.txt'):
        # config variables
        self.n_letters = n_letters
        self.top_k_results = top_k_results

        # vocab
        self.letters = set()
        self.vocab = set()
        with open(vocab_path, 'r') as f:
            for line in f:
                word = line.strip()
                self.letters |= {c for c in word}
                self.vocab.add(word)
        with open(guess_vocab_path, 'r') as f:
            self.guess_vocab = {line.strip() for line in f}

        # game state variables
        self.new_game(hard_mode)

    def new_game(self, hard_mode=False):
        self.n_guesses = 0
        self.hard_mode = hard_mode
        self.match_letters = [set(self.letters)
                              for i in range(self.n_letters)]
        self.have_letters = set()

    def guess(self, guess_word='', hint=''):
        """
        Input:
        - word: guessed word
        - hint: string of 0, 1, 2s to represent the hint returned from the word
        Output:
        - results: top K guesses for the word
        """
        # update filters
        for i, (c, c_hint) in enumerate(zip(guess_word, hint)):
            if c_hint == '2':
                self.match_letters[i] = {c}
                self.have_letters.add(c)
            elif c_hint == '1':
                self.match_letters[i].discard(c)
                self.have_letters.add(c)
            elif c_hint == '0':
                for j in range(self.n_letters):
                    self.match_letters[j].discard(c)

        # get guess vocab set
        f_vocab = self._filtered_vocab()
        if self.n_guesses == 0 or (self.hard_mode and self.n_guesses == 1):
            vocab = self.guess_vocab
        else:
            vocab = f_vocab
        self.n_guesses += 1

        # sort and return top k
        results = sorted(((w, self._n_splits(w, f_vocab)) for w in vocab),
            key=lambda x: -x[1])[:self.top_k_results]
        return results

    def _filtered_vocab(self):
        return {w for w in self.vocab if self._word_matches_filters(w)}

    def _word_matches_filters(self, word):
        if self.have_letters and not self.have_letters.issubset(word):
            return False
        for i, cs in enumerate(self.match_letters):
            if word[i] not in cs:
                return False
        return True

    def _n_splits(self, guess_word, vocab):
        return len({self._word_to_hint(guess_word, word) for word in vocab})

    def _word_to_hint(self, guess_word, word):
        hint = ''
        for c_guess, c in zip(guess_word, word):
            if c_guess == c:
                hint += '2'
            elif c_guess in word:
                hint += '1'
            else:
                hint += '0'
        return hint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-hm', '--hard_mode', action='store_true')
    # TODO: add oracle mode
    # parser.add_argument('-o', '--oracle', type=str, default='')
    args = parser.parse_args()

    solver = Solver(hard_mode=args.hard_mode)

    def display_results(results):
        print(f'Top {solver.top_k_results} guesses:')
        for word, score in results:
            print(word, score)

    results = solver.guess()
    display_results(results)

    while len(results) > 1:
        guess_word = input('Word: ')
        if len(guess_word) != solver.n_letters:
            print(f'Word must be {solver.n_letters} letters long')
            continue
        hint = input('Hint: ')
        if len(hint) != solver.n_letters:
            print(f'Hint must be {solver.n_letters} letters long')
            continue
        results = solver.guess(guess_word, hint)
        display_results(results)


if __name__ == '__main__':
    main()
