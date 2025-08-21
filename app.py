# ------------------ CHARTS SIDE BY SIDE ------------------
st.subheader("📈 Open Interest Overview")

col_left, col_right = st.columns([1, 2])  # Wider space for line chart

# 📊 Bar Chart: CALL vs PUT OI Change
with col_left:
    total_ce_chg = df_chg["CE_ChgOI"].sum() / 100000
    total_pe_chg = df_chg["PE_ChgOI"].sum() / 100000

    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=["CALL"], y=[total_ce_chg], name="CALL", marker_color="green"))
    bar_fig.add_trace(go.Bar(x=["PUT"], y=[total_pe_chg], name="PUT", marker_color="red"))
    bar_fig.update_layout(
        template="plotly_dark",
        title="Change in OI (in Lakhs)",
        yaxis_title="OI Change (L)",
        xaxis_title="Option Type",
        height=400,
        margin=dict(l=30, r=30, t=40, b=30)
    )
    st.plotly_chart(bar_fig, use_container_width=True)

# 📈 Line Chart: CE/PE/Futures Trend
with col_right:
    max_oi = max(df_chg["CE_ChgOI"].max(), df_chg["PE_ChgOI"].max()) if not df_chg.empty else 1
    fut_price = spot_price

    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=df_chg["Strike"], y=df_chg["CE_ChgOI"],
        mode="lines+markers", name="CE", line=dict(color="green")
    ))
    line_fig.add_trace(go.Scatter(
        x=df_chg["Strike"], y=df_chg["PE_ChgOI"],
        mode="lines+markers", name="PE", line=dict(color="red")
    ))
    line_fig.add_trace(go.Scatter(
        x=df_chg["Strike"], y=[fut_price]*len(df_chg),
        mode="lines", name="Future", line=dict(color="gray", dash="dot"),
        yaxis="y2"
    ))

    line_fig.update_layout(
        template="plotly_dark",
        title="Change in OI vs Strike",
        xaxis_title="Strike Price",
        yaxis=dict(title="OI Change", side="left"),
        yaxis2=dict(
            title="Future Price",
            overlaying="y",
            side="right",
            range=[fut_price - 50, fut_price + 50],
            showgrid=False
        ),
        shapes=[dict(
            type="line",
            x0=spot_price, x1=spot_price,
            y0=0, y1=max_oi,
            line=dict(color="yellow", dash="dash")
        )],
        annotations=[dict(
            x=spot_price, y=max_oi * 0.1,
            text=f"Spot @ {spot_price:.2f}",
            showarrow=False,
            font=dict(color="yellow"),
            xanchor="left"
        )],
        legend=dict(x=0.01, y=0.99),
        height=500,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(line_fig, use_container_width=True)
