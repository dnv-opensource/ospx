from ospx.simulation import Simulation


def test_simulation_init_default_values() -> None:
    # Execute
    simulation = Simulation()

    # Assert
    assert simulation.name is None
    assert simulation.start_time is None
    assert simulation.stop_time is None
    assert simulation.base_step_size is None
    assert simulation.algorithm == "fixedStep"


def test_simulation_init_with_values() -> None:
    # Execute
    simulation = Simulation(
        name="test_sim",
        start_time=0.0,
        stop_time=10.0,
        base_step_size=0.01,
    )

    # Assert
    assert simulation.name == "test_sim"
    assert simulation.start_time == 0.0
    assert simulation.stop_time == 10.0
    assert simulation.base_step_size == 0.01
    assert simulation.algorithm == "fixedStep"


def test_simulation_algorithm_setter_valid() -> None:
    # Prepare
    simulation = Simulation(name="test_sim")

    # Execute
    simulation.algorithm = "ecco"

    # Assert
    assert simulation.algorithm == "ecco"


def test_simulation_algorithm_setter_invalid() -> None:
    # Prepare
    simulation = Simulation(name="test_sim")

    # Execute
    simulation.algorithm = "invalid_algorithm"

    # Assert
    assert simulation.algorithm == "fixedStep"


def test_simulation_algorithm_getter() -> None:
    # Prepare
    simulation = Simulation(name="test_sim", _algorithm="ecco")

    # Execute & Assert
    assert simulation.algorithm == "ecco"
