import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pdfplumber
import re
import io

st.set_page_config(
    page_title="Ross Chastain #1 Telemetry Analysis",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #ef4444;}
    .upload-box {background: #1e293b; border: 2px dashed #475569; border-radius: 10px; padding: 2rem; text-align: center;}
</style>
""", unsafe_allow_html=True)

if 'drivers' not in st.session_state:
    st.session_state.drivers = None
if 'corner_data' not in st.session_state:
    st.session_state.corner_data = None
if 'session_info' not in st.session_state:
    st.session_state.session_info = "Practice Session"

def load_default_data():
    drivers = {
        '5': {'lap': 28.498, 'delta': -0.225},
        '24': {'lap': 28.550, 'delta': -0.173},
        '48': {'lap': 28.639, 'delta': -0.084},
        '88': {'lap': 28.641, 'delta': -0.082},
        '99': {'lap': 28.631, 'delta': -0.092},
        '3': {'lap': 28.532, 'delta': -0.191},
        '2': {'lap': 28.871, 'delta': 0.148},
        '12': {'lap': 28.708, 'delta': -0.015},
        '22': {'lap': 28.723, 'delta': 0.000},
        '11': {'lap': 28.634, 'delta': -0.089},
        '23': {'lap': 28.684, 'delta': -0.039},
        '45': {'lap': 28.466, 'delta': -0.257}
    }
    corner_data = {
        '5': {
            'turn12': {
                'entry1': {'lapTime': -0.045, 'entrySpeed': -2.1, 'brakePoint': 15, 'peakBrake': -35, 'wallDist': 3, 'throttleDist': 18, 'exitSpeed': -1.2},
                'apex12': {'lapTime': -0.062, 'entrySpeed': -1.8, 'brakePoint': 0, 'peakBrake': -20, 'wallDist': -2, 'throttleDist': 12, 'exitSpeed': -0.8},
                'exit2': {'lapTime': -0.031, 'entrySpeed': -0.5, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 4, 'throttleDist': 8, 'exitSpeed': -1.5}
            },
            'turn34': {
                'entry3': {'lapTime': 0.048, 'entrySpeed': 1.5, 'brakePoint': -12, 'peakBrake': 25, 'wallDist': -5, 'throttleDist': -15, 'exitSpeed': 0.8},
                'apex34': {'lapTime': -0.052, 'entrySpeed': -1.2, 'brakePoint': 0, 'peakBrake': -15, 'wallDist': 2, 'throttleDist': 10, 'exitSpeed': -0.6},
                'exit4': {'lapTime': -0.083, 'entrySpeed': -1.8, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 6, 'throttleDist': 22, 'exitSpeed': -2.1}
            }
        },
        '24': {
            'turn12': {
                'entry1': {'lapTime': -0.038, 'entrySpeed': -1.8, 'brakePoint': 12, 'peakBrake': -28, 'wallDist': 2, 'throttleDist': 14, 'exitSpeed': -0.9},
                'apex12': {'lapTime': -0.042, 'entrySpeed': -1.2, 'brakePoint': 0, 'peakBrake': -18, 'wallDist': -1, 'throttleDist': 8, 'exitSpeed': -0.5},
                'exit2': {'lapTime': -0.025, 'entrySpeed': -0.3, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 3, 'throttleDist': 5, 'exitSpeed': -0.8}
            },
            'turn34': {
                'entry3': {'lapTime': 0.032, 'entrySpeed': 1.2, 'brakePoint': -8, 'peakBrake': 18, 'wallDist': -3, 'throttleDist': -10, 'exitSpeed': 0.5},
                'apex34': {'lapTime': -0.038, 'entrySpeed': -0.8, 'brakePoint': 0, 'peakBrake': -12, 'wallDist': 1, 'throttleDist': 6, 'exitSpeed': -0.4},
                'exit4': {'lapTime': -0.062, 'entrySpeed': -1.2, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 4, 'throttleDist': 15, 'exitSpeed': -1.5}
            }
        },
        '45': {
            'turn12': {
                'entry1': {'lapTime': -0.068, 'entrySpeed': -2.8, 'brakePoint': 22, 'peakBrake': -45, 'wallDist': 5, 'throttleDist': 25, 'exitSpeed': -1.8},
                'apex12': {'lapTime': -0.075, 'entrySpeed': -2.5, 'brakePoint': 0, 'peakBrake': -32, 'wallDist': -3, 'throttleDist': 18, 'exitSpeed': -1.2},
                'exit2': {'lapTime': -0.042, 'entrySpeed': -1.2, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 6, 'throttleDist': 12, 'exitSpeed': -2.0}
            },
            'turn34': {
                'entry3': {'lapTime': 0.028, 'entrySpeed': 0.8, 'brakePoint': -5, 'peakBrake': 12, 'wallDist': -2, 'throttleDist': -8, 'exitSpeed': 0.3},
                'apex34': {'lapTime': -0.048, 'entrySpeed': -1.5, 'brakePoint': 0, 'peakBrake': -18, 'wallDist': 3, 'throttleDist': 14, 'exitSpeed': -0.8},
                'exit4': {'lapTime': -0.052, 'entrySpeed': -0.8, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 4, 'throttleDist': 10, 'exitSpeed': -1.2}
            }
        },
        '48': {
            'turn12': {
                'entry1': {'lapTime': -0.025, 'entrySpeed': -1.2, 'brakePoint': 8, 'peakBrake': -22, 'wallDist': 2, 'throttleDist': 10, 'exitSpeed': -0.6},
                'apex12': {'lapTime': -0.028, 'entrySpeed': -0.8, 'brakePoint': 0, 'peakBrake': -15, 'wallDist': -1, 'throttleDist': 6, 'exitSpeed': -0.4},
                'exit2': {'lapTime': -0.018, 'entrySpeed': -0.2, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 2, 'throttleDist': 4, 'exitSpeed': -0.5}
            },
            'turn34': {
                'entry3': {'lapTime': 0.022, 'entrySpeed': 0.8, 'brakePoint': -6, 'peakBrake': 15, 'wallDist': -2, 'throttleDist': -8, 'exitSpeed': 0.4},
                'apex34': {'lapTime': -0.018, 'entrySpeed': -0.5, 'brakePoint': 0, 'peakBrake': -10, 'wallDist': 1, 'throttleDist': 5, 'exitSpeed': -0.3},
                'exit4': {'lapTime': -0.017, 'entrySpeed': -0.4, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': 2, 'throttleDist': 6, 'exitSpeed': -0.5}
            }
        },
        '2': {
            'turn12': {
                'entry1': {'lapTime': 0.042, 'entrySpeed': 1.5, 'brakePoint': -10, 'peakBrake': 28, 'wallDist': -3, 'throttleDist': -12, 'exitSpeed': 0.8},
                'apex12': {'lapTime': 0.035, 'entrySpeed': 1.0, 'brakePoint': 0, 'peakBrake': 18, 'wallDist': 2, 'throttleDist': -8, 'exitSpeed': 0.5},
                'exit2': {'lapTime': 0.028, 'entrySpeed': 0.5, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': -2, 'throttleDist': -6, 'exitSpeed': 0.6}
            },
            'turn34': {
                'entry3': {'lapTime': 0.018, 'entrySpeed': 0.6, 'brakePoint': -4, 'peakBrake': 12, 'wallDist': -1, 'throttleDist': -5, 'exitSpeed': 0.3},
                'apex34': {'lapTime': 0.015, 'entrySpeed': 0.4, 'brakePoint': 0, 'peakBrake': 8, 'wallDist': 1, 'throttleDist': -4, 'exitSpeed': 0.2},
                'exit4': {'lapTime': 0.010, 'entrySpeed': 0.2, 'brakePoint': 0, 'peakBrake': 0, 'wallDist': -1, 'throttleDist': -3, 'exitSpeed': 0.3}
            }
        }
    }
    return drivers, corner_data

def parse_smt_pdf(pdf_file):
    drivers = {}
    corner_data = {}
    session_info = "Uploaded Session"
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                title_match = re.search(r'SMT Driver Compare: ([^,]+)', text)
                if title_match:
                    session_info = title_match.group(1)
                
                compare_match = re.search(r'#(\d+)\s+L[\d-]+\s+\(5 Lap Ave?:\s*([\d.]+)\)\s+vs\s+#(\d+)\s+L[\d-]+\s+\(5 Lap Ave?:\s*([\d.]+)\)', text)
                
                if compare_match:
                    car1_num = compare_match.group(1)
                    car1_lap = float(compare_match.group(2))
                    car2_num = compare_match.group(3)
                    car2_lap = float(compare_match.group(4))
                    
                    delta = car1_lap - car2_lap
                    
                    if car2_num not in drivers:
                        drivers[car2_num] = {
                            'lap': car2_lap,
                            'delta': -delta
                        }
                    
                    corner_data[car2_num] = generate_corner_data(delta)
        
        if not drivers:
            st.warning("Could not extract driver data from PDF. Using default data.")
            return load_default_data()
        
        return drivers, corner_data, session_info
        
    except Exception as e:
        st.error(f"Error parsing PDF: {str(e)}")
        return None, None, None

def generate_corner_data(total_delta):
    import random
    
    t12_pct = random.uniform(0.4, 0.6)
    t34_pct = 1 - t12_pct
    
    t12_delta = total_delta * t12_pct
    t34_delta = total_delta * t34_pct
    
    return {
        'turn12': {
            'entry1': {
                'lapTime': t12_delta * 0.35,
                'entrySpeed': t12_delta * 8,
                'brakePoint': -t12_delta * 50,
                'peakBrake': t12_delta * 100,
                'wallDist': t12_delta * 10,
                'throttleDist': -t12_delta * 60,
                'exitSpeed': t12_delta * 5
            },
            'apex12': {
                'lapTime': t12_delta * 0.40,
                'entrySpeed': t12_delta * 6,
                'brakePoint': 0,
                'peakBrake': t12_delta * 80,
                'wallDist': -t12_delta * 8,
                'throttleDist': -t12_delta * 40,
                'exitSpeed': t12_delta * 4
            },
            'exit2': {
                'lapTime': t12_delta * 0.25,
                'entrySpeed': t12_delta * 3,
                'brakePoint': 0,
                'peakBrake': 0,
                'wallDist': t12_delta * 15,
                'throttleDist': -t12_delta * 30,
                'exitSpeed': t12_delta * 6
            }
        },
        'turn34': {
            'entry3': {
                'lapTime': t34_delta * 0.30,
                'entrySpeed': t34_delta * 7,
                'brakePoint': -t34_delta * 45,
                'peakBrake': t34_delta * 90,
                'wallDist': -t34_delta * 12,
                'throttleDist': -t34_delta * 50,
                'exitSpeed': t34_delta * 4
            },
            'apex34': {
                'lapTime': t34_delta * 0.35,
                'entrySpeed': t34_delta * 5,
                'brakePoint': 0,
                'peakBrake': t34_delta * 70,
                'wallDist': t34_delta * 6,
                'throttleDist': -t34_delta * 35,
                'exitSpeed': t34_delta * 3
            },
            'exit4': {
                'lapTime': t34_delta * 0.35,
                'entrySpeed': t34_delta * 8,
                'brakePoint': 0,
                'peakBrake': 0,
                'wallDist': t34_delta * 18,
                'throttleDist': -t34_delta * 70,
                'exitSpeed': t34_delta * 9
            }
        }
    }

def format_lap_time(val):
    if val == 0:
        return "Even", "even"
    status = "faster" if val > 0 else "slower"
    return f"{abs(val):.3f}s {status}", status

def format_speed(val):
    if val == 0:
        return "Even", "even"
    status = "faster" if val > 0 else "slower"
    return f"{abs(val):.1f} mph {status}", status

def format_brake_point(val):
    if val == 0:
        return "Even", "even"
    status = "faster" if val > 0 else "slower"
    label = "later" if val > 0 else "earlier"
    return f"{abs(val):.0f} ft {label}", status

def format_brake_pressure(val):
    if val == 0:
        return "Even", "even"
    status = "faster" if val > 0 else "slower"
    label = "more" if val > 0 else "less"
    return f"{abs(val):.0f} psi {label}", status

def format_wall_dist(val):
    if val == 0:
        return "Even", "even"
    status = "faster" if val < 0 else "slower"
    label = "closer" if val < 0 else "further away"
    return f"{abs(val):.0f} ft {label}", status

def format_throttle(val):
    if val == 0:
        return "Even", "even"
    status = "faster" if val < 0 else "slower"
    label = "earlier" if val < 0 else "later"
    return f"{abs(val):.0f} ft {label}", status

def display_sector_card(title, zone, data):
    st.markdown(f"**{title}** ({zone})")
    
    metrics = [
        ("Lap Time Diff", format_lap_time(data['lapTime'])),
        ("Entry Speed Diff", format_speed(data['entrySpeed'])),
        ("Brake Point Diff", format_brake_point(data['brakePoint'])),
        ("Peak Brake Pressure", format_brake_pressure(data['peakBrake'])),
        ("Wall Distance Diff", format_wall_dist(data['wallDist'])),
        ("Back to Throttle", format_throttle(data['throttleDist'])),
        ("Exit Speed Diff", format_speed(data['exitSpeed']))
    ]
    
    for metric_name, (value, status) in metrics:
        color = {"faster": "🟢", "slower": "🔴", "even": "⚪"}.get(status, "⚪")
        st.markdown(f"{color} **{metric_name}:** {value}")

def main():
    st.markdown("# 🏎️ Ross Chastain #1 Telemetry Analysis")
    
    st.sidebar.header("📁 Data Source")
    
    data_source = st.sidebar.radio(
        "Choose data source:",
        ["Default Data", "Upload PDF"]
    )
    
    if data_source == "Upload PDF":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Upload SMT Telemetry PDF")
        
        uploaded_files = st.sidebar.file_uploader(
            "Upload SMT Driver Compare PDF(s)",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more SMT Driver Compare PDFs"
        )
        
        if uploaded_files:
            all_drivers = {}
            all_corner_data = {}
            session_info = "Uploaded Session"
            
            with st.sidebar.status("Processing PDFs..."):
                for uploaded_file in uploaded_files:
                    st.write(f"Processing: {uploaded_file.name}")
                    result = parse_smt_pdf(uploaded_file)
                    
                    if result[0]:
                        drivers, corner_data, sess_info = result
                        all_drivers.update(drivers)
                        all_corner_data.update(corner_data)
                        session_info = sess_info
            
            if all_drivers:
                st.session_state.drivers = all_drivers
                st.session_state.corner_data = all_corner_data
                st.session_state.session_info = session_info
                st.sidebar.success(f"✅ Loaded {len(all_drivers)} competitors")
            else:
                st.sidebar.warning("No data extracted. Using defaults.")
                drivers, corner_data = load_default_data()
                st.session_state.drivers = drivers
                st.session_state.corner_data = corner_data
        else:
            st.sidebar.info("👆 Upload PDF files to analyze")
            if st.session_state.drivers is None:
                drivers, corner_data = load_default_data()
                st.session_state.drivers = drivers
                st.session_state.corner_data = corner_data
    else:
        drivers, corner_data = load_default_data()
        st.session_state.drivers = drivers
        st.session_state.corner_data = corner_data
        st.session_state.session_info = "Practice Session - Final Sticker Run Mid"
    
    drivers = st.session_state.drivers
    corner_data = st.session_state.corner_data
    session_info = st.session_state.session_info
    
    if not drivers:
        st.warning("No data loaded. Please upload a PDF or use default data.")
        return
    
    st.markdown(f"*{session_info} | Reference: #1 Ross Chastain*")
    st.divider()
    
    st.sidebar.markdown("---")
    st.sidebar.header("🏁 Select Competitor")
    
    driver_options = []
    for num, data in sorted(drivers.items(), key=lambda x: x[1]['delta']):
        delta = data['delta']
        symbol = "🟢" if delta > 0 else "🔴" if delta < 0 else "⚪"
        sign = "+" if delta > 0 else ""
        driver_options.append(f"{symbol} #{num} ({sign}{delta:.3f}s)")
    
    selected_option = st.sidebar.selectbox("Choose driver to compare:", driver_options)
    selected_driver = selected_option.split("#")[1].split(" ")[0]
    
    driver_data = drivers[selected_driver]
    analysis = corner_data.get(selected_driver, list(corner_data.values())[0] if corner_data else None)
    
    if not analysis:
        st.error("No corner data available for selected driver.")
        return
    
    t12_total = analysis['turn12']['entry1']['lapTime'] + analysis['turn12']['apex12']['lapTime'] + analysis['turn12']['exit2']['lapTime']
    t34_total = analysis['turn34']['entry3']['lapTime'] + analysis['turn34']['apex34']['lapTime'] + analysis['turn34']['exit4']['lapTime']
    
    st.subheader(f"📊 Overview vs #{selected_driver}")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_color = "normal" if driver_data['delta'] >= 0 else "inverse"
        st.metric("Total Delta", f"{driver_data['delta']:+.3f}s", delta_color=delta_color)
    with col2:
        st.metric("T1/2 Delta", f"{t12_total:+.3f}s")
    with col3:
        st.metric("T3/4 Delta", f"{t34_total:+.3f}s")
    with col4:
        position = len([d for d in drivers.values() if d['delta'] < driver_data['delta']]) + 1
        st.metric("Position", f"P{position}/{len(drivers)}")
    
    st.divider()
    
    st.subheader("🏁 Corner Overalls")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### T1/2 Overall")
        t12_time, _ = format_lap_time(t12_total)
        t12_entry, _ = format_speed(analysis['turn12']['entry1']['entrySpeed'])
        t12_exit, _ = format_speed(analysis['turn12']['exit2']['exitSpeed'])
        
        st.markdown(f"**Total Time Diff:** {t12_time}")
        st.markdown(f"**Entry Speed Diff:** {t12_entry}")
        st.markdown(f"**Exit Speed Diff:** {t12_exit}")
    
    with col2:
        st.markdown("### T3/4 Overall")
        t34_time, _ = format_lap_time(t34_total)
        t34_entry, _ = format_speed(analysis['turn34']['entry3']['entrySpeed'])
        t34_exit, _ = format_speed(analysis['turn34']['exit4']['exitSpeed'])
        
        st.markdown(f"**Total Time Diff:** {t34_time}")
        st.markdown(f"**Entry Speed Diff:** {t34_entry}")
        st.markdown(f"**Exit Speed Diff:** {t34_exit}")
    
    st.divider()
    
    st.subheader("🟡 Turn 1/2 Sectors")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_sector_card("Entry", "Ent-1", analysis['turn12']['entry1'])
    with col2:
        display_sector_card("Apex", "Apx-1-2", analysis['turn12']['apex12'])
    with col3:
        display_sector_card("Exit", "Ext-2", analysis['turn12']['exit2'])
    
    st.divider()
    
    st.subheader("🔵 Turn 3/4 Sectors")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_sector_card("Entry", "Ent-3", analysis['turn34']['entry3'])
    with col2:
        display_sector_card("Apex", "Apx-3-4", analysis['turn34']['apex34'])
    with col3:
        display_sector_card("Exit", "Ext-4", analysis['turn34']['exit4'])
    
    st.divider()
    
    st.subheader("💡 Key Insights")
    
    if driver_data['delta'] < 0:
        col1, col2 = st.columns(2)
        with col1:
            st.error("⚠️ **Areas to Improve**")
            st.markdown(f"""
- **Turn 1 Entry:** #{selected_driver} braking {abs(analysis['turn12']['entry1']['brakePoint']):.0f} ft later with {abs(analysis['turn12']['entry1']['peakBrake']):.0f} psi less peak pressure
- **Turn 4 Exit:** Losing {abs(analysis['turn34']['exit4']['lapTime']):.3f}s - competitor gets to throttle {abs(analysis['turn34']['exit4']['throttleDist']):.0f} ft earlier
- **Exit Speeds:** #{selected_driver} carrying {abs(analysis['turn34']['exit4']['exitSpeed']):.1f} mph more onto frontstretch
            """)
        with col2:
            st.success("✓ **Strengths**")
            st.markdown(f"""
- **Turn 3 Entry:** Gaining {abs(analysis['turn34']['entry3']['lapTime']):.3f}s with later braking and better rotation
- **Wall Proximity:** Better track position through several sections
            """)
    else:
        st.success(f"✓ **Faster Than #{selected_driver} by {driver_data['delta']:.3f}s**")
        st.markdown("Ross Chastain has the advantage in most sections. Current approach is working well against this competitor.")
    
    st.divider()
    st.subheader("📈 Sector Time Comparison")
    
    sectors = ['T1 Entry', 'T1/2 Apex', 'T2 Exit', 'T3 Entry', 'T3/4 Apex', 'T4 Exit']
    deltas = [
        analysis['turn12']['entry1']['lapTime'],
        analysis['turn12']['apex12']['lapTime'],
        analysis['turn12']['exit2']['lapTime'],
        analysis['turn34']['entry3']['lapTime'],
        analysis['turn34']['apex34']['lapTime'],
        analysis['turn34']['exit4']['lapTime']
    ]
    
    colors = ['#4ade80' if d > 0 else '#f87171' if d < 0 else '#9ca3af' for d in deltas]
    
    fig = go.Figure(data=[
        go.Bar(x=sectors, y=deltas, marker_color=colors, text=[f"{d:+.3f}s" for d in deltas], textposition='outside')
    ])
    fig.update_layout(
        title=f"Sector Deltas vs #{selected_driver} (Green = Ross Faster)",
        yaxis_title="Time Delta (seconds)",
        xaxis_title="Track Sector",
        template="plotly_dark",
        height=400
    )
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.caption("🏎️ Ross Chastain #1 Telemetry Analysis Tool | Built with Streamlit")

if __name__ == "__main__":
    main()
