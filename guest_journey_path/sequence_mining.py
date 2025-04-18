import pandas as pd
from spmf import Spmf

def sequence_mining(seq):
    # Data Preparation - convert from Dataframe to list of lists
    sequences = seq.tolist()

    # Replace zone names with numerical labels
    zone_index = {'hollywood': '1', 'minion_land': '2', 'far_far_away':'3', 'lost_world':'4', 'ancient_egypt':'5', 'scifi_city':'6', 'new_york':'7'}
    prepped_data = [[zone_index.get(key) for key in seq] for seq in sequences]

    # Rename output data with original string values for ease of reading post-processing
    index_convert = '@CONVERTED_FROM_TEXT\n@ITEM=1=hollywood\n@ITEM=2=minion_land\n@ITEM=3=far_far_away\n@ITEM=4=lost_world\n@ITEM=5=ancient_egypt\n@ITEM=6=scifi_city\n@ITEM=7=new_york\n@ITEM=-1=-1\n'
    
    # Formatting input data into txt file for spmf to read
    input_data = '\n'.join(' -1 '.join(seq) + ' -1 -2' for seq in prepped_data)

    # Write data into input.txt file
    with open("input.txt", "w") as f:
        f.write(index_convert)
        f.write(input_data)
    
    # Run SPMF library for sequence mining
    spmf = Spmf('TNS', input_filename='input.txt', output_filename='output.txt', arguments=[7, 0.5, 10]) #k=7, confidence=0.5, delta=10
    spmf.run()
    results = TNS_to_dataframe('output.txt')
    
    return results

def TNS_to_dataframe(output_file):
    rules = []

    with open(output_file, "r") as f:
        for line in f:
            parts = line.strip().split(" #SUP:")  # Split by support keyword

            rule_part = parts[0]  # Extract rule
            sup_conf_part = parts[1]  # Extract support and confidence

            rule_split = rule_part.split(" ==> ")  # Split antecedent and consequent
            antecedent = rule_split[0]
            consequent = rule_split[1] if len(rule_split) > 1 else ""

            # Extract support and confidence
            sup_conf_split = sup_conf_part.split(" #CONF:")
            support = int(sup_conf_split[0])
            confidence = float(sup_conf_split[1])  # Convert to decimal

            # Append to list
            rules.append([antecedent, consequent, support, confidence])

    # Create DataFrame
    df = pd.DataFrame(rules, columns=['visited_zone', 'next_zone', 'sup', 'conf'])
    return df