"""
XDS Report Module.

This module provides a comprehensive set of functions for processing XDS data, visualising diffraction patterns,
and analyzing crystallographic information derived from XDS output files. It includes utilities for generating
rotation matrices, computing distances to planes, parsing `XDS.INP` files, creating interactive 3D scatter plots,
and generating HTML reports summarizing the analysis and visualisations.

Typical usage example:
    # Visualise lattice from an XDS directory
    visualise_lattice("/path/to/xds_directory")

    # Generate an HTML report for XDS data
    create_html_file("/path/to/report_directory", mode="single")

Attributes:
    html_head (str): HTML header for the report, containing styles and external script references.

Functions:
    rotation_matrix(axis: np.ndarray, theta: float) -> np.ndarray:
        Computes the rotation matrix for a specified axis and angle.

    distance_to_plane(points: np.ndarray, vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
        Calculates the perpendicular distance of each point to a plane defined by two vectors.

    parse_xds_inp(fn: str) -> tuple:
        Parses the `XDS.INP` file to extract essential crystallographic parameters.

    process_data(xds_dir: str, root: Tk) -> None:
        Processes XDS data for visualisation by extracting and rotating reflection coordinates.

    plot_data(X_rot: np.ndarray, Y_rot: np.ndarray, Z_rot: np.ndarray, ...) -> None:
        Generates a 3D scatter plot of rotated reflection coordinates with interactive controls.

    set_view_direction(ax: plt.Axes, a_star: np.ndarray) -> None:
        Adjusts the view direction of the 3D plot to align with a specified reciprocal lattice vector.

    visualise_lattice(xds_dir: str) -> None:
        Initiates the lattice visualisation process by setting up the GUI and processing data.

    create_html_file(report_path: str, mode: str) -> str:
        Generates an HTML report summarizing the XDS analysis and visualisations.

    open_html_file(path: str, mode: str, open: bool) -> None:
        Opens the generated HTML report in the default web browser.

Dependencies:
    - Standard libraries: os, subprocess, threading, webbrowser, tkinter, matplotlib, numpy, pandas, scipy
    - Third-party libraries: mpld3, plotly
    - Custom modules:
        - util: linux_to_windows_path, is_wsl, unit_cell_with_esd
        - xds_analysis: load_spot_binned, analysis_idxref_lp, etc.
        - xds_cluster: parse_xscale_lp, calculate_dendrogram
        - xds_input: extract_keywords

Credits:
    - Date: 2024-12-15
    - Authors: Developed by Yinlin Chen
    - License: BSD 3-clause

"""

import os
import subprocess
import threading
import webbrowser

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.cluster.hierarchy import dendrogram

from ..util import linux_to_windows_path, is_wsl, unit_cell_with_esd
from ..xds_analysis import load_spot_binned, load_mosaicity_list, load_divergence_list, load_scale_list, \
    extract_run_result, extract_cluster_result
from ..xds_cluster import parse_xscale_lp, calculate_dendrogram

html_head = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1" charset="UTF-8"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css"/>
    <style type="text/css">
        body {
            margin: 0;
            min-width: 240px;
            font-family: 'Arial', sans-serif;
            background-color: #f8f9fa;
            color: #495057;
        }
        .container-fluid {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin: 40px auto;
            max-width: 80%;
        }
        .page-header {
            margin-top: 0;
            padding-bottom: 20px;
            border-bottom: 2px solid #004085;
        }
        h1 {
            font-size: 2.5em;
            margin: 0;
            color: #004085;
        }
        h2 {
            font-size: 2em;
            margin-top: 40px;
            margin-bottom: 20px;
            color: #004085;
        }
        h5 {
            margin-left: 20px;
            margin-right: 20px;
        }
        .panel {
            margin-top: 20px;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
        }
        .panel-heading {
            padding: 10px 15px;
            border-bottom: 1px solid #dee2e6;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            background-color: #f5f5f5;
            cursor: pointer;
        }
        .panel-heading h3 {
            margin: 0;
            font-size: 1.25em;
        }
        .panel-body {
            padding: 15px;
        }
        .table-responsive {
            margin-top: 20px;
            overflow-x: auto;
        }
        table {
            table-layout: auto;
            margin-bottom: 20px;
            border-collapse: collapse;
            width: auto;
            max-width: 100%;
            border: 1px solid #dee2e6;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
            font-size: 0.95em;
        }
        th {
            background-color: #f2f2f2;
            color: #343a40;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:nth-child(odd) {
            background-color: #ffffff;
        }
        tr:hover {
            background-color: #e9ecef;
        }
        .plot-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
        }
        .plot {
            width: 48%;
            margin-bottom: 10px;
        }
        .plot_one_line {
            width: 78%;
            margin-bottom: 30px;
        }
    </style>
</head>\n"""


def create_plotly_figure_cc12(df):
    """Creates a Plotly figure for CC<sub>1/2</sub> vs. resolution.

    Args:
        df (pd.DataFrame): DataFrame containing CC<sub>1/2</sub> and resolution data.

    Returns:
        str: HTML string of the Plotly figure.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["high_res"],
        y=df["CC1/2"],
        mode='lines',
        name='CC<sub>1/2</sub>',
        hovertemplate='%{y}',
        line=dict(color='rgb(34, 193, 195)')
    ))
    fig.add_trace(go.Scatter(
        x=df["high_res"],
        y=df["CC_crit"],
        mode='lines',
        name='CC<sub>1/2</sub> crit. (p=0.5%)',
        hovertemplate='%{y}',
        line=dict(color='rgb(34, 193, 195)', dash='dot')
    ))
    fig.update_layout(
        title='CC<sub>1/2</sub> vs resolution',
        xaxis=dict(title='Resolution (Å)', type='log', gridcolor='lightgrey', showline=True, linewidth=2,
                   linecolor='black', autorange='reversed'),
        yaxis=dict(range=[0, 100], title='CC<sub>1/2</sub>', gridcolor='lightgrey'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        spikedistance=-1,
        hovermode='x'
    )
    fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_plotly_figure_R(df):
    """Creates a Plotly figure for R-values vs. resolution.

    Args:
        df (pd.DataFrame): DataFrame containing R<sub>meas</sub>, R<sub>int</sub>, and resolution data.

    Returns:
        str: HTML string of the Plotly figure.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["high_res"],
        y=df["R_meas"],
        mode='lines+markers',
        name='R<sub>meas</sub>',
        hovertemplate='%{y}',
        line=dict(color='rgb(102, 194, 165)')
    ))
    fig.add_trace(go.Scatter(
        x=df["high_res"],
        y=df["R_int"],
        mode='lines+markers',
        name='R<sub>int</sub>',
        hovertemplate='%{y}',
        line=dict(color='rgb(102, 194, 165)', dash='dot')
    ))
    fig.update_layout(
        title='R value vs Resolution',
        xaxis=dict(title='Resolution (Å)', type='log', gridcolor='lightgrey', showline=True, linewidth=2,
                   linecolor='black', autorange='reversed'),
        yaxis=dict(range=[-20, 200], title='R-value (%)', gridcolor='lightgrey'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        spikedistance=-1,
        hovermode='x',
        legend=dict(x=0, y=1, xanchor='left', yanchor='top'),
        margin=dict(r=20, l=20)
    )
    fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_plotly_figure_reso(plot_type, df):
    """Creates a Plotly figure for resolution-based metrics.

    Args:
        plot_type (str): Type of resolution plot. Options:
            - "isa" for I/Sigma.
            - "completeness" for completeness.
            - "multiplicity" for multiplicity.
        df (pd.DataFrame): DataFrame containing the relevant data for plotting.

    Returns:
        str: HTML string of the Plotly figure.

    Raises:
        ValueError: If an invalid `plot_type` is provided.
    """
    if plot_type == 'isa':
        x_data = df["high_res"]
        y_data = df["Isa_meas"]
        title = 'I/Sigma vs Resolution'
        yaxis_title = 'I/σ'
        line_color = 'rgb(141, 160, 203)'
    elif plot_type == 'completeness':
        x_data = df["high_res"]
        y_data = df["completeness"]
        title = 'Completeness vs Resolution'
        yaxis_title = 'Completeness (%)'
        line_color = 'rgb(231, 138, 195)'
    elif plot_type == 'multiplicity':
        x_data = df["high_res"]
        y_data = df["multiplicity"]
        title = 'Multiplicity vs Resolution'
        yaxis_title = 'Multiplicity'
        line_color = 'rgb(166, 216, 84)'
    else:
        raise ValueError("Invalid plot type. Must be 'isa', 'completeness', or 'multiplicity'.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines+markers',
        name=plot_type.capitalize(),
        hovertemplate='%{y}',
        line=dict(color=line_color)
    ))
    fig.update_layout(
        title=title,
        xaxis=dict(
            title='Resolution (Å)', type='log', gridcolor='lightgrey', showline=True,
            linewidth=2, linecolor='black', autorange='reversed'
        ),
        yaxis=dict(title=yaxis_title, gridcolor='lightgrey'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        spikedistance=-1,
        hovermode='x',
        margin=dict(r=20, l=20)
    )
    fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', showline=True)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_plotly_spot(spot_xds):
    """Creates a Plotly figure for spots vs. frames from the `SPOT.XDS` file.

    Args:
        spot_xds (str): Path to the `SPOT.XDS` file.

    Returns:
        str: HTML string of the Plotly figure.
    """

    spot_pd = load_spot_binned(spot_xds)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spot_pd["rebinned_frame"],
        y=spot_pd["count"],
        mode='lines',
        name='Spot',
        hovertemplate='%{y}',
        line=dict(color='rgb(55, 126, 184)', shape='hv')
    ))
    fig.add_trace(go.Scatter(
        x=spot_pd["rebinned_frame"],
        y=spot_pd["unindexed_count"],
        mode='lines',
        name='Unindexed Spot',
        hovertemplate='%{y}',
        line=dict(color='red', dash='dot', shape='hv')
    ))
    fig.update_layout(
        title='Spots vs Frames',
        xaxis=dict(title='Frames', gridcolor='lightgrey', showline=True, linewidth=2, linecolor='black'),
        yaxis=dict(title='No. of Spots', gridcolor='lightgrey'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        spikedistance=-1,
        hovermode='x',
        legend=dict(x=1, y=1, xanchor='right', yanchor='top'),
        margin=dict(r=20, l=20)
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_plotly_figure_frame(integrate_lp, plot_type):
    """Creates a Plotly figure for frame-specific statistics.

    Args:
        integrate_lp (str): Path to the `INTEGRATE.LP` file.
        plot_type (str): Type of frame plot. Options:
            - "scale" for scale factor vs. frames.
            - "divergence" for divergence vs. frames.
            - "mosaicity" for mosaicity vs. frames.

    Returns:
        str: HTML string of the Plotly figure.

    Raises:
        ValueError: If an invalid `plot_type` is provided.
    """
    with open(integrate_lp, 'r') as f:
        lines = f.readlines()
    if plot_type == 'scale':
        data = load_scale_list(lines)
        title = 'Scale vs Frames'
        yaxis_title = 'Scale'
        line_color = 'rgb(77, 175, 74)'
    elif plot_type == 'divergence':
        data = load_divergence_list(lines)
        title = 'Divergence vs Frames'
        yaxis_title = 'Divergence'
        line_color = 'rgb(152, 78, 163)'
    elif plot_type == 'mosaicity':
        data = load_mosaicity_list(lines)
        title = 'Mosaicity vs Frames'
        yaxis_title = 'Mosaicity'
        line_color = 'rgb(255, 127, 0)'
    else:
        raise ValueError("Invalid plot type. Must be 'scale', 'divergence', or 'mosaicity'.")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(data.keys()),
        y=list(data.values()),
        mode='lines',
        name=plot_type.capitalize(),
        hovertemplate='%{y}',
        line=dict(color=line_color, shape='hv')
    ))
    fig.update_layout(
        title=title,
        xaxis=dict(title='Frames', gridcolor='lightgrey', showline=True, linewidth=2, linecolor='black'),
        yaxis=dict(title=yaxis_title, gridcolor='lightgrey'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        spikedistance=-1,
        hovermode='x',
        margin=dict(r=20, l=20)
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_html_plot_sec1(dir_path, mode="single"):
    """Generates the first section of the HTML report containing resolution-based statistics plots.

    Args:
        dir_path (str): Directory containing the XDS files.
        mode (str, optional): Mode of the report. Options are:
            - "single" for single datasets.
            - "cluster" for cluster datasets.
            Defaults to "single".

    Returns:
        str: HTML string for the first plot section.
    """
    if mode == "single":
        df = pd.DataFrame(extract_run_result(dir_path)["slice_report"])
    elif mode == "cluster":
        df = pd.DataFrame(extract_cluster_result(dir_path)["slice_report"])
    else:
        return
    html_plot1 = f"""
    <h2>Plot</h2>
    <div class="panel">
        <div class="panel-heading" data-toggle="collapse" data-target="#plot_reso">
            <h3>Statistics over Resolution</h3>
        </div>
        <div id="plot_reso" class="panel-collapse collapse in">
            <div class="panel-body">
                <div class="plot-container">
                    <div class="plot_one_line">{create_plotly_figure_cc12(df)}</div>
                </div>
                <div class="plot-container">
                    <div class="plot">{create_plotly_figure_R(df)}</div>
                    <div class="plot">{create_plotly_figure_reso('isa', df)}</div>
                </div>
                <div class="plot-container">
                    <div class="plot">{create_plotly_figure_reso('completeness', df)}</div>
                    <div class="plot">{create_plotly_figure_reso('multiplicity', df)}</div>
                </div>
            </div>
        </div>
    </div>"""
    return html_plot1


def create_html_plot_sec2_single(dir_path):
    """Generates the second section of the HTML report for single mode, including frame-based statistics plots.

    Args:
        dir_path (str): Directory containing the XDS files.

    Returns:
        str: HTML string for the second plot section.
    """
    integrate_lp = os.path.join(dir_path, "INTEGRATE.LP")
    spot_xds = os.path.join(dir_path, "SPOT.XDS")
    html_plot2 = f"""
    <div class="panel">
        <div class="panel-heading" data-toggle="collapse" data-target="#plot_frame">
            <h3>Statistics over Frames</h3>
        </div>
        <div id="plot_frame" class="panel-collapse collapse in">
            <div class="panel-body">
                <div class="plot-container">
                    <div class="plot">{create_plotly_spot(spot_xds)}</div>
                    <div class="plot">{create_plotly_figure_frame(integrate_lp, "scale")}</div>
                </div>
                <div class="plot-container">
                    <div class="plot">{create_plotly_figure_frame(integrate_lp, "divergence")}</div>
                    <div class="plot">{create_plotly_figure_frame(integrate_lp, "mosaicity")}</div>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
</html>\n"""
    return html_plot2


def metadata_to_table(st, line):
    """Converts metadata into table format for inclusion in the HTML report.

    Args:
        st (dict): Dictionary containing metadata.
        line (int): Line number or identifier for the metadata entry.

    Returns:
        tuple: A tuple containing:
            - metadata (dict): Metadata formatted for the table.
            - overall (dict): Overall statistics formatted for the table.
            - raw_data (dict): Dictionary containing raw data paths.
    """
    try:
        output_cell = unit_cell_with_esd(st.get("unit_cell"), st.get("unit_cell_esd"))
        metadata = {
            "Data": f"data{line}",
            "#Frame": st.get("frames"),
            "Step (°)": round(st.get("step"), 3),
            "Start (°)": round(st.get("start_angle"), 2),
            "End (°)": round(st.get("end_angle"), 2),
            "Rot.(°)": round(np.degrees(np.arctan2(st.get("rotation_axis")[1],
                                                   st.get("rotation_axis")[0])), 1),
            "WL (Å)": st.get("wavelength"),
            "Camera_l (mm)": st.get("camera_length"),
            "Size1": st.get("input").get("NX")[0],
            "Size2": st.get("input").get("NY")[0],
            "Pixel Size (1/mm)": "{:.3f}".format(
                st.get("pixel_size") / st.get("camera_length") * 10 ** 4 / st.get("wavelength"))
        }
    except TypeError:
        output_cell = unit_cell_with_esd(st.get("unit_cell"), st.get("unit_cell_esd"))
        metadata = None

    overall = {
        "Data": f"data{line}",
        'Reso. Range': "{:.2f}–{:.2f}".format(st.get("max_res", 99), st.get("resolution")),
        "SG": "{} ({})".format(
            st.get("space_group_name").replace("(", "<sub>").replace(")", "</sub>"),
            st.get("space_group_number"))
        if "space_group_name" in st else st.get("space_group_number"),
        "a (Å)": output_cell[0],
        "b (Å)": output_cell[1],
        "c (Å)": output_cell[2],
        "α (°)": output_cell[3],
        "β (°)": output_cell[4],
        "γ (°)": output_cell[5],
        '#Refls': st.get("refls_reso") if "refls_reso" in st else st.get("N_obs"),
        '#Uniq.': st.get("uniq_reso") if "uniq_reso" in st else st.get("N_uni"),
        'Reso.': st.get("resolution"),
        'Comp.': st.get("completeness"),
        'ISa': st.get("ISa_model"),
        'R<sub>meas</sub>': st.get("rmeas") if "rmeas" in st else st.get("R_meas"),
        'CC<sub>1/2</sub>': st.get("cc12_reso") if "cc12_reso" in st else st.get("CC1/2"),
    }
    return metadata, overall, {"Data": f"data{line}", "Path": st.get("xds_dir")}


def create_html_table(dir_path, mode="single"):
    """Creates HTML tables summarizing metadata, overall statistics, and raw data paths.

    Args:
        dir_path (str): Directory containing the XDS files.
        mode (str, optional): Mode of the report. Options are:
            - "single" for single datasets.
            - "cluster" for cluster datasets.
            Defaults to "single".

    Returns:
        str: HTML string containing all the generated tables.
    """
    if mode == "single":
        result_dict = extract_run_result(dir_path)
        sta_list = [result_dict]
    elif mode == "cluster":
        result_dict = extract_cluster_result(dir_path, output=True)
        sta_list = list(result_dict['input_statistics'].values()) + [result_dict]
    else:
        return None
    raw_list = []
    metadata_list = []
    overall_list = []
    for i, statistics in enumerate(sta_list):
        metadata, overall, xds_dir = metadata_to_table(statistics, i + 1)
        if metadata:
            metadata_list.append(metadata)
        overall_list.append(overall)
        raw_list.append(xds_dir)
    if len(sta_list) > 1:
        overall_list[-1]["Data"] = "Merged"
        overall_list[-1]["ISa"] = "N/A"
        blank_line = {
            "Data": " ", 'Reso. Range': " ", "SG": " ", "a (Å)": "", "b (Å)": "", "c (Å)": "",
            "α (°)": "", "β (°)": "", "γ (°)": "", '#Refls': "", '#Uniq.': "", 'Reso.': "",
            'Comp.': "", 'ISa': "", 'R<sub>meas</sub>': "", 'CC<sub>1/2</sub>': "", }
        overall_list.insert(-1, blank_line)

    else:
        overall_list[0]["Reso. Range"] = ("{:.2f}–{:.2f}".format(result_dict["max_res"], result_dict["min_res"])
                                          if "max_res" in result_dict else "N/A")
    table_html1 = pd.DataFrame(metadata_list).to_html(header=True, index=False, escape=False)
    table_html2 = pd.DataFrame(overall_list).to_html(header=True, index=False, escape=False)
    table_html4 = pd.DataFrame(
        raw_list if len(raw_list) == 1 else raw_list[:-1]
    ).to_html(header=True, index=False, escape=False)

    slice_report = pd.DataFrame(result_dict["slice_report"])
    slice_report.insert(0, 'Resolution', slice_report.apply(
        lambda row: f"{row['low_res']}–{row['high_res']}", axis=1))
    slice_report.rename(columns={'completeness': 'Comp.', 'multiplicity': 'Multi.', 'Isa_meas': 'I/Sigma'},
                        inplace=True)

    # Merge CC1/2 and CC_crit into CC_half and drop the original columns
    slice_report['CC_half'] = slice_report.apply(
        lambda row: f"{row['CC1/2']}*" if row['CC1/2'] > row['CC_crit'] else f"{row['CC1/2']}", axis=1)
    slice_report.drop(columns=['low_res', 'high_res', 'CC1/2', 'CC_crit'], inplace=True)

    # Add new rows
    new_row = {
        'Resolution': 'Inf–{}'.format(result_dict['resolution']) + ("*" if "merge_resolution" in result_dict else ""),
        'N_obs': result_dict['refls_reso'],
        'N_uni': result_dict['uniq_reso'],
        'ideal_N': result_dict['ideal_reso'],
        'Comp.': '{}'.format(result_dict['completeness']) + ("*" if "merge_resolution" in result_dict else ""),
        'Multi.': result_dict['multi_reso'],
        'I/Sigma': result_dict['isa'],
        'R_int': result_dict['rint'],
        'R_meas': result_dict['rmeas'],
        'R_exp': result_dict['rexp'],
        'CC_half': '{}{}'.format(
            result_dict['cc12_reso'], "*" if result_dict['cc12_reso'] > result_dict['cc12_crit'] else ""),
    }

    new_row_empty = {col: ' ' for col in slice_report.columns}
    slice_report.loc[len(slice_report)] = new_row_empty
    slice_report.loc[len(slice_report)] = new_row

    if "merge_resolution" in result_dict:
        complete_string = (f"* The completeness is calculated with "
                           f"resolution cut-off of {result_dict['merge_resolution']} Å.")
    else:
        complete_string = ''

    table_html3 = slice_report.to_html(header=True, index=False, justify='center')

    html_table = f"""
    <body>
    <div class="container-fluid">
        <div class="page-header"><h1>Data Reduction Report</h1></div>
        <h4>This report is for {mode} data in the directory {dir_path}.</h4>
        <h2>Table</h2>
        <div class="panel">
            <div class="panel-heading" data-toggle="collapse" data-target="#metadata"><h3>Metadata</h3></div>
            <div id="metadata" class="panel-collapse collapse in">
                <div class="panel-body"><div class="table-responsive">{table_html1}</div></div>
                <h5>  * The abbreviate parameters used in the metadata table are #Frame = number of frames, 
                Rot. =  the angle between the projection of rotation axis on the detector, 
                WL = wavelength, Camera_l = camera length, Size1/2 = number of pixels on x/y axis, 
                Pixel Size = pixel size in the reciprocal space.</h5>
            </div>
        </div>
        <div class="panel">
            <div class="panel-heading" data-toggle="collapse" data-target="#overall"><h3>Overall Statistics</h3></div>
            <div id="overall" class="panel-collapse collapse in">
                <div class="panel-body"><div class="table-responsive">{table_html2}</div></div>
                <h5>  * The abbreviate parameters used in the metadata table are 
                Reso. Range = the lowest and the highest resolution of raw / merged data, 
                SG =  space group, #Refls = number of reflections in the resolution range,	
                #Uniq. = number of unique reflections in the resolution range, 
                Comp. = Completeness with resolution cut-off, 
                Reso. = suggested resolution cut-off, ISa = Model ISa value reported by XDS.</h5>
            </div>
        </div>
        <div class="panel">
            <div class="panel-heading" data-toggle="collapse" data-target="#resolution"><h3>Resolution Shells</h3></div>
            <div id="resolution" class="panel-collapse collapse in">
                <div class="panel-body"><div class="table-responsive">{table_html3}</div></div>
                <h5>  {complete_string} </h5>
            </div>
        </div>
        <div class="panel">
            <div class="panel-heading" data-toggle="collapse" data-target="#rawdata"><h3>Rawdata Path List</h3></div>
            <div id="rawdata" class="panel-collapse collapse out">
                <div class="panel-body"><div class="table-responsive">{table_html4}</div></div>
            </div>
        </div>\n"""
    return html_table


def create_html_plot_sec2_cluster(dir_path):
    """Generates the second section of the HTML report for cluster mode, including dendrogram plots.

    Args:
        dir_path (str): Directory containing the XDS files.

    Returns:
        str: HTML string for the second plot section.
    """
    xscale_lp_path = os.path.join(dir_path, "XSCALE.LP")
    if os.path.exists(xscale_lp_path):
        ccs = parse_xscale_lp(xscale_lp_path)
        if not ccs:
            print("No correlation coefficients found in XSCALE.LP.")
            return
        z = calculate_dendrogram(ccs)

        fig = go.Figure()

        # Convert the linkage matrix to a dendrogram format using scipy's dendrogram function
        dendrogram_data = dendrogram(z, no_plot=True)

        # Extract the dendrogram data
        icoord = dendrogram_data['icoord']
        dcoord = dendrogram_data['dcoord']
        color_list = dendrogram_data['color_list']

        # Plot each line segment of the dendrogram
        for i, d, c in zip(icoord, dcoord, color_list):
            # Convert the coordinates to plotly format
            x = [val / 10 for val in i]  # Scaling to make it look better
            y = d

            # Add each dendrogram segment as a line
            fig.add_trace(go.Scatter(
                x=x, y=y,
                mode='lines',
                line=dict(color='rgb(31, 119, 180)', width=2),
                hoverinfo='none'
            ))

        # Configure the layout
        fig.update_layout(
            title={
                'text': 'Dendrogram of Correlation Coefficients',
                'font': {'family': 'Arial', 'size': 24, 'color': '#2c3e50'},
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title={'text': 'Samples', 'font': {'family': 'Arial', 'size': 18, 'color': '#34495e'}},
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                autorange=False,
                range=[-0.5, max([max(x) for x, y, c in zip(icoord, dcoord, color_list)]) / 10 + 0.5],
                showline=True,
                linewidth=2,
                linecolor='#bdc3c7'
            ),
            yaxis=dict(
                title={'text': 'Distance', 'font': {'family': 'Arial', 'size': 18, 'color': '#34495e'}},
                gridcolor='#ecf0f1',
                showline=True,
                linewidth=2,
                linecolor='#bdc3c7',
                range=[0, max([max(y) for x, y, c in zip(icoord, dcoord, color_list)]) * 1.1],
                tickfont={'family': 'Arial', 'size': 14}
            ),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            showlegend=False,
            width=950,
            height=550,
            margin=dict(l=60, r=60, t=100, b=60),
            shapes=[{
                'type': 'rect',
                'xref': 'paper',
                'yref': 'paper',
                'x0': 0,
                'y0': 0,
                'x1': 1,
                'y1': 1,
                'line': {'width': 2, 'color': '#e0e6ed'}
            }],
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        # Update the existing traces with better hover templates and styling
        for i, trace in enumerate(fig.data):
            fig.data[i].update(
                line=dict(color='#3498db', width=2.5),
                hoverinfo='text',
                hovertext='Dendrogram branch'
            )

        html_plot2 = """
        <div class="panel">
            <div class="panel-heading" data-toggle="collapse" data-target="#plot_cluster">
                <h3>Statistics over Clusters</h3>
            </div>
            <div id="plot_cluster" class="panel-collapse collapse in">
                <div class="plot-container">
                    <div class="plot_one_line">{}</div>
                </div>
            </div>
        </div>
    </div>
    </body>
    </html>""".format(fig.to_html(full_html=False, include_plotlyjs='cdn'))

        return html_plot2

    else:
        print(f"File {xscale_lp_path} does not exist.")
        return None


def create_html_file(report_path, mode="single"):
    """Generates an HTML report summarizing the XDS analysis and visualisations.

    Args:
        report_path (str): Directory where the report will be saved.
        mode (str, optional): Mode of the report. Options are:
            - "single" for single datasets.
            - "cluster" for cluster datasets.
            Defaults to "single".

    Returns:
        str: Path to the created HTML file.

    Raises:
        Exception: If an error occurs during HTML file creation.
    """
    print("Creating HTML file ... ... ... ", end="", flush=True)
    html_table = create_html_table(report_path, mode)
    html_plot1 = create_html_plot_sec1(report_path, mode)
    if mode == "single":
        html_plot2 = create_html_plot_sec2_single(report_path)
    elif mode == "cluster":
        html_plot2 = create_html_plot_sec2_cluster(report_path)
    else:
        return None
    html_file = os.path.join(report_path, 'autolei_report.html')
    with open(html_file, 'w') as file:
        file.write(html_head + html_table + html_plot1 + html_plot2)
    print("\rCreating HTML file ... ... ... OK\n")
    return html_file


def open_html_file(path, mode="single", open_html=True):
    """Opens the generated HTML report in the default web browser.

    Args:
        path (str): Directory containing the XDS files.
        mode (str, optional): Mode of the report. Options are:
            - "single" for single datasets.
            - "cluster" for cluster datasets.
            Defaults to "single".
        open_html (bool, optional): Whether to automatically open the report in the browser. Defaults to True.
    """
    if mode == "single":
        if not os.path.exists(os.path.join(path, 'XDS_ASCII.HKL')):
            print("XDS_ASCII.HKL file not found. You may need to run XDS first.")
            return
        file_path = create_html_file(path, mode="single")
    elif mode == "cluster":
        if not os.path.exists(os.path.join(path, 'all.HKL')):
            print("all.HKL file not found. You may need to run XSCALE first.")
            return
        file_path = create_html_file(path, mode="cluster")
    else:
        return None
    file_url = f'file://{file_path}'

    def open_file_in_windows(wsl_path):
        # Convert WSL path to Windows path
        windows_path = linux_to_windows_path(wsl_path)
        command = f'powershell.exe Start-Process "{windows_path}"'
        subprocess.run(command, shell=True)

    def open_url(url):
        webbrowser.open(url)

    if open_html:
        if is_wsl():
            thread = threading.Thread(target=open_file_in_windows, args=(file_path,))
        else:
            thread = threading.Thread(target=open_url, args=(file_url,))
        thread.start()
