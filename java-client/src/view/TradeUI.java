package view;

import java.awt.Color;
import javax.swing.*;
import javax.swing.border.EmptyBorder;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.DefaultCategoryDataset;

import javax.swing.table.DefaultTableCellRenderer;

public class TradeUI extends JFrame {
    private static final long serialVersionUID = 1L;
    public JFreeChart mChart;
    public DefaultCategoryDataset mDataset;
    public CategoryPlot mPlot;
    public ChartPanel mChartPanel;
    public JButton start, stop, complete, backMain;
    public JTable market, orders, position;
    public JLabel MarketInfo, TradeHistory, Position;
    public Object[][] marketContent, ordersContent, positionContent;
    public String[] marketTitle = new String[]{"CODE", "PRICE", "BUY", "SELL", "VOLUME"};
    public boolean[] marketColumnEditables = new boolean[]{false, false, false, false, false, false};
    public String[] ordersTitle = new String[]{"CODE", "DATETIME", "VOLUME", "DIRECTION", "PRICE"};
    public boolean[] ordersColumnEditables = new boolean[]{false, false, false, false, false};
    public String[] positionTitle = new String[]{"CODE", "VOLUME"};
    public boolean[] positionColumnEditables = new boolean[]{false, false};

    /**
     * Create the frame.
     */
    public TradeUI() {
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setExtendedState(JFrame.MAXIMIZED_BOTH);
        setBounds(100, 100, 1920, 1080);
        JPanel contentPane = new JPanel();
        contentPane.setBorder(new EmptyBorder(5, 5, 5, 5));
        setContentPane(contentPane);
        contentPane.setLayout(null);

        mChart = ChartFactory.createLineChart(
                "",
                "",
                "",
                mDataset, PlotOrientation.VERTICAL,
                true, false, false
        );
        mPlot = (CategoryPlot) mChart.getPlot();
        mPlot.setBackgroundPaint(Color.LIGHT_GRAY);
        mPlot.setRangeGridlinePaint(Color.BLUE);
        mPlot.setOutlinePaint(Color.RED);
        contentPane.setLayout(null);

        mChartPanel = new ChartPanel(mChart);
        mChartPanel.setMouseZoomable(false);
        mChartPanel.setMouseWheelEnabled(true);
        mChartPanel.setLocation(10, 10);
        mChartPanel.setSize(1280, 660);
        contentPane.add(mChartPanel);
        mChartPanel.setLayout(null);

        JScrollPane MarketScrollPane = new JScrollPane();
        MarketScrollPane.setBounds(1300, 35, 600, 1000);
        contentPane.add(MarketScrollPane);

        market = new JTable();
        market.setEnabled(false);
        MarketScrollPane.setViewportView(market);
        DefaultTableCellRenderer cr = new DefaultTableCellRenderer();
        cr.setHorizontalAlignment(SwingConstants.CENTER);
        market.setDefaultRenderer(Object.class, cr);

        JScrollPane HistoryScrollPane = new JScrollPane();
        HistoryScrollPane.setBounds(10, 700, 880, 260);
        contentPane.add(HistoryScrollPane);

        orders = new JTable();
        HistoryScrollPane.setViewportView(orders);

        JScrollPane PositionScrollPane = new JScrollPane();
        PositionScrollPane.setBounds(900, 700, 380, 260);
        contentPane.add(PositionScrollPane);

        position = new JTable();
        PositionScrollPane.setViewportView(position);

        start = new JButton("\u5F00\u59CB\u4EA4\u6613");
        start.setBounds(700, 1000, 100, 23);
        contentPane.add(start);

        stop = new JButton("\u505C\u6B62\u4EA4\u6613");
        stop.setEnabled(false);
        stop.setBounds(840, 1000, 100, 23);
        contentPane.add(stop);

        complete = new JButton("\u5B8C\u6210\u4EA4\u6613");
        complete.setBounds(980, 1000, 100, 23);
        contentPane.add(complete);

        backMain = new JButton("\u8FD4\u56DE\u4E3B\u754C\u9762");
        backMain.setBounds(1120, 1000, 100, 23);
        contentPane.add(backMain);

        Position = new JLabel("Position");
        Position.setBounds(900, 680, 200, 15);
        contentPane.add(Position);

        MarketInfo = new JLabel("Market Info");
        MarketInfo.setBounds(1300, 10, 200, 15);
        contentPane.add(MarketInfo);

        TradeHistory = new JLabel("Trading History");
        TradeHistory.setBounds(10, 680, 200, 15);
        contentPane.add(TradeHistory);
    }
}
