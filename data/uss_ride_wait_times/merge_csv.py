import csv
import glob

def merge_csv(folder, output):
    file_pattern = 'Raw Data/' + folder + '/download*.csv'
    first_file = True

    with open(output, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for filename in glob.glob(file_pattern):
            with open(filename, 'r') as infile:
                reader = csv.reader(infile)
                try:
                    headers = next(reader)
                    if first_file:
                        writer.writerow(headers)
                        first_file = False
                    for row in reader:
                        writer.writerow(row)
                except StopIteration:
                    continue  # skip empty files
    return

merge_csv('Accelerator', 'merged_accelerator.csv')
merge_csv('Battlestar Galactica_CYLON', 'merged_cylon.csv')
merge_csv('Battlestar Galactica_HUMAN', 'merged_human.csv')
merge_csv('Buggie Boogie', 'merged_buggieboogie.csv')
merge_csv('Canopy Flyer', 'merged_canopyflyer.csv')
merge_csv('Despicable Me Minion Mayhem', 'merged_minionmayhem.csv')
merge_csv('Dino Soarin', 'merged_dinosoarin.csv')
merge_csv('Enchanted Airways', 'merged_enchantedairways.csv')
merge_csv('Jurassic Park Rapids Adventure', 'merged_jurassic.csv')
merge_csv('Lights Camera Action_Hosted by Steven Spielberg', 'merged_lightscameraaction.csv')
merge_csv('Magic Potion Spin', 'merged_magicpotionspin.csv')
merge_csv('Puss in Boots Giant Journey', 'merged_pussinboots.csv')
merge_csv('Revenge of the Mummy', 'merged_mummy.csv')
merge_csv('Sesame Street Spaghetti Space Chase', 'merged_sesamestreet.csv')
merge_csv('Shrek 4D Adventure', 'merged_shrek.csv')
merge_csv('Silly Swirly', 'merged_sillyswirly.csv')
merge_csv('TRANSFORMERS The Ride', 'merged_transformers.csv')
merge_csv('Treasure Hunters', 'merged_treasurehunters.csv')

def merge_csv_full(output):
    file_pattern = 'merged*.csv'
    first_file = True

    with open(output, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for filename in glob.glob(file_pattern):
            with open(filename, 'r') as infile:
                reader = csv.reader(infile)
                try:
                    headers = next(reader)
                    if first_file:
                        writer.writerow(headers)
                        first_file = False
                    for row in reader:
                        writer.writerow(row)
                except StopIteration:
                    continue  # skip empty files
    return

merge_csv_full('all_ride_wait_times.csv')