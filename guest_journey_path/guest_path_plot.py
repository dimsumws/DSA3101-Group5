import matplotlib.pyplot as plt
import seaborn as sns

def plot_graph(label, data):
    path_matrix = data[['hollywood', 'minion_land', 'far_far_away', 'lost_world', 'ancient_egypt', 'scifi_city', 'new_york']]
    # subplots set up
    num_cols = len(path_matrix.columns)
    fig, axes = plt.subplots(nrows=(num_cols + 2) // 3, ncols=3, figsize=(15, 10))
    axes = axes.flatten()
    plt.suptitle(f'Visit Order for {label} Ride Preference Guests')

    # generating bar plots for each zone
    for i, col in enumerate(path_matrix.columns):
        counts = path_matrix[col].value_counts(dropna=False).sort_index()  # Include NaNs and sort categories
        sns.barplot(x=counts.index.astype(str), y=counts.values, ax=axes[i])
        axes[i].set_ylim(0, 10)
        axes[i].set_title(f"guest visit order for {col}")
        axes[i].set_xlabel('order of sequence')
        axes[i].set_ylabel("count")
        
        # value labels
        for j, v in enumerate(counts.values):
            axes[i].text(j, v + 0.1, str(v), ha='center', fontsize=10)

    # remove empty subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout()
    plt.show()