import json
from typing import NamedTuple, Dict, Tuple, Optional, Sequence, List, Set, FrozenSet
import array
import heapq
import time
import itertools

with open('Crafting.json') as f:
    Crafting = json.load(f)
#+END_SRC python
#k
#You may want to try printing out some different information from =Crafting= to get a feel for its schema:

#+BEGIN_SRC python
# Example

# List of items that can be in your inventory:
print(Crafting['Items'])
# example: ['bench', 'cart', ..., 'wood', 'wooden_axe', 'wooden_pickaxe']

# List of items needed to be in your inventory at the end of the plan:
# (okay to have more than this; some might be satisfied by initial inventory)
print(Crafting['Goal'])
# {'stone_pickaxe': 2}

# Dict of crafting recipes (each is a dict):
print(Crafting['Recipes']['craft stone_pickaxe at bench'])
# { 'Produces': {'stone_pickaxe': 1},
# 'Requires': {'bench': True},
# 'Consumes': {'cobble': 3, 'stick': 2},
# 'Time': 1
# }
items_by_index: List[str] = Crafting['Items']
items_to_indices: Dict[str, int] = {
    item: index for index, item in enumerate(items_by_index)
}

class State:
    items: array.array

    def __init__(self, items: Optional[Sequence[int]] = None) -> None:
        if items is not None:
            # Copying a state from an old state.
            # This call to the array constructor creates an array of unsigned integers and initializes it from the contents of items.
            self.items = array.array('I', items)
        else:
            self.items = array.array('I', [0 for item in items_by_index])

    def __add__(self, other:'State') -> 'State':
        s = State(self.items)
        # A. How do we add together the contents of two states?
        for i in range(0,len(s.items)):
            s.items[i] += other.items[i]
        return s

    def __sub__(self, other:'State') -> 'State':
        s = State(self.items)
        # B. How do we subtract one state from another?
        for i in range(0,len(s.items)):
            s.items[i] = abs(s.items[i] - other.items[i])
        return s

    def __ge__(self, other: 'State') -> bool:
        # C. How do we know whether one state (self) contains everything that's inside of another (other)?
        for i in range(0,len(self.items)):
            if(self.items[i] < other.items[i]):
                return False
        return True

    def __lt__(self, other: 'State') -> bool:
        return not (self >= other)

    def __eq__(self, other) -> bool:
        return self.items == other.items

    def __hash__(self) -> int:
        hsh = 5381
        for s in self.items:
            hsh = ((hsh << 5) + hsh) + s
        return hsh

    def __str__(self) -> str:
        return self.to_dict().__str__()

    def to_dict(self) -> Dict[str, int]:
        return {items_by_index[idx]: self.items[idx]
                for idx in range(len(self.items))}

    @classmethod
    def from_dict(cls, item_dict: Dict[str, int]) -> 'State':
        return cls([
            item_dict.get(item, 0) for item in items_by_index
        ])

class Recipe(NamedTuple):
    produces: State
    consumes: State
    requires: State
    cost: int

recipes: Dict[str, Recipe] = {}
for name, rule in Crafting['Recipes'].items():
    recipes[name] = Recipe(
        State.from_dict(rule.get('Produces', {})),
        State.from_dict(rule.get('Consumes', {})),
        State.from_dict({item: 1 if req else 0
                         for item, req in rule.get('Requires', {}).items()}),
        rule['Time']
    )

def preconditions_satisfied(state: State, recipe: Recipe) -> bool:
    # D. What needs to be true about state and recipe?
    # Feel free to use State's >= method
    for i in range(0, len(recipe.requires.items)):
        if state.items[i] < recipe.requires.items[i]:
            return False
        if state.items[i] < recipe.consumes.items[i]:
            return False
    return True

def apply_effects(state: State, recipe: Recipe) -> State:
    # E. How do you make a new state out of a state and a recipe?
    # Note, DO NOT change state in-place!
    if(preconditions_satisfied(state, recipe)):
        state = state - recipe.consumes
        state = state + recipe.produces
        return state
    return None

def find_neighbors(initial: State) -> List[Tuple[str, int]]:
    neighbors : List[Tuple[State, int]] = []
    for recipe_str, recipe in recipes.items():
        if preconditions_satisfied(initial, recipe):
            neighbors.append((recipe_str, recipe.cost))
    return neighbors

def plan_dijkstra(initial: State, goal: State, limit:int) -> Tuple[int, int, Optional[List[str]]]:
    start_time = 0
    # E. Implement it here!  When you find a solution, print out the number of nodes visited and the time it took to get there.  If you don't find a solution, print out the number of nodes visited and the time it took to fail.
    # Feel free to use or modify the solution printing routine from the last exercise.
    # Return a tuple of (nodes_visited, -1, None) if no path exists, or else a tuple of (nodes_visited, cost, path) where path is a list of recipe names.
    # You should also use limit to avoid visiting too many nodes before returning _something_.
    # Finally, you can check whether a State _satisfies_ a goal by checking `state >= goal`
    open_list: List[Tuple[int, State]] = [(start_time, initial)];
    best_costs: Dict[State, Tuple[int, str, State]] = {initial:(start_time, "initial", initial)};
    visit_count = 0;
    meets_goal = goal;
    while open_list:
        cost, state = heapq.heappop(open_list)
        if(visit_count >= limit):
            break
        visit_count += 1
        if (state >= goal):
            meets_goal = state
            break
        neighbors = find_neighbors(state)
        for recipe_str, recipe_cost in neighbors:
            tempState = state
            recipe = recipes.get(recipe_str)
            nextState = apply_effects(tempState, recipe)
            if(nextState not in best_costs):
                heapq.heappush(open_list, (cost + recipe_cost, nextState))
                cost2, recipe_str2, prevState = best_costs.get(state);
                best_costs[nextState] = (cost2 + recipe_cost, recipe_str, state)
            pass
        pass
    if(meets_goal in best_costs):
        cost, recipe_str, prevState = best_costs.get(meets_goal)
        path: List[str] = []
        tempCost, tempRecipe_str, tempPrevState = best_costs.get(meets_goal)
        while(tempRecipe_str != "initial"):
            path.append(tempRecipe_str)
            tempCost, tempRecipe_str, tempPrevState = best_costs.get(tempPrevState);
        path.reverse()
        return (visit_count, cost, path)
    else:
        return (visit_count, -1, None)

# print(plan_dijkstra(State.from_dict({}),
#                     State.from_dict({'stone_pickaxe':1}),
#                     200000))
# print(plan_dijkstra(State.from_dict({'bench':1,'stone_pickaxe':1}),
#                     State.from_dict({'ingot':1}),
#                     200000))

class Proposition(NamedTuple):
    item: int
    at_least: int

def state_propositions(state: State) -> Set[Proposition]:
    propositions: Set[Proposition] = set()
    # F. Do something for each item in state.  Output all propositions entailed by the state's contents
    for i in range(0, len(state.items)):
        if(state.items[i] > 0):
            for j in range(1, state.items[i]+1):
                tempProp: Proposition = Proposition(
                    item = i,
                    at_least = j)
                propositions.add(tempProp)
    return propositions

# Now let's get the propositions from the recipes

def recipe_to_propositions(recipe: Recipe) -> Set[Proposition]:
    propositions: Set[Proposition] = set()
    # G. Do something with recipe.consumes, recipe.produces, and recipe.requires.
    produceProp = state_propositions(recipe.produces)
    requiresProp = state_propositions(recipe.requires)
    consumeProp = state_propositions(recipe.consumes)
    propositions |= produceProp
    propositions |= requiresProp
    propositions |= consumeProp
    # Output, for this recipe, all the propositions entailed by the preconditions and the _minimal_ set of propositions embodied in the postconditions (i.e., don't need to output wood >= 2, wood >= 1, wood >= 0 if the recipe creates 2 wood.)
    return propositions

recipe_propositions = set()
for r in recipes.values():
    recipe_propositions |= recipe_to_propositions(r)

# # Example, assuming propositions is a Set[Proposition]
# state_props:Set[Proposition] = state_propositions(state)
# if state_props.issuperset(propositions):
#     pass
#     # The state has this combination!
# else:
#     pass
#     # The state does not!

# set of FrozenSets -- all witnessed combinations of propositions
def see_state(state:State, combinations:List[Set[Proposition]], seen_combinations:Set[FrozenSet[Proposition]]) -> bool:
    any_new = False
    state_props = state_propositions(state)
    for combo in combinations:
        # H. Is this combination already in seen_combinations?
        if (combo not in seen_combinations):
            if (state_props.issuperset(combo)):
                any_new = True
                break
        # I. If not, it's novel; so is this combination a subset of the state_props?
        pass
    return any_new

def plan_width(initial: State, goal: State, WMax: int) -> Tuple[int, int, Optional[List[str]]]:
    start_time = time.time()
    all_propositions = recipe_propositions | state_propositions(initial) | state_propositions(goal)
    all_combinations: List[FrozenSet[Proposition]] = []
    # Increase W up to WMax
    for W in range(1, WMax + 1):
        visited = 0
        # Calculate all combinations of propositions at size W and add to all_combinations
        all_combinations += [frozenset(props) for props in itertools.combinations(all_propositions, W)]
        # Sanity check that this is 6279 for W=3, for example
        print("W=",W,"Combination count=",len(all_combinations))
        # Track, for each combination (by index), whether we have seen this combination before (0 for no, >0 for yes)
        seen_combinations: Set[FrozenSet[Proposition]] = set()
        # Initialize seen_combinations
        see_state(initial, all_combinations, seen_combinations)
        open_list: List[Tuple[int, State]] = [(0, initial)]
        best_costs: Dict[State, int] = {initial: 0}
        best_from: Dict[State, List[str]] = {initial: []}
        while open_list:
            cost, state = heapq.heappop(open_list)
            visited += 1
            # I. This should look like your graph search (Dijkstra's is a nice choice), except...
            # Call see_state on newly expanded states to update seen_combinations and use its return value to decide whether to add this state to the open list (is that the only thing that determines whether it should go on the open list?)
    return visited, -1, None
#
# # Example
# # Try harder ones once you have these down
#
# print(width_search({},{'bench':1},4))
# print(width_search({'wood':1},{'iron_pickaxe':1},4))
# print(width_search({},{'rail':1},4))
# print(width_search({},{'cart':1},4))
