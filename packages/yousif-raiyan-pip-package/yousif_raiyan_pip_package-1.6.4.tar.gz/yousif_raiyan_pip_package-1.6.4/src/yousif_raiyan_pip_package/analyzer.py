import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft

class Analyzer:
    def __init__(self, loader, trigger_detector, target_length=50):
        """
        Initializes the Analyzer with instances of EDFLoader and TriggerDetector.

        :param loader: EDFLoader, the loader instance containing paths and signal data.
        :param trigger_detector: TriggerDetector, the instance containing trigger detection data.
        :param target_length: int, the fixed number of time bins to resample each FFT result to.
        """
        self.loader = loader
        self.trigger_detector = trigger_detector
        self.df_triggers = trigger_detector.df_triggers  # DataFrame with 'start_index' and 'end_index'
        self.channels = ['Fp1', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 
                         'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'Fz']
        self.bands = {
            "Delta": (0.5, 4),
            "Theta": (4, 8),
            "Alpha": (8, 12),
            "Beta": (12, 30),
            "Gamma": (30, 100)
        }
        self.target_length = target_length

    def _resample_array(self, arr, target_length):
        """
        Resamples a 1D array to a fixed target length using linear interpolation.

        :param arr: numpy.ndarray, the array to resample.
        :param target_length: int, the desired length.
        :return: numpy.ndarray, the resampled array.
        """
        old_indices = np.linspace(0, len(arr) - 1, num=len(arr))
        new_indices = np.linspace(0, len(arr) - 1, num=target_length)
        return np.interp(new_indices, old_indices, arr)

    def plot_signal_window(self, window_index, lead):
        """
        Plots the raw signal segment between consecutive triggers for a specified lead.

        :param window_index: int, index of the window to plot 
                             (window is defined between trigger[window_index]'s end and trigger[window_index+1]'s start)
        :param lead: str, the channel/lead name to plot (e.g., 'T6')
        """
        try:
            if window_index >= len(self.df_triggers) - 1:
                raise ValueError("window_index out of range. A subsequent trigger is needed to define a window.")
            start_index = int(self.df_triggers.iloc[window_index]['end_index'])
            end_index = int(self.df_triggers.iloc[window_index + 1]['start_index'])
            signal_data = self.loader.signals_dict[lead]['data']

            plt.figure(figsize=(10, 4))
            plt.plot(signal_data[start_index:end_index])
            plt.title(f'Signal Window from index {start_index} to {end_index} for lead {lead}')
            plt.xlabel('Sample Index')
            plt.ylabel('Amplitude')
            plt.show()

        except Exception as e:
            print(f"Error plotting window {window_index} for lead {lead}: {e}")

    def plot_average_window(self, channel, start_window=None, end_window=None,
                            target_length=500, aggregation_method='mean', trim_ratio=0.1):
        """
        Computes and plots the aggregated raw signal window (time-domain) for a specified channel 
        over a given range of trigger-defined windows. Each window is resampled to target_length
        before aggregation. Available aggregation methods: 'mean', 'median', or 'trimmed'.
        
        :param channel: str, channel/lead name (e.g., 'T6')
        :param start_window: int, starting window index (default is 0)
        :param end_window: int, ending window index (default is the last available window)
        :param target_length: int, the number of points to resample each window to
        :param aggregation_method: str, method to aggregate windows: 'mean', 'median', or 'trimmed'
        :param trim_ratio: float, the proportion to trim from each end when using trimmed mean
        """
        if start_window is None:
            start_window = 0
        if end_window is None:
            end_window = len(self.df_triggers) - 1  # because windows are defined between triggers
        
        signal_data = self.loader.signals_dict[channel]['data']
        windows = []
        for i in range(start_window, end_window):
            start_idx = int(self.df_triggers.iloc[i]['end_index'])
            end_idx = int(self.df_triggers.iloc[i + 1]['start_index'])
            if end_idx <= start_idx:
                continue
            segment = signal_data[start_idx:end_idx]
            # Resample the segment so all windows have the same length
            resampled_segment = self._resample_array(segment, target_length)
            windows.append(resampled_segment)
        
        if not windows:
            print("No valid windows found for the specified indices.")
            return
        
        windows_stack = np.stack(windows)
        
        # Choose aggregation method
        if aggregation_method == 'mean':
            agg_window = np.mean(windows_stack, axis=0)
        elif aggregation_method == 'median':
            agg_window = np.median(windows_stack, axis=0)
        elif aggregation_method == 'trimmed':
            from scipy.stats import trim_mean
            agg_window = np.array([trim_mean(windows_stack[:, i], trim_ratio) for i in range(windows_stack.shape[1])])
        else:
            raise ValueError("Invalid aggregation_method. Choose 'mean', 'median', or 'trimmed'.")

        plt.figure(figsize=(10, 4))
        plt.plot(agg_window)
        plt.title(f'Aggregated Raw Signal Window for channel {channel}\n'
                  f'Windows {start_window} to {end_window} using {aggregation_method} aggregation')
        plt.xlabel('Resampled Time Index')
        plt.ylabel('Amplitude')
        plt.show()

    def __get_fft_values(self, data, sample_rate, window_sec=2, overlap_sec=1):
        """
        Computes the Short Time Fourier Transform (STFT) of the input data and sums FFT values
        within predefined frequency bands.

        :param data: numpy.ndarray, the input signal segment.
        :param sample_rate: float, sampling rate of the signal.
        :param window_sec: float, window duration (seconds) for the STFT.
        :param overlap_sec: float, overlap duration (seconds) between windows.
        :return: dict, keys are band names and values are summed FFT values over time.
        """
        nperseg = int(sample_rate * window_sec)
        noverlap = int(sample_rate * overlap_sec)

        f, t, Zxx = stft(data, fs=sample_rate, nperseg=nperseg, noverlap=noverlap)
        band_values = {}
        for band, (lowcut, highcut) in self.bands.items():
            freq_indices = np.where((f >= lowcut) & (f <= highcut))[0]
            filtered_data = np.abs(Zxx[freq_indices, :]).sum(axis=0)
            band_values[band] = filtered_data
        return band_values

    def extract_signals(self):
        """
        Processes signal segments defined by consecutive triggers for each channel.
        For each frequency band, computes the STFT on each segment, resamples the result to a fixed length,
        and then aggregates the results using the median across segments. Each channel's median FFT data is saved
        to its own CSV file and plotted separately. The CSV files and plots for each band are organized into separate directories.
        """
        # Loop over each channel
        for channel in self.channels:
            signal_data = self.loader.signals_dict[channel]['data']
            sample_rate = self.loader.signals_dict[channel]['sample_rate']
            # Loop over each band
            for band in self.bands:
                all_windows = []
                for i in range(len(self.df_triggers) - 1):
                    start = int(self.df_triggers.iloc[i]['end_index'])
                    end = int(self.df_triggers.iloc[i + 1]['start_index'])
                    # Skip segments shorter than 2 seconds
                    if end - start < sample_rate * 2:
                        continue

                    fft_dict = self.__get_fft_values(signal_data[start:end], sample_rate)
                    band_values = fft_dict.get(band)
                    if band_values is not None:
                        # Resample band_values to a fixed target length
                        resampled_values = self._resample_array(band_values, self.target_length)
                        all_windows.append(resampled_values)

                if all_windows:
                    stacked_windows = np.stack(all_windows)
                    # Aggregate using median
                    channel_band_median = np.median(stacked_windows, axis=0)
                    
                    # Create a directory for the band if it doesn't exist
                    band_dir = os.path.join(self.loader.folder_path, self.loader.name, band)
                    os.makedirs(band_dir, exist_ok=True)
                    
                    # Create subdirectories for CSV and plots
                    csv_dir = os.path.join(band_dir, "csv")
                    plot_dir = os.path.join(band_dir, "plots")
                    os.makedirs(csv_dir, exist_ok=True)
                    os.makedirs(plot_dir, exist_ok=True)
                    
                    # Save to CSV for this channel and band in the CSV directory
                    csv_output_path = os.path.join(csv_dir, f'{channel}_{band}_fft_median.csv')
                    df = pd.DataFrame({f"{channel}_{band}_fft_median": channel_band_median})
                    df.to_csv(csv_output_path, index=False)
                    print(f"Saved FFT medians for channel {channel} in band {band} to {csv_output_path}.")

                    # Plot for this channel and band and save in the plot directory
                    plt.figure(figsize=(10, 6))
                    plt.plot(channel_band_median, label=f'{channel} {band} median')
                    plt.xlabel('Time Steps')
                    plt.ylabel('FFT Amplitude')
                    plt.title(f'Median FFT Values for {channel} in {band} Band')
                    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
                    plt.tight_layout()
                    plot_output_path = os.path.join(plot_dir, f'{channel}_{band}_fft_median.png')
                    plt.savefig(plot_output_path)
                    plt.show()
                else:
                    print(f"No valid windows for channel {channel} in band {band}.")