import data.real_data.preprocess as prep
import data.real_data.dataplot as dp


for i in range(1,10):

    filename = "../data/real_data/Diabetes/UCI/Diabetes-Data/data-0"+str(i)
    newfilename = "../data/real_data/Diabetes/UCI/Diabetes-csv/block_time/data-0"+str(i)+".csv"
    prep.diabetesdata_format_transformation(filename, newfilename)

    filename = "../data/real_data/Diabetes/UCI/Diabetes-csv/block_time/data-0"+str(i)+".csv"
    newfilename = "../data/real_data/Diabetes/UCI/Diabetes-csv/single_time/data-0" + str(i) + ".csv"
    prep.diabetesdata_time_block(filename,newfilename)

for i in range(10,71):

    filename = "../data/real_data/Diabetes/UCI/Diabetes-Data/data-"+str(i)
    newfilename = "../data/real_data/Diabetes/UCI/Diabetes-csv/block_time/data-"+str(i)+".csv"
    prep.diabetesdata_format_transformation(filename, newfilename)

    filename = "../data/real_data/Diabetes/UCI/Diabetes-csv/block_time/data-" + str(i) + ".csv"
    newfilename = "../data/real_data/Diabetes/UCI/Diabetes-csv/single_time/data-" + str(i) + ".csv"
    prep.diabetesdata_time_block(filename, newfilename)