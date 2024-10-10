def pytest_addoption(parser):
    parser.addoption(
        "--database",
        action="store",
        default="mock",
        choices=["mock", "sqlite"],
        help="Specify the database type to use for testing: mock or sqlite",
    )
