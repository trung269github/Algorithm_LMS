from ortools.sat.python import cp_model


def main():
    with open(r"C:\Users\DELL\Downloads\Algorithm_LMS\solver-main\data-5.txt", "r") as file:
        #  Data
        num_teachers, num_courses = map(int, file.readline().split())
        all_teachers = range(num_teachers)
        all_courses = range(num_courses)

        interests = []
        for _ in all_teachers:
            _, *subject = map(int, file.readline().split())
            interests.append(list(map(lambda x: x - 1, subject)))

        conflicts = [[False for _ in all_courses] for _ in all_courses]
        for _ in range(int(file.readline())):
            c1, c2 = map(int, file.readline().split())
            conflicts[c1 - 1][c2 - 1] = True
            conflicts[c2 - 1][c1 - 1] = True

        #  Model
        model = cp_model.CpModel()

        # Variables
        assignments = {}
        for t in all_teachers:
            for c in all_courses:
                assignments[(t, c)] = model.NewBoolVar(f"assignments[{t},{c}]")

        # Constraints
        # 1. Each course is assigned to exactly one teacher
        for c in all_courses:
            model.Add(sum(assignments[(t, c)] for t in all_teachers) == 1)
        # 2. No two conflicting courses are assigned to the same teacher
        for t in all_teachers:
            for c1 in all_courses:
                for c2 in all_courses:
                    if conflicts[c1][c2]:
                        # model.Add(
                        #     assignments[(i, j)].Not()
                        #     + assignments[(i, k)].Not()
                        #     >= 1
                        # )
                        model.AddBoolOr(
                            [
                                assignments[(t, c1)].Not(),
                                assignments[(t, c2)].Not(),
                            ]
                        )
        # 3. Each course is assigned to a teacher who can teach it
        for t in all_teachers:
            for c in all_courses:
                if c not in interests[t]:
                    model.Add(assignments[(t, c)] == 0)

    # Objective
    # https://stackoverflow.com/questions/69397752/google-or-tools-solving-an-objective-function-containing-max-function-of-multip
    # Make sure the teacher with the highest load has the lowest load possible
    max_load = model.NewIntVar(0, num_courses, "max_load")
    for t in all_teachers:
        model.Add(max_load >= sum(assignments[(t, c)] for c in all_courses))
    model.Minimize(max_load)

    # Solver
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:
        for t in all_teachers:
            for c in all_courses:
                if solver.Value(assignments[(t, c)]) == 1:
                    print(f"Teacher {t + 1} teaches course {c + 1}")
        print(solver.ObjectiveValue())
    else:
        print(-1)


if __name__ == "__main__":
    main()
