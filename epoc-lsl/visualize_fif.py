import mne
import matplotlib.pyplot as plt
import sys
import os

# Check if a file path was provided as an argument
if len(sys.argv) > 1:
    fif_file = sys.argv[1]
else:
    # List all .fif files in the current directory
    fif_files = [f for f in os.listdir('.') if f.endswith('_raw.fif')]
    
    if not fif_files:
        print("No FIF files found in the current directory.")
        sys.exit(1)
    
    # Use the most recent file if multiple exist
    fif_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    fif_file = fif_files[0]
    print(f"Using most recent file: {fif_file}")

# Load the FIF file
print(f"Loading {fif_file}...")
raw = mne.io.read_raw_fif(fif_file, preload=True)

# Create a figure with multiple visualizations
plt.figure(figsize=(15, 10))

# Plot 1: Power Spectral Density (frequency content)
plt.subplot(2, 1, 1)
raw.plot_psd(fmax=50, show=False)
plt.title('Power Spectral Density')

# Plot 2: Channel locations (topographic view)
plt.subplot(2, 1, 2)
try:
    raw.plot_sensors(show_names=True, show=False)
    plt.title('Channel Locations')
except Exception as e:
    plt.text(0.5, 0.5, f"Could not plot channel locations:\n{str(e)}", 
             ha='center', va='center', wrap=True)

plt.tight_layout()
plt.suptitle(f"EEG Data Visualization: {os.path.basename(fif_file)}", fontsize=16)
plt.subplots_adjust(top=0.9)

# Save the visualization
output_file = f"{os.path.splitext(fif_file)[0]}_viz.png"
plt.savefig(output_file, dpi=300)
print(f"Visualization saved to {output_file}")

# Show the plots
plt.show()

# For raw time series, use a separate figure (this can't be embedded in the same figure easily)
print("Opening raw time series in a new window...")
raw.plot(n_channels=14, scalings='auto')