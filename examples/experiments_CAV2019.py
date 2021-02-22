from examples import example_table, example_cell_model


def run():
    print("-------------\nRESULTS TABLE\n-------------\n\n")

    example_table.run_example(1)
    example_table.run_example(2)
    example_table.run_example(3)

    print("\n\n------------------\nRESULTS CELL MODEL\n------------------")

    example_cell_model.example_cell_plot_for_paper()


def main():
    run()


if __name__ == "__main__":
    main()
