from eradication_data_requirements.fit_ramsey_time_series import (
    add_slopes_to_effort_capture_data,
    add_probs_to_effort_capture_data,
)
from eradication_data_requirements.plot_progress_probability import plot_progress_probability
from eradication_data_requirements.plot_cpue_series import (
    calculate_cpue_and_cumulative_by_season,
    calculate_cpue_and_cumulative_by_flight,
    plot_cumulative_series_cpue,
)
from eradication_data_requirements.set_data import select_december_of_every_year

import pandas as pd
import typer
import matplotlib.pyplot as plt

app = typer.Typer()


@app.command()
def write_progress_probability_figure(
    data_path: str = typer.Option("", help="Input file path"),
    figure_path: str = typer.Option("", help="Output file path"),
):
    monthly_progress_probability = pd.read_csv(data_path)
    plot_progress_probability(monthly_progress_probability)
    plt.savefig(figure_path)


@app.command()
def write_effort_and_captures_with_probability(
    input_path: str = typer.Option(help="Input file path"),
    bootstrapping_number: int = typer.Option(help="Bootstrapping number"),
    output_path: str = typer.Option(help="Output file path"),
    window_length: int = typer.Option(help="Window length for removal rate"),
):
    effort_capture_data = pd.read_csv(input_path)
    effort_captures_with_slopes = add_probs_to_effort_capture_data(
        effort_capture_data, bootstrapping_number, window_length
    )
    yearly_results = select_december_of_every_year(effort_captures_with_slopes)
    yearly_results.to_csv(output_path, index=False)


@app.command()
def write_effort_and_captures_with_slopes(
    input_path: str = typer.Option("", help="Input file path"),
    output_path: str = typer.Option("", help="Output file path"),
):
    effort_capture_data = pd.read_csv(input_path)
    effort_captures_with_slopes = add_slopes_to_effort_capture_data(effort_capture_data)
    effort_captures_with_slopes.to_csv(output_path, index=False)


@app.command()
def plot_cumulative_series_cpue_by_season(
    effort_capture_path: str = typer.Option("", help="Input file path"),
    output_png: str = typer.Option("", help="Output file path"),
    fontsize: int = typer.Option(27, help="Font size of axis"),
):
    effort_capture_df = pd.read_csv(effort_capture_path)
    data_year = calculate_cpue_and_cumulative_by_season(effort_capture_df)
    plot_cumulative_series_cpue(fontsize, data_year)
    plt.savefig(output_png, dpi=300, transparent=True)


@app.command()
def plot_cumulative_series_cpue_by_flight(
    effort_capture_path: str = typer.Option("", help="Input file path"),
    output_png: str = typer.Option("", help="Output file path"),
    fontsize: int = typer.Option(27, help="Font size of axis"),
):
    effort_capture_df = pd.read_csv(effort_capture_path)
    data_year = calculate_cpue_and_cumulative_by_flight(effort_capture_df)
    plot_cumulative_series_cpue(fontsize, data_year)
    plt.savefig(output_png, dpi=300, transparent=True)
