import data.real_data.preprocess as prep
import data.real_data.dataplot as dp


from hysynth import ha_synthesis_from_data_pwl


def example_ekg_1():

    filename1 = "../data/real_data/datasets/ekg_data/ekg_1.csv"
    filename2 = "../data/real_data/datasets/ekg_data/ekg_2.csv"
    filename3 = "../data/real_data/datasets/ekg_data/ekg_3.csv"

    f1 = prep.data2array(filename1, 2)
    f2 = prep.data2array(filename2, 2)
    f3 = prep.data2array(filename3, 2)

    time_series_dataset = [f1, f2, f3]


    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.05,
                                    clustering_bandwidth=False)

    print(ha)

    dp.multilineplot(time_series_dataset)


def example_ekg_2():

    filename1 = "../data/real_data/datasets/ekg_data/ekg2_1.csv"
    filename2 = "../data/real_data/datasets/ekg_data/ekg2_2.csv"
    filename3 = "../data/real_data/datasets/ekg_data/ekg2_3.csv"

    f1 = prep.data2array(filename1, 2)
    f2 = prep.data2array(filename2, 2)
    f3 = prep.data2array(filename3, 2)

    time_series_dataset = [f1, f2, f3]


    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.05,
                                    clustering_bandwidth=False)

    print(ha)

    dp.multilineplot(time_series_dataset)

def example_pulse1():

    filename1 = "../data/real_data/datasets/basic_data/pulse1-1.csv"
    filename2 = "../data/real_data/datasets/basic_data/pulse1-2.csv"
    filename3 = "../data/real_data/datasets/basic_data/pulse1-3.csv"

    f1 = prep.data2array(filename1, 1)
    f2 = prep.data2array(filename2, 1)
    f3 = prep.data2array(filename3, 1)

    time_series_dataset = [f1, f2, f3]


    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.05,
                                    clustering_bandwidth=False)

    print(ha)

    dp.multilineplot(time_series_dataset)


def example_pulse2():

    filename1 = "../data/real_data/datasets/basic_data/pulse2-1.csv"
    filename2 = "../data/real_data/datasets/basic_data/pulse2-2.csv"
    filename3 = "../data/real_data/datasets/basic_data/pulse2-3.csv"

    f1 = prep.data2array(filename1, 1)
    f2 = prep.data2array(filename2, 1)
    f3 = prep.data2array(filename3, 1)

    time_series_dataset = [f1, f2, f3]


    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.05,
                                    clustering_bandwidth=False)

    print(ha)

    dp.multilineplot(time_series_dataset)



def main():
    example_ekg_1()
    # example_ekg_2()
    # example_pulse1()


if __name__ == "__main__":
    main()
