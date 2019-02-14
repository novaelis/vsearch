def search_for_letters(phrase: str, letters_for_search: str='aeiou') -> set:
    """Return a set of the 'letters' found in 'phrase'."""
    # letters = set(letters_for_search)
    return set(letters_for_search).intersection(set(phrase))


def search_for_vowels(phrase: str) -> set:
    """Return any vowels dound in a supplied word."""
    vowels = set('aeiou')
    return vowels.intersection(set(phrase))
