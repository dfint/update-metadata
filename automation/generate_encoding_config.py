from typing import Iterable, Iterator, Mapping, NamedTuple, Optional
from unidecode import unidecode
from collections import defaultdict


def get_letters(encoding: str) -> Iterator[str]:
    for i in range(256):
        try:
            char = bytes([i]).decode(encoding)
            if char.isalpha():
                yield char
        except UnicodeDecodeError:
            pass


def get_capitalize_map(letters: Iterable[str]) -> Iterator[tuple[str, str]]:
    for letter in letters:
        cap = letter.capitalize()
        if cap != letter and cap in letters:
            yield letter, cap


def get_lower_map(letters: Iterable[str]) -> Iterator[tuple[str, str]]:
    for letter in letters:
        low = letter.lower()
        if low != letter and low in letters:
            yield letter, low


def group_mapping(mapping: Iterable[tuple[str, str]], encoding: str) -> Iterator[str]:
    class State(NamedTuple):
        from_code: int
        to_code: int
        from_letter: str
        to_letter: str
        
        @property
        def diff(self):
            return to_code - from_code
        
        def is_plus_one(self, other):
            if not isinstance(other, self.__class__):
                return False
            
            if abs(other.from_code - self.from_code) > 1:
                return False
            
            return self.diff == other.diff
    
    def format_result(prev_state: State, state_start: State) -> str:
        if prev_state == state_start:
            return f"{prev_state.from_code} = {prev_state.diff} # {prev_state.from_letter} -> {prev_state.to_letter}"
        else:
            return (f"\"{state_start.from_code}:{prev_state.from_code}\" = {prev_state.diff} "
            f"# {state_start.from_letter}-{prev_state.from_letter} -> {state_start.to_letter}-{prev_state.to_letter}")
    
    state_start: Optional[State] = None
    prev_state: Optional[State] = None
    
    for from_letter, to_letter in mapping:
        to_code = to_letter.encode(encoding)[0]
        from_code = from_letter.encode(encoding)[0]
        
        current_state = State(from_code, to_code, from_letter, to_letter)
        
        if state_start is None:
            state_start = current_state
            prev_state = current_state

        if not current_state.is_plus_one(prev_state):
            yield format_result(prev_state, state_start)
            state_start = current_state
        
        prev_state = current_state
    
    if prev_state:
        yield format_result(prev_state, state_start)


def get_simplified_map(letters: Iterable[str]) -> Iterator[tuple[str, str]]:
    for letter in letters:
        simplified = unidecode(letter)
        if simplified != letter and simplified in letters:
            yield letter, simplified


def get_grouped_simplified(letters: Iterable[str]) -> Mapping[str, str]:
    simplified_map = get_simplified_map(letters)
    
    grouped_simplified = defaultdict(list)
    for letter, simplified in simplified_map:
        grouped_simplified[simplified.lower()].append(letter)
    
    return grouped_simplified


def main(encoding: str):
    print("[metadata]")
    print(f"encoding = \"{encoding}\"")
    print()
    
    letters = list(get_letters(encoding))
    
    print("[maps.capitalize]")
    capitalize_map = list(get_capitalize_map(letters))
    for line in group_mapping(capitalize_map, encoding):
        print(line)
    
    print()
    
    print("[maps.lowercast]")
    lower_map = list(get_lower_map(letters))
    for line in group_mapping(lower_map, encoding):
        print(line)

    print()
    
    print("[maps.simplify]")
    simplified = get_grouped_simplified(letters)
    simplified = {"".join(from_letters): to_letter for to_letter, from_letters in simplified.items()}
    for from_letters, to_letter in simplified.items():
        from_codes = "|".join([str(letter.encode(encoding)[0]) for letter in from_letters])
        to_code = to_letter.encode(encoding)[0]
        print(f""""{from_codes}" = {to_code} # {from_letters} -> {to_letter}""")


if __name__ == "__main__":
    main("cp866")
