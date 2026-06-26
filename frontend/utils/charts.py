import plotly.graph_objects as go
from typing import List, Dict, Any

def sentiment_bar_chart(positive: int, negative: int, neutral: int) -> go.Figure:
    """
    Renders horizontal sentiment count breakdown bar chart.
    """
    fig = go.Figure(go.Bar(
        x=[positive, negative, neutral],
        y=["Positive", "Negative", "Neutral"],
        orientation='h',
        marker_color=["#22c55e", "#ef4444", "#6b7280"]
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(showgrid=False)
    )
    return fig

def activity_line_chart(dates: List[str], counts: List[int]) -> go.Figure:
    """
    Renders 7-day user activity line chart with markers.
    """
    fig = go.Figure(go.Scatter(
        x=dates,
        y=counts,
        mode="lines+markers",
        line=dict(color="#6366f1", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(99, 102, 241, 0.1)"
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    )
    return fig

def model_scores_chart(model_scores: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders model breakdown performance probabilities.
    """
    names = [m["model_name"].upper() for m in model_scores]
    confs = [m["confidence"] for m in model_scores]
    colors = []
    for m in model_scores:
        s = m["sentiment"].lower()
        if s == "positive":
            colors.append("#22c55e")
        elif s == "negative":
            colors.append("#ef4444")
        else:
            colors.append("#6b7280")
            
    fig = go.Figure(go.Bar(
        x=confs,
        y=names,
        orientation='h',
        marker_color=colors,
        text=[f"{c*100:.1f}%" for c in confs],
        textposition="inside"
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=240,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0.0, 1.05], showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(showgrid=False)
    )
    return fig

def confidence_gauge(confidence: float, sentiment: str) -> go.Figure:
    """
    Renders speed gauge indicators for confidence ratings.
    """
    color = "#6b7280"
    if sentiment.lower() == "positive":
        color = "#22c55e"
    elif sentiment.lower() == "negative":
        color = "#ef4444"
        
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence,
        number={"valueformat": ".1%"},
        gauge={
            "axis": {"range": [0, 1], "tickwidth": 1, "tickcolor": "gray"},
            "bar": {"color": color},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "gray"
        }
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=180,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig
