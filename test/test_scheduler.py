from pycamp_bot.scheduler.schedule_calculator import (
    PyCampScheduleProblem,
    hill_climbing,
    IMPOSIBLE_COST,
)


def _make_problem_data(projects=None, slots=None):
    """Helper para crear datos de problema de scheduling."""
    if slots is None:
        slots = ["A1", "A2", "B1", "B2"]
    if projects is None:
        projects = {
            "proyecto1": {
                "responsables": ["pepe"],
                "votes": ["juan", "maria"],
                "difficult_level": 1,
                "theme": "django",
                "priority_slots": [],
            },
            "proyecto2": {
                "responsables": ["ana"],
                "votes": ["juan", "carlos"],
                "difficult_level": 2,
                "theme": "flask",
                "priority_slots": [],
            },
        }
    responsable_available_slots = {}
    for proj_data in projects.values():
        for resp in proj_data["responsables"]:
            responsable_available_slots[resp] = slots

    return {
        "projects": projects,
        "available_slots": slots,
        "responsable_available_slots": responsable_available_slots,
    }


class TestPyCampScheduleProblemInit:

    def test_creates_problem_from_data(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        assert problem.data is not None

    def test_responsables_added_to_votes(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        assert "pepe" in problem.data.projects.proyecto1.votes
        assert "ana" in problem.data.projects.proyecto2.votes

    def test_project_list_extracted(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        assert "proyecto1" in problem.project_list
        assert "proyecto2" in problem.project_list
        assert len(problem.project_list) == 2

    def test_total_participants_calculated(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        # Votantes únicos: juan, maria, carlos, pepe, ana (responsables se agregan a votos)
        all_voters = set()
        for proj in data["projects"].values():
            all_voters.update(proj["votes"])
            all_voters.update(proj["responsables"])
        assert problem.total_participants == len(all_voters)


class TestGenerateRandomState:

    def test_returns_all_projects(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        state = problem.generate_random_state()
        project_names = [proj for proj, _ in state]
        assert "proyecto1" in project_names
        assert "proyecto2" in project_names

    def test_each_project_has_valid_slot(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        state = problem.generate_random_state()
        for _, slot in state:
            assert slot in data["available_slots"]

    def test_random_state_length(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        state = problem.generate_random_state()
        assert len(state) == len(data["projects"])


class TestNeighboors:

    def test_includes_single_reassignment(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        state = [("proyecto1", "A1"), ("proyecto2", "A2")]
        neighbors = problem.neighboors(state)
        # Debe incluir reasignaciones de proyecto1 a A2, B1, B2
        reassigned = [n for n in neighbors if dict(n)["proyecto1"] != "A1" and dict(n)["proyecto2"] == "A2"]
        assert len(reassigned) == 3  # A2, B1, B2

    def test_includes_swaps(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        state = [("proyecto1", "A1"), ("proyecto2", "A2")]
        neighbors = problem.neighboors(state)
        # Debe incluir swap: proyecto1->A2, proyecto2->A1
        swapped = [n for n in neighbors if dict(n)["proyecto1"] == "A2" and dict(n)["proyecto2"] == "A1"]
        assert len(swapped) == 1

    def test_neighboors_count(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        state = [("proyecto1", "A1"), ("proyecto2", "A2")]
        neighbors = problem.neighboors(state)
        # Reasignaciones: 2 proyectos * 3 slots alternativos = 6
        # Swaps: C(2,2) = 1 (solo si slots diferentes)
        assert len(neighbors) == 7


class TestValue:

    def test_no_collisions_returns_negative_value(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        # Proyectos en slots distintos: sin colisiones
        state = [("proyecto1", "A1"), ("proyecto2", "B1")]
        value = problem.value(state)
        assert value < 0  # Siempre negativo por slot_population_cost y most_voted_cost

    def test_responsable_collision_impossible_cost(self):
        projects = {
            "proyecto1": {
                "responsables": ["pepe"],
                "votes": ["juan"],
                "difficult_level": 1,
                "theme": "django",
                "priority_slots": [],
            },
            "proyecto2": {
                "responsables": ["pepe"],  # Mismo responsable
                "votes": ["maria"],
                "difficult_level": 2,
                "theme": "flask",
                "priority_slots": [],
            },
        }
        data = _make_problem_data(projects=projects)
        problem = PyCampScheduleProblem(data)
        # Mismos responsables en el mismo slot
        state_collision = [("proyecto1", "A1"), ("proyecto2", "A1")]
        state_no_collision = [("proyecto1", "A1"), ("proyecto2", "B1")]
        val_collision = problem.value(state_collision)
        val_no_collision = problem.value(state_no_collision)
        # La colisión de responsables debe hacer mucho peor el valor
        assert val_collision < val_no_collision
        assert (val_no_collision - val_collision) >= IMPOSIBLE_COST

    def test_voter_collision_increases_cost(self):
        projects = {
            "proyecto1": {
                "responsables": ["pepe"],
                "votes": ["juan", "maria"],
                "difficult_level": 1,
                "theme": "django",
                "priority_slots": [],
            },
            "proyecto2": {
                "responsables": ["ana"],
                "votes": ["juan", "maria"],  # Mismos votantes
                "difficult_level": 2,
                "theme": "flask",
                "priority_slots": [],
            },
        }
        data = _make_problem_data(projects=projects)
        problem = PyCampScheduleProblem(data)
        state_collision = [("proyecto1", "A1"), ("proyecto2", "A1")]
        state_no_collision = [("proyecto1", "A1"), ("proyecto2", "B1")]
        assert problem.value(state_collision) < problem.value(state_no_collision)

    def test_same_difficulty_penalized(self):
        projects = {
            "proyecto1": {
                "responsables": ["pepe"],
                "votes": [],
                "difficult_level": 1,
                "theme": "django",
                "priority_slots": [],
            },
            "proyecto2": {
                "responsables": ["ana"],
                "votes": [],
                "difficult_level": 1,  # Mismo nivel
                "theme": "flask",
                "priority_slots": [],
            },
        }
        data = _make_problem_data(projects=projects)
        problem = PyCampScheduleProblem(data)
        state_same_slot = [("proyecto1", "A1"), ("proyecto2", "A1")]
        state_diff_slot = [("proyecto1", "A1"), ("proyecto2", "B1")]
        assert problem.value(state_same_slot) <= problem.value(state_diff_slot)

    def test_same_theme_penalized(self):
        projects = {
            "proyecto1": {
                "responsables": ["pepe"],
                "votes": [],
                "difficult_level": 1,
                "theme": "django",
                "priority_slots": [],
            },
            "proyecto2": {
                "responsables": ["ana"],
                "votes": [],
                "difficult_level": 2,
                "theme": "django",  # Mismo tema
                "priority_slots": [],
            },
        }
        data = _make_problem_data(projects=projects)
        problem = PyCampScheduleProblem(data)
        state_same_slot = [("proyecto1", "A1"), ("proyecto2", "A1")]
        state_diff_slot = [("proyecto1", "A1"), ("proyecto2", "B1")]
        assert problem.value(state_same_slot) <= problem.value(state_diff_slot)


class TestHillClimbing:

    def test_returns_valid_state(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        initial = problem.generate_random_state()
        result = hill_climbing(problem, initial)
        project_names = [proj for proj, _ in result]
        assert "proyecto1" in project_names
        assert "proyecto2" in project_names

    def test_result_is_local_optimum(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        initial = problem.generate_random_state()
        result = hill_climbing(problem, initial)
        result_value = problem.value(result)
        # Ningún vecino debe ser mejor
        for neighbor in problem.neighboors(result):
            assert problem.value(neighbor) <= result_value

    def test_improves_or_maintains_initial_value(self):
        data = _make_problem_data()
        problem = PyCampScheduleProblem(data)
        initial = problem.generate_random_state()
        initial_value = problem.value(initial)
        result = hill_climbing(problem, initial)
        assert problem.value(result) >= initial_value
